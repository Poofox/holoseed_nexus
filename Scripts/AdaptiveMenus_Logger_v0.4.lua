-- AdaptiveMenus Logger v0.4
-- Portable/multi-machine deployment version
-- Part of the Adaptive Menus system
-- by foxAsteria & Planty C 🌱

local script_name = "AdaptiveMenus_Logger"
local version = "0.4"
local schema_version = 1  -- For future compatibility

-- Config
local config = {
  flush_interval = 30,
  max_buffer_size = 100,
  heartbeat_interval = 300,
  quiet_mode = true,           -- Minimal console output for background running
  daily_rotation = true,       -- New log file each day
  debug_interval = 500         -- Less frequent debug output
}

-- Machine identity
local machine_name = (os.getenv("COMPUTERNAME") or os.getenv("HOSTNAME") or "unknown"):gsub("[^%w%-_]", "")

-- Paths - all relative to resource path (portable-friendly)
local resource_path = reaper.GetResourcePath()
local data_dir = resource_path .. "/Data/AdaptiveMenus/"

-- Generate log filename (with optional daily rotation)
local function get_log_filename()
  if config.daily_rotation then
    return string.format("log_%s_%s.jsonl", machine_name, os.date("%Y-%m-%d"))
  else
    return string.format("log_%s.jsonl", machine_name)
  end
end

local log_path = data_dir .. get_log_filename()

-- State
local session_start_time = reaper.time_precise()
local last_action_time = 0
local action_buffer = {}
local last_flush_time = reaper.time_precise()
local last_heartbeat_time = reaper.time_precise()
local session_id = os.time() .. "_" .. machine_name .. "_" .. math.random(1000, 9999)
local action_count = 0
local action_freq = {}  -- Track frequency of each action
local is_running = true
local init_success = false
local current_log_date = os.date("%Y-%m-%d")

-- Toggle state for toolbar button
local _, _, section_id, cmd_id = reaper.get_action_context()
if cmd_id > 0 then
  reaper.SetToggleCommandState(section_id, cmd_id, 1)
  reaper.RefreshToolbar2(section_id, cmd_id)
end

-- Console output (respects quiet mode)
local function log_console(msg, force)
  if not config.quiet_mode or force then
    reaper.ShowConsoleMsg(msg)
  end
end

-- Safe file write test
local function test_write_access(path)
  local test_file = path .. "/.write_test_" .. os.time()
  local f = io.open(test_file, "w")
  if f then
    f:write("test")
    f:close()
    os.remove(test_file)
    return true
  end
  return false
end

-- Ensure directory exists
local function ensure_data_dir()
  reaper.RecursiveCreateDirectory(data_dir, 1)
  if test_write_access(data_dir) then
    return true, "Data directory ready"
  end
  return false, "Cannot write to " .. data_dir
end

-- Get current project info
local function get_project_info()
  local proj, proj_fn = reaper.EnumProjects(-1)
  local proj_name = "(unsaved)"
  if proj_fn and proj_fn ~= "" then
    proj_name = proj_fn:match("([^\\/]+)%.RPP$") or proj_fn:match("([^\\/]+)$") or proj_fn
  end
  return proj_name
end

-- Context detection
local function get_context()
  local ctx = {
    window = "main",
    tracks = reaper.CountSelectedTracks(0) or 0,
    items = reaper.CountSelectedMediaItems(0) or 0,
    cursor = reaper.GetCursorPosition(),
    play_state = reaper.GetPlayState(),
    project = get_project_info(),
    session_time = reaper.time_precise() - session_start_time
  }
  
  local midi_hwnd = reaper.MIDIEditor_GetActive()
  if midi_hwnd then ctx.window = "midi" end
  
  return ctx
end

-- Safe JSON string escape
local function escape_json(str)
  if not str then return "" end
  return (str:gsub('\\', '\\\\'):gsub('"', '\\"'):gsub('\n', '\\n'):gsub('\r', '\\r'):gsub('\t', '\\t'))
end

