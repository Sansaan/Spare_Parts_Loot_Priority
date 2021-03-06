Spare_Parts_Loot_Priority = {}

function Spare_Parts_Loot_Priority.ItemSearch(itemname)
    for index, value in next, spare_parts_loot_table do
        if value["loot_id"] == itemname then
            return value["prio"]
        end
    end
end

local split = function (str, pat, limit)
  --https://stackoverflow.com/users/2150472/benjamin-vison
  --https://stackoverflow.com/a/60172017
  local t = {}
  local fpat = "(.-)" .. pat
  local last_end = 1
  local s, e, cap = str:find(fpat, 1)
  while s do
    if s ~= 1 or cap ~= "" then
      table.insert(t, cap)
    end

    last_end = e+1
    s, e, cap = str:find(fpat, last_end)

    if limit ~= nil and limit <= #t then
      break
    end
  end

  if last_end <= #str then
    cap = str:sub(last_end)
    table.insert(t, cap)
  end

  return t
end

function Spare_Parts_Loot_Priority.MakeTooltip(tooltip, ...)
  local itemname, itemlink = tooltip:GetItem()

  if itemlink then
    local priority = Spare_Parts_Loot_Priority.ItemSearch(itemlink:match("item:(%d+):"))

    local color_dots = "47faf6"
    local color_title = "fa83f5"
    local color_prio = "ffa60c"

    if priority then
      local headfoot = string.format("|c00"..color_dots.."*****************************")
      local spacer = string.format("|c00"..color_dots.."*")
      local title = string.format("|c00"..color_dots.."*|c00"..color_title.."  Spare Parts Loot Priority:")
      tooltip:AddLine(headfoot)
      tooltip:AddLine(title)

      local priolist = split(priority, " > ")
      for i,prio in ipairs(priolist) do
        tooltip:AddLine(string.format("|c00"..color_dots.."*|c00"..color_prio.."      %s", prio))
      end

      tooltip:AddLine(spacer)
      tooltip:AddLine(headfoot)
    end
  end
end

-- hover tooltip
GameTooltip:HookScript("OnTooltipSetItem", Spare_Parts_Loot_Priority.MakeTooltip)

-- link click tooltip
ItemRefTooltip:HookScript("OnTooltipSetItem", Spare_Parts_Loot_Priority.MakeTooltip)
