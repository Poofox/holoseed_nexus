-- Planty C Launcher for Reaper
-- Add this script to your Reaper actions and assign a hotkey
-- 
-- SETUP:
-- 1. Edit the paths below to match your system
-- 2. Make sure ANTHROPIC_API_KEY is set in your environment
-- 3. Actions > Show action list > Load ReaScript > select this file
-- 4. Assign a hotkey (I suggest Ctrl+Shift+P for "Planty")

---------------------
-- CONFIGURE THESE --
---------------------

-- Path to your Python executable
local python_path = "python3"  -- or full path like "/usr/bin/python3"

-- Path to the claude_chat.py script
local script_path = "/path/to/reaper_claude_chat/claude_chat.py"

-- Your API key (alternatively, set it system-wide)
local api_key = ""  -- Leave empty if already set in environment

---------------------

function launch_planty_c()
    local cmd
    
    if reaper.GetOS():match("Win") then
        -- Windows
        if api_key ~= "" then
            cmd = string.format('start cmd /c "set ANTHROPIC_API_KEY=%s && %s %s"', 
                api_key, python_path, script_path)
        else
            cmd = string.format('start cmd /c "%s %s"', python_path, script_path)
        end
    else
        -- macOS / Linux
        if api_key ~= "" then
            cmd = string.format('ANTHROPIC_API_KEY="%s" %s "%s" &', 
                api_key, python_path, script_path)
        else
            cmd = string.format('%s "%s" &', python_path, script_path)
        end
    end
    
    os.execute(cmd)
    reaper.ShowConsoleMsg("🌱 Planty C launched!\n")
end

-- Run it
launch_planty_c()
