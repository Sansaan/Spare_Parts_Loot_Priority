# Spare Parts Loot Priority

**\*\*\* Intended for use by the Spare Parts guild on Westfall \*\*\***

This addon will display the loot priority (if any) by class and spec on the item’s tooltip.

Currently included raids:
* Mount Hyjal
* Black Temple

---

The addon data is read from [loot_table.lua](loot_table.lua).

This LUA file is generated using [data_management/csv_to_lua.py](csv_to_lua.py) and uses a CSV named [data_management/loot_table.csv](loot_table.csv).

The CSV file contains one line per item with the following format "id,name,prio,zone,boss,note".
"prio" is a list of classes/specs separated by " > " which will get turned into newlines in the item tooltip. If you want a ">" to be printed in the tooltip, eg "MS>OS", ensure that there is no leading or trailing space.
"zone", "boss", and "note" are not currently used by the addon.
