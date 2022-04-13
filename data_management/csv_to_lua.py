#!/usr/bin/python

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import pandas as pd

loot = pd.read_csv("loot_table.csv")

print('spare_parts_loot_table = {')

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
    '",},')

print('}')
