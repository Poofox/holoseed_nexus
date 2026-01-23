-- AdaptiveMenus Log Viewer v0.1
-- Quick viewer to see what's been logged

local resource_path = reaper.GetResourcePath()
local log_path = resource_path .. "/Scripts/AdaptiveMenus/adaptive_menus_log.json"

-- Read and parse log
local function read_log()
  local file = io.open(log_path, "r")
  if not file then 
    reaper.ShowConsoleMsg("No log file found at:\n" .. log_path .. "\n")
    reaper.ShowConsoleMsg("\nRun the Logger script first to start collecting data.\n")
    return nil
  end
  
  local entries = {}
  for line in file:lines() do
    if line ~= "" then
      local entry = {}
      entry.timestamp = tonumber(line:match('"timestamp":(%d+)'))
      entry.session = line:match('"session":"([^"]*)"')
      entry.action_id = line:match('"action_id":"([^"]*)"')
      entry.action_name = line:match('"action_name":"([^"]*)"')
      entry.source = line:match('"source":"([^"]*)"')
      entry.tracks = tonumber(line:match('"tracks":(%d+)'))
      entry.items = tonumber(line:match('"items":(%d+)'))
      entry.time_since_last = tonumber(line:match('"time_since_last":([%d%.]+)'))
      
      if entry.timestamp then
        table.insert(entries, entry)
      end
    end
  end
  file:close()
  
  return entries
end

-- Count action frequencies
local function analyze_log(entries)
  local counts = {}
  local sessions = {}
  local total = 0
  
  for _, entry in ipairs(entries) do
    if entry.action_name and 
       entry.action_name ~= "Logger Started" and 
       entry.action_name ~= "Logger Stopped" then
      counts[entry.action_name] = (counts[entry.action_name] or 0) + 1
      total = total + 1
    end
    sessions[entry.session] = true
  end
  
  -- Sort by frequency
  local sorted = {}
  for name, count in pairs(counts) do
    table.insert(sorted, {name = name, count = count})
  end
  table.sort(sorted, function(a, b) return a.count > b.count end)
  
  return sorted, total, sessions
end

-- Main
local entries = read_log()
if not entries then return end

local sorted, total, sessions = analyze_log(entries)

-- Count sessions
local session_count = 0
for _ in pairs(sessions) do session_count = session_count + 1 end

reaper.ShowConsoleMsg("\n")
reaper.ShowConsoleMsg("═══════════════════════════════════════════════════════════\n")
reaper.ShowConsoleMsg("              ADAPTIVE MENUS - LOG SUMMARY\n")
reaper.ShowConsoleMsg("═══════════════════════════════════════════════════════════\n\n")

reaper.ShowConsoleMsg(string.format("Total actions logged: %d\n", total))
reaper.ShowConsoleMsg(string.format("Unique actions: %d\n", #sorted))
reaper.ShowConsoleMsg(string.format("Sessions: %d\n", session_count))
reaper.ShowConsoleMsg("\n")

reaper.ShowConsoleMsg("───────────────────────────────────────────────────────────\n")
reaper.ShowConsoleMsg("TOP 20 MOST USED ACTIONS:\n")
reaper.ShowConsoleMsg("───────────────────────────────────────────────────────────\n\n")

for i = 1, math.min(20, #sorted) do
  local entry = sorted[i]
  local pct = (entry.count / total) * 100
  local bar = string.rep("█", math.floor(pct / 2))
  reaper.ShowConsoleMsg(string.format("%3d. %-40s %4d (%5.1f%%) %s\n", 
    i, entry.name:sub(1, 40), entry.count, pct, bar))
end

if #sorted > 20 then
  reaper.ShowConsoleMsg(string.format("\n... and %d more unique actions\n", #sorted - 20))
end

reaper.ShowConsoleMsg("\n═══════════════════════════════════════════════════════════\n")
