#!/usr/bin/python

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

from sys import exit
import os
from urllib.parse import quote_plus
import argparse
import pandas as pd

input_file = 'loot_table.csv'
lua_file = 'loot_table.lua'
new_csv_file = 'new.'+input_file

# parse args
parser = argparse.ArgumentParser(description='Create an update LUA loot table from a CSV.')

parser.add_argument('-i', '--input',
                    metavar='filename',
                    action='append',
                    help='CSV file containing loot priorities')

parser.add_argument('-o', '--output',
                    metavar='filename',
                    action='append',
                    help='LUA file to be used for the addon. Addon expects filename to be "'+lua_file+'"')

args = parser.parse_args()

if isinstance(args.input, list):
    input_file = args.input[0]
    if len(args.input) > 1:
        parser.error("only open input file (-i) is supported.")

    if os.path.splitext(input_file)[1] != '.csv':
        lua_file = input_file+'.lua'
        new_csv_file = 'new.'+input_file+'.csv'
    else:
        lua_file = os.path.splitext(input_file)[0]+'.lua'
        new_csv_file = 'new.'+input_file

if isinstance(args.output, list):
    lua_file = args.output[0]
    if len(args.output) > 1:
        parser.error("only open output file (-o) is supported.")

loot = pd.read_csv(input_file)

if loot['id'].isna().any():

    print('\nMissing ID(s) found. Attempting to correct...\n')

    # from https://github.com/nexus-devs/wow-classic-items/tree/master/data/json
    database = pd.read_json('data.json')
    database.set_index('itemId',inplace=True)

    for ind in loot.index:
        name = loot['name'][ind]
        id = loot['id'][ind]

        if pd.isna(id) or id == 0:
            itemId = database.index[database['name'].str.lower() == name.lower()].tolist()

            if len(itemId) > 1:
                print('    More than one itemId found for "'+name+'" in the supplied data file. Please investigate.')
            elif len(itemId) == 0:
                print('    Unable to locate "'+name+'" in the supplied data file. Please investigate. https://tbc.wowhead.com/search?q='+(quote_plus(name)))
            else:
                print('    Updating "'+name+'" with an ID of "'+str(itemId[0])+'"')
                loot.loc[ind,'name'] = database.at[itemId[0],'name']
                loot.loc[ind,'id'] = itemId[0]
        else:
            pass

    if loot['id'].isna().any():
        print('\nERROR: Unable to autocorrect missing IDs. Please review output and manually correct.')
        exit()

    loot['id'] = loot['id'].astype(int)

    print('\nUpdated CSV saved to new.loot_table.csv')
    loot.to_csv(new_csv_file,index=False)    

with open(lua_file, 'w') as output_file:
    print('spare_parts_loot_table = {', file=output_file)

    for index,item in loot.iterrows():

        loot_id = str(item['id'])
        loot_name = str(item['name'])
        prio = str(item['prio'])
        loot_zone = str(item['zone'])
        loot_bosses = str(item['boss'])

        print ('    {["loot_id"] = "'+loot_id+
        '",["loot_name"] = "'+loot_name+
        '",["prio"] = "'+prio+
        '",["loot_zone"] = "'+loot_zone+
        '",["loot_bosses"] = "'+loot_bosses+
        '",},', file=output_file)

    print('}', file=output_file)