-- Build JSON line
local function build_json(entry)
  return string.format(
    '{"v":%d,"ts":%d,"sid":"%s","m":"%s","a":"%s","src":"%s","prj":"%s","win":"%s","tr":%d,"it":%d,"st":%.1f,"dt":%.3f}',
    schema_version,
    entry.timestamp,
    entry.session,
    machine_name,
    escape_json(entry.action_name),
    entry.source,
    escape_json(entry.project),
    entry.window,
    entry.tracks,
    entry.items,
    entry.session_time,
    entry.time_since_last
  )
end

-- Log an action
local function log_action(action_name, source)
  local now = reaper.time_precise()
  local context = get_context()
  
  local entry = {
    timestamp = os.time(),
    session = session_id,
    action_name = action_name or "(nil)",
    source = source or "undo",
    project = context.project,
    window = context.window,
    tracks = context.tracks,
    items = context.items,
    session_time = context.session_time,
    time_since_last = last_action_time > 0 and (now - last_action_time) or 0
  }
  
  table.insert(action_buffer, entry)
  last_action_time = now
  action_count = action_count + 1
  
  -- Track frequency
  action_freq[action_name] = (action_freq[action_name] or 0) + 1
  
  log_console(string.format("  #%-4d %s\n", action_count, action_name))
  
  if #action_buffer >= config.max_buffer_size then
    flush_buffer()
  end
end

-- Check for daily rotation
local function check_log_rotation()
  if not config.daily_rotation then return end
  
  local today = os.date("%Y-%m-%d")
  if today ~= current_log_date then
    flush_buffer()
    current_log_date = today
    log_path = data_dir .. get_log_filename()
    log_console("  📅 New day, rotating log: " .. get_log_filename() .. "\n", true)
  end
end

