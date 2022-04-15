import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

from flask import Flask, url_for, request, redirect, render_template, Markup, flash # type: ignore

import pandas as pd
import datetime as dt
import base64
import os
from io import StringIO

from dotenv import load_dotenv # type: ignore
load_dotenv()

persistent_data = True
title = 'Spare Parts Loot Council Distribution Report'

ALLOWED_EXTENSIONS = {'txt', 'csv'}

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'for dev use only, please change')

def encode_from_df(df):
    return str(base64.b64encode(df.to_json().encode('utf-8')))[2:-1]

def decode_to_df(message):
    return pd.read_json(base64.b64decode(request.form[message]).decode('utf-8'))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def cleanup(df):
    df.rename(columns={
        'player' : 'Player',
        'date' : 'Date',
        'item' : 'Item',
        'response' : 'Response'
    }, inplace=True)
    df['Date'] = df['Date'].apply(pd.to_datetime)
    df['Item'] = df['Item'].str.replace(r'^\[|\]$','')
    df['Player'] = df['Player'].str.replace(r'-Westfall$','')

    df['Response'] = df['Response'].str.replace(r'Mainspec','Main Spec')
    df['Response'] = df['Response'].str.replace(r'Offspec/Greed','Off Spec')
    df['Response'] = df['Response'].str.replace(r'Candidate didn\'t respond on time','No Response')
    df['Response'] = df['Response'].str.replace(r'Candidate is not in the instance','No Response')
    df['Response'] = df['Response'].str.replace(r'Awarded','No Response')

    df.drop(df.index[df['Item'] == 'Heart of Darkness'], inplace=True)
    df.drop(df.index[df['Response'] == 'Disenchant'], inplace=True)
    df.drop(df.index[df['Response'] == 'Banking'], inplace=True)

    roles = pd.read_csv(os.path.join(app.root_path, 'rolemap.csv'))
    roles.set_index('player', inplace=True)

    df['Role'] = df['Player'].map(roles.to_dict()['role'])

    return df

@app.route('/')
def index():
    return render_template('index.html', title=title, next='parse')

@app.route('/unknown')
@app.route('/error')
def unknown():
    return render_template('error.html', title=title)

@app.route('/parse', methods=['GET', 'POST'])
def parse():
    if request.method == 'GET' and not persistent_data:
        return redirect(url_for('index'))
    
    output = ''
    if request.form['csv_string'] != '' and request.files['csv_file'].filename != '':
        flash('ERROR! Please do not attempt to paste CSV data and upload a file at the same time.','error')
        return redirect(url_for('index'))

    elif request.form['csv_string'] == '' and request.files['csv_file'].filename == '':
        flash('ERROR! Please provide the CSV string OR upload a file.','error')
        return redirect(url_for('index'))

    elif request.form['csv_string'] != '':
        csv = StringIO(request.form['csv_string'])

    elif request.files['csv_file'].filename != '':
        if allowed_file(request.files['csv_file'].filename):
            csv = request.files['csv_file']
        else:
            flash('ERROR! That filetype is not allow. Please only use CSV or TXT files.','error')
            return redirect(url_for('index'))

    else:
        flash('ERROR! There should be no way at all to get here. Please let San know what you were trying to do.','error')
        return redirect(url_for('unknown'))

    try:
        loot = cleanup(pd.read_csv(csv, encoding = "ISO-8859-1")).sort_values('Date')
    except:
        flash('ERROR! Unable to parse the supplied data. Is it valid CSV exported from RCLC?','error')
        return redirect(url_for('index'))

    no_roles = loot.loc[(loot['Role'].isna())]['Player'].unique()
    for player in no_roles:
        flash('WARNING! '+player+' does not have a role (Tank/Healer/DPS) defined. Please have San correct this before proceeding.','error')

    output += 'Please scan over the imported table for any glaring issues and let San know if you see something wrong.<br/>'
    if not len(no_roles):
        output += '''<br/>
  <form action="'''+url_for('report')+'''" method="POST">
    <input type="hidden" name="loot_csv" value="'''+encode_from_df(loot)+'''" />
    <input type="submit" value="View Report"/>
  </form>'''

    loot['Role'] = loot['Role'].fillna('<span style="font-weight:bold;color:#f00;">No Role Defined</span>')
 
    output += loot.to_html(columns=['Player','Role','Date','Item','Response'], index=False, escape=False)
    return render_template('parse.html', title=title, content=Markup(output))

