-- AdaptiveMenus Logger v0.2
-- Now with visible state reporting!
-- Part of the Adaptive Menus system
-- by foxAsteria & Planty C 🌱

local script_name = "AdaptiveMenus_Logger"
local version = "0.2"

-- Config
local config = {
  flush_interval = 30,          -- How often to write to disk (seconds)
  max_buffer_size = 100,        -- Force flush if buffer gets this big
  log_file = "adaptive_menus_log.json"
}

-- Get resource path for storing data
local resource_path = reaper.GetResourcePath()
local data_dir = resource_path .. "/Scripts/AdaptiveMenus/"
local log_path = data_dir .. config.log_file

-- Ensure data directory exists
reaper.RecursiveCreateDirectory(data_dir, 1)

-- State
local last_action_time = 0
local action_buffer = {}
local last_flush_time = reaper.time_precise()
local session_id = os.time() .. "_" .. math.random(1000, 9999)
local action_count = 0
local is_running = true

-- Toggle state for toolbar button (makes button light up when active)
local _, _, section_id, cmd_id = reaper.get_action_context()
if cmd_id > 0 then
  reaper.SetToggleCommandState(section_id, cmd_id, 1)
  reaper.RefreshToolbar2(section_id, cmd_id)
end

-- Console banner
reaper.ClearConsole()
reaper.ShowConsoleMsg("\n")
reaper.ShowConsoleMsg("═══════════════════════════════════════════════════════════\n")
reaper.ShowConsoleMsg("       🌱 ADAPTIVE MENUS LOGGER v" .. version .. " - ACTIVE\n")
reaper.ShowConsoleMsg("═══════════════════════════════════════════════════════════\n")
reaper.ShowConsoleMsg("Session: " .. session_id .. "\n")
reaper.ShowConsoleMsg("Log file: " .. log_path .. "\n")
reaper.ShowConsoleMsg("───────────────────────────────────────────────────────────\n")
reaper.ShowConsoleMsg("Listening for actions...\n\n")

-- Context detection
local function get_context()
  local ctx = {
    window = "unknown",
    selection = {
      tracks = 0,
      items = 0
    },
    edit_cursor = reaper.GetCursorPosition(),
    play_state = reaper.GetPlayState(),
    project_length = reaper.GetProjectLength(0)
  }
  
  ctx.selection.tracks = reaper.CountSelectedTracks(0)
  ctx.selection.items = reaper.CountSelectedMediaItems(0)
  
  -- Check if we're in MIDI editor
  local midi_hwnd = reaper.MIDIEditor_GetActive()
  if midi_hwnd then
    ctx.window = "midi_editor"
  end
  
  return ctx
end

-- Log an action
local function log_action(action_name, source)
  local now = reaper.time_precise()
  local context = get_context()
  
  local entry = {
    timestamp = os.time(),
    timestamp_precise = now,
    session = session_id,
    action_name = action_name,
    source = source or "unknown",
    context = context,
    time_since_last = last_action_time > 0 and (now - last_action_time) or 0
  }
  
  table.insert(action_buffer, entry)
  last_action_time = now
  action_count = action_count + 1
  
  -- Show in console
  reaper.ShowConsoleMsg(string.format("  #%-4d [%s] %s\n", 
    action_count, os.date("%H:%M:%S"), action_name))
  
  if #action_buffer >= config.max_buffer_size then
    flush_buffer()
  end
end

-- Flush buffer to disk
function flush_buffer()
  if #action_buffer == 0 then return end
  
  local file = io.open(log_path, "a")
  if not file then
    reaper.ShowConsoleMsg("\n  ⚠️  Error: Could not open log file!\n")
    return
  end
  
  for _, entry in ipairs(action_buffer) do
    local json = string.format(
      '{"timestamp":%d,"session":"%s","action_name":"%s","source":"%s","tracks":%d,"items":%d,"time_since_last":%.3f}\n',
      entry.timestamp,
      entry.session,
      (entry.action_name or ""):gsub('"', '\\"'),
      entry.source,
      entry.context.selection.tracks,
      entry.context.selection.items,
      entry.time_since_last
    )
    file:write(json)
  end
  
  file:close()
  
  reaper.ShowConsoleMsg(string.format("\n  💾 Saved %d actions to disk (total: %d)\n\n", #action_buffer, action_count))
  
  action_buffer = {}
  last_flush_time = reaper.time_precise()
end

-- Watch undo history for changes
local last_undo_name = ""
local debug_counter = 0
local DEBUG_INTERVAL = 100  -- Print debug info every N cycles

local function check_for_actions()
  if not is_running then return end
  
  local undo_name = reaper.Undo_CanUndo2(0)
  
  -- Debug output every N cycles
  debug_counter = debug_counter + 1
  if debug_counter >= DEBUG_INTERVAL then
    debug_counter = 0
    reaper.ShowConsoleMsg(string.format("  [DEBUG] Undo state: \"%s\" | Last: \"%s\"\n", 
      tostring(undo_name), tostring(last_undo_name)))
  end
  
  -- Check if undo name changed
  if undo_name and undo_name ~= last_undo_name then
    reaper.ShowConsoleMsg(string.format("  [DEBUG] CHANGE DETECTED: \"%s\" -> \"%s\"\n", 
      tostring(last_undo_name), tostring(undo_name)))
    
    if undo_name ~= "" then
      log_action(undo_name, "undo_detected")
    end
    last_undo_name = undo_name
  end
  
  -- Periodic flush
  local now = reaper.time_precise()
  if now - last_flush_time > config.flush_interval then
    flush_buffer()
  end
  
  reaper.defer(check_for_actions)
end

-- Startup
local function init()
  local file = io.open(log_path, "a")
  if file then
    file:write(string.format(
      '{"timestamp":%d,"session":"%s","action_name":"SESSION_START","source":"system","tracks":0,"items":0,"time_since_last":0}\n',
      os.time(), session_id
    ))
    file:close()
    reaper.ShowConsoleMsg("  ✓ Log file ready\n\n")
  else
    reaper.ShowConsoleMsg("  ⚠️  Warning: Could not write to log file!\n")
    reaper.ShowConsoleMsg("     Check folder exists: " .. data_dir .. "\n\n")
  end
  
  check_for_actions()
end

-- Cleanup on exit
local function cleanup()
  is_running = false
  flush_buffer()
  
  local file = io.open(log_path, "a")
  if file then
    file:write(string.format(
      '{"timestamp":%d,"session":"%s","action_name":"SESSION_END","source":"system","tracks":0,"items":0,"time_since_last":0}\n',
      os.time(), session_id
    ))
    file:close()
  end
  
  -- Turn off toolbar button
  if cmd_id > 0 then
    reaper.SetToggleCommandState(section_id, cmd_id, 0)
    reaper.RefreshToolbar2(section_id, cmd_id)
  end
  
  reaper.ShowConsoleMsg("\n───────────────────────────────────────────────────────────\n")
  reaper.ShowConsoleMsg(string.format("  🌱 Logger stopped. Total actions: %d\n", action_count))
  reaper.ShowConsoleMsg("═══════════════════════════════════════════════════════════\n\n")
end

reaper.atexit(cleanup)

-- Start
init()