-- Flush buffer to disk
function flush_buffer()
  if #action_buffer == 0 then return true end
  
  local file, err = io.open(log_path, "a")
  if not file then
    log_console("\n  ⚠️  FLUSH ERROR: " .. (err or "unknown") .. "\n", true)
    return false
  end
  
  for _, entry in ipairs(action_buffer) do
    file:write(build_json(entry) .. "\n")
  end
  
  file:close()
  
  log_console(string.format("  💾 Flushed %d actions\n", #action_buffer))
  
  action_buffer = {}
  last_flush_time = reaper.time_precise()
  return true
end

-- Log heartbeat
local function log_heartbeat()
  local file = io.open(log_path, "a")
  if file then
    local ctx = get_context()
    file:write(string.format(
      '{"v":%d,"ts":%d,"sid":"%s","m":"%s","a":"HEARTBEAT","src":"sys","prj":"%s","win":"%s","tr":0,"it":0,"st":%.1f,"dt":0,"cnt":%d}\n',
      schema_version, os.time(), session_id, machine_name, 
      escape_json(ctx.project), ctx.window, ctx.session_time, action_count
    ))
    file:close()
    log_console(string.format("  💓 Heartbeat (%d actions)\n", action_count))
  end
  last_heartbeat_time = reaper.time_precise()
end

-- Main loop
local last_undo_name = ""
local debug_counter = 0
local loop_counter = 0

local function check_for_actions()
  if not is_running then return end
  
  loop_counter = loop_counter + 1
  
  check_log_rotation()
  
  local ok, undo_name = pcall(reaper.Undo_CanUndo2, 0)
  if not ok then undo_name = nil end
  undo_name = undo_name or ""
  
  debug_counter = debug_counter + 1
  if debug_counter >= config.debug_interval then
    debug_counter = 0
    log_console(string.format("  [%s] Loop #%d | Actions: %d\n", 
      os.date("%H:%M"), loop_counter, action_count))
  end
  
  if undo_name ~= "" and undo_name ~= last_undo_name then
    log_action(undo_name, "undo")
    last_undo_name = undo_name
  elseif undo_name == "" and last_undo_name ~= "" then
    last_undo_name = ""
  end
  
  local now = reaper.time_precise()
  if now - last_flush_time > config.flush_interval then
    flush_buffer()
  end
  
  if now - last_heartbeat_time > config.heartbeat_interval then
    log_heartbeat()
  end
  
  reaper.defer(check_for_actions)
end

-- Console banner
local function show_banner()
  reaper.ClearConsole()
  reaper.ShowConsoleMsg("\n")
  reaper.ShowConsoleMsg("════════════════════════════════════════════════════════════\n")
  reaper.ShowConsoleMsg("       🌱 ADAPTIVE MENUS LOGGER v" .. version)
  if config.quiet_mode then
    reaper.ShowConsoleMsg(" (quiet)\n")
  else
    reaper.ShowConsoleMsg("\n")
  end
  reaper.ShowConsoleMsg("════════════════════════════════════════════════════════════\n")
  reaper.ShowConsoleMsg("Session:  " .. session_id .. "\n")
  reaper.ShowConsoleMsg("Machine:  " .. machine_name .. "\n")
  reaper.ShowConsoleMsg("Log:      " .. get_log_filename() .. "\n")
  reaper.ShowConsoleMsg("────────────────────────────────────────────────────────────\n")
end

-- Generate top actions summary
local function get_top_actions(n)
  local sorted = {}
  for action, count in pairs(action_freq) do
    table.insert(sorted, {action = action, count = count})
  end
  table.sort(sorted, function(a, b) return a.count > b.count end)
  
  local result = {}
  for i = 1, math.min(n, #sorted) do
    table.insert(result, sorted[i])
  end
  return result
end

-- Startup
local function init()
  show_banner()
  
  local dir_ok, dir_msg = ensure_data_dir()
  if not dir_ok then
    reaper.ShowConsoleMsg("\n  ❌ FATAL: " .. dir_msg .. "\n")
    return false
  end
  reaper.ShowConsoleMsg("  ✓ " .. dir_msg .. "\n")
  
  local file = io.open(log_path, "a")
  if file then
    file:write(string.format(
      '{"v":%d,"ts":%d,"sid":"%s","m":"%s","a":"SESSION_START","src":"sys","prj":"%s","win":"main","tr":0,"it":0,"st":0,"dt":0}\n',
      schema_version, os.time(), session_id, machine_name, escape_json(get_project_info())
    ))
    file:close()
    reaper.ShowConsoleMsg("  ✓ Log ready\n")
  else
    reaper.ShowConsoleMsg("  ❌ Could not write to log!\n")
    return false
  end
  
  reaper.ShowConsoleMsg("────────────────────────────────────────────────────────────\n")
  reaper.ShowConsoleMsg("  Listening..." .. (config.quiet_mode and " (quiet mode)" or "") .. "\n\n")
  
  init_success = true
  check_for_actions()
  return true
end

-- Cleanup
local function cleanup()
  is_running = false
  
  if init_success then
    flush_buffer()
    
    local file = io.open(log_path, "a")
    if file then
      local session_duration = reaper.time_precise() - session_start_time
      file:write(string.format(
        '{"v":%d,"ts":%d,"sid":"%s","m":"%s","a":"SESSION_END","src":"sys","prj":"%s","win":"main","tr":0,"it":0,"st":%.1f,"dt":0,"cnt":%d,"dur":%.1f}\n',
        schema_version, os.time(), session_id, machine_name, 
        escape_json(get_project_info()), session_duration, action_count, session_duration
      ))
      file:close()
    end
    
    reaper.ShowConsoleMsg("\n────────────────────────────────────────────────────────────\n")
    reaper.ShowConsoleMsg(string.format("  🌱 Session complete: %d actions in %.1f min\n", 
      action_count, (reaper.time_precise() - session_start_time) / 60))
    
    if action_count > 0 then
      reaper.ShowConsoleMsg("\n  Top actions:\n")
      local top = get_top_actions(5)
      for i, item in ipairs(top) do
        reaper.ShowConsoleMsg(string.format("    %d. %s (%d)\n", i, item.action, item.count))
      end
    end
    
    reaper.ShowConsoleMsg("════════════════════════════════════════════════════════════\n\n")
  end
  
  if cmd_id > 0 then
    reaper.SetToggleCommandState(section_id, cmd_id, 0)
    reaper.RefreshToolbar2(section_id, cmd_id)
  end
end

reaper.atexit(cleanup)
init()