@app.route('/report', methods=['GET', 'POST'])
def report():
    if request.method == 'GET' and not persistent_data:
        return redirect(url_for('index'))

    loot = decode_to_df('loot_csv')

    character_search = ''
    item_search = ''
    role_search = ''

    end_date = loot['Date'].max().date()
    start_date = end_date - dt.timedelta(days=28)
    start_date = loot['Date'].min().date()

    characters = loot.loc[
        (loot['Player'].str.contains(character_search, case=False)) &
        (loot['Item'].str.contains(item_search, case=False)) &
        (loot['Role'].str.contains(role_search, case=False)) &
        ((loot['Date'].dt.date >= start_date) & (loot['Date'].dt.date <= end_date)) &
        (True)]['Player'].unique()

    character_count=len(characters)

    roles = loot.loc[
        (loot['Player'].str.contains(character_search, case=False)) &
        (loot['Item'].str.contains(item_search, case=False)) &
        (loot['Role'].str.contains(role_search, case=False)) &
        ((loot['Date'].dt.date >= start_date) & (loot['Date'].dt.date <= end_date))
        ]['Role'].unique()
    
    role_count = {}
    for role in roles:
        members = loot.loc[
            (loot['Player'].str.contains(character_search, case=False)) & 
            (loot['Item'].str.contains(item_search, case=False)) &
            (loot['Role'].str.contains(role_search, case=False)) &
            ((loot['Date'].dt.date >= start_date) & (loot['Date'].dt.date <= end_date)) &
            (loot['Role'] == role) &
            (True)]['Player'].unique()
        role_count[role] = len(members)

    character_role_count = {}
    character_loot = {}

    for toon in sorted(characters):
        character_role_count[toon] = {}
        character_loot[toon] = {}

        distributions = loot.loc[
            (loot['Player'] == toon) &
            (loot['Item'].str.contains(item_search, case=False)) &
            ((loot['Date'].dt.date >= start_date) & (loot['Date'].dt.date <= end_date)) &
            (loot['Role'].str.contains(role_search, case=False)) &
            (True)].sort_values(by='Date')

        character_role_count[toon]['Total'] = len(distributions)
        character_role_count[toon]['Main Spec'] = len(loot.loc[
            (loot['Player'] == toon) & (loot['Response'] == 'Main Spec') &
            (loot['Item'].str.contains(item_search, case=False)) &
            ((loot['Date'].dt.date >= start_date) & (loot['Date'].dt.date <= end_date)) &
            (loot['Role'].str.contains(role_search, case=False)) &
            (True)])
        character_role_count[toon]['Upgrade'] = len(loot.loc[
            (loot['Player'] == toon) & (loot['Response'] == 'Upgrade') &
            (loot['Item'].str.contains(item_search, case=False)) &
            ((loot['Date'].dt.date >= start_date) & (loot['Date'].dt.date <= end_date)) &
            (loot['Role'].str.contains(role_search, case=False)) &
            (True)])
        character_role_count[toon]['Off Spec'] = len(loot.loc[
            (loot['Player'] == toon) & (loot['Response'] == 'Off Spec') &
            (loot['Item'].str.contains(item_search, case=False)) &
            ((loot['Date'].dt.date >= start_date) & (loot['Date'].dt.date <= end_date)) &
            (loot['Role'].str.contains(role_search, case=False)) &
            (True)])

        character_loot[toon] = []
        for dist in distributions.index:
            item = distributions['Item'][dist]
            date = distributions['Date'][dist]
            response = distributions['Response'][dist]

            character_loot[toon].append(item+", "+str(date.date())+", "+response)
            
    return render_template('report.html',
        title=title,
        start_date=start_date, end_date=end_date,
        character_count=character_count,
        role_count=role_count,
        character_role_count=character_role_count,
        character_loot=character_loot
        )

if __name__ == '__main__':
	app.run(debug=False)

