-- @description UndoTreePlant - Undo History Tree Visualizer
-- @author foxAsteria & Claude (Anthropic)
-- @version 0.1.0
-- @changelog
--   Initial development - Phase 1
-- @about
--   # UndoTreePlant
--   A visual undo history tree for REAPER with branching, categories, and macro building.
--
--   ## Features:
--   - Horizontal tree visualization of undo history
--   - Smart action categorization (Track, Item, MIDI, FX, etc.)
--   - Day/Night themes (37%/73% brightness)
--   - Right-click nodes to create branches or add to macros
--   - Icon picker for toolbar customization (inspired by Reapertips & Sexan)
--   - Double-click empty space to refresh from project
--
--   ## Credits:
--   - foxAsteria: Concept, design direction, and testing
--   - Claude (Anthropic): Code implementation
--   - Icon picker inspired by Reapertips & Sexan's Track Icon Selector
--
-- @license GPL v3

local r = reaper
local script_name = "UndoTreePlant"

-- Check for ReaImGui (supports both old and new loading methods)
local ImGui
local imgui_ok = pcall(function()
  -- Try new 0.9+ method first
  ImGui = dofile(r.GetResourcePath() .. '/Scripts/ReaTeam Extensions/API/imgui.lua')('0.9')
end)

if not imgui_ok then
  -- Try alternative path or show error
  r.ShowMessageBox("This script requires ReaImGui extension (v0.9+).\n\nPlease install it via ReaPack:\nExtensions > ReaPack > Synchronize packages", script_name, 0)
  return
end

-- ChildFlags_Borders value (1) - works with ReaImGui 0.9+
-- In 0.10.x, BeginChild requires numeric flags, not boolean
local CHILD_BORDER = 1  -- ImGui.ChildFlags_Borders = 1

--------------------------------------------------------------------------------
-- CONFIGURATION
--------------------------------------------------------------------------------

-- Theme definitions
-- Day: ~73% brightness base, Night: ~37% brightness base
local themes = {
  day = {
    name = "Day",
    -- Base colors (~73% brightness = 0xBB or 187)
    background = 0xBABABAFF,
    panel_bg = 0xB0B0B0FF,
    -- Contrast elements
    active_branch = 0x404040FF,
    inactive_branch = 0x888888FF,
    node_active = 0x303030FF,
    node_inactive = 0x909090FF,
    node_current = 0x2D8C2DFF,      -- Muted green
    selected_node = 0x3366AAFF,     -- Muted blue
    hover_highlight = 0xBB6622FF,   -- Muted orange
    -- Text
    text = 0x202020FF,
    text_dim = 0x606060FF,
    -- Icons (grayscale)
    icon_light = 0xE0E0E0FF,
    icon_dark = 0x303030FF,
  },
  night = {
    name = "Night",
    -- Base colors (~37% brightness = 0x5E or 94, but we'll go a bit darker for contrast)
    background = 0x2E2E2EFF,
    panel_bg = 0x383838FF,
    -- Contrast elements  
    active_branch = 0xC0C0C0FF,
    inactive_branch = 0x606060FF,
    node_active = 0xD0D0D0FF,
    node_inactive = 0x707070FF,
    node_current = 0x66BB66FF,      -- Muted green
    selected_node = 0x5588CCFF,     -- Muted blue
    hover_highlight = 0xDD8844FF,   -- Muted orange
    -- Text
    text = 0xD8D8D8FF,
    text_dim = 0x888888FF,
    -- Icons (grayscale)
    icon_light = 0xC0C0C0FF,
    icon_dark = 0x404040FF,
  },
}

local config = {
  -- Current theme
  theme = "night",
  
  -- Layout - HORIZONTAL tree (time flows left to right)
  node_radius = 8,
  node_spacing_x = 60,    -- Horizontal gap between nodes (time axis)
  node_spacing_y = 40,    -- Vertical gap between branches
  tree_padding = 30,
  sidebar_width = 320,
  action_list_width = 280,  -- 4th column for action list
  show_action_list = false, -- Toggle for 4th column
  
  -- View modes
  view_mode = "both", -- "categories", "chronological", "both"
  
  -- Refresh
  auto_refresh = true,
  last_project_state = nil,
}

-- Helper to get current theme colors
local function theme()
  return themes[config.theme]
end

--------------------------------------------------------------------------------
-- MACRO SYSTEM (for action sequences)
--------------------------------------------------------------------------------
local MacroSystem = {
  presets = {},           -- Saved macro presets
  current_macro = {},     -- Actions being built
  preset_name = "",       -- Name for saving
}

function MacroSystem:add_action(action_id, action_name)
  table.insert(self.current_macro, {
    id = action_id,
    name = action_name,
    clean_name = clean_action_name(action_name),
  })
end

function MacroSystem:remove_action(index)
  table.remove(self.current_macro, index)
end

function MacroSystem:clear()
  self.current_macro = {}
end

function MacroSystem:execute()
  for _, action in ipairs(self.current_macro) do
    -- Execute action via Reaper
    if type(action.id) == "number" then
      r.Main_OnCommand(action.id, 0)
    elseif type(action.id) == "string" then
      local cmd = r.NamedCommandLookup(action.id)
      if cmd > 0 then
        r.Main_OnCommand(cmd, 0)
      end
    end
  end
end

function MacroSystem:save_preset(name)
  self.presets[name] = {}
  for i, action in ipairs(self.current_macro) do
    self.presets[name][i] = { id = action.id, name = action.name, clean_name = action.clean_name }
  end
end

function MacroSystem:load_preset(name)
  if self.presets[name] then
    self.current_macro = {}
    for i, action in ipairs(self.presets[name]) do
      self.current_macro[i] = { id = action.id, name = action.name, clean_name = action.clean_name }
    end
  end
end

--------------------------------------------------------------------------------
-- HOVER STATE (for cross-highlighting between tree and sidebar)
--------------------------------------------------------------------------------
local HoverState = {
  hovered_node = nil,           -- Node being hovered in tree view
  hovered_category = nil,       -- Category being hovered in sidebar
  hovered_history_idx = nil,    -- History index being hovered in sidebar
  dragging_action = nil,        -- Action being dragged from action list
}

--------------------------------------------------------------------------------
-- ICON DRAWING (vector icons via DrawList)
--------------------------------------------------------------------------------
local IconDrawers = {
  -- Track icon: horizontal lines (like a mixer fader)
  ["Track"] = function(draw_list, cx, cy, size, color)
    local s = size * 0.6
    ImGui.DrawList_AddLine(draw_list, cx - s, cy - s*0.6, cx + s, cy - s*0.6, color, 2)
    ImGui.DrawList_AddLine(draw_list, cx - s, cy, cx + s, cy, color, 2)
    ImGui.DrawList_AddLine(draw_list, cx - s, cy + s*0.6, cx + s, cy + s*0.6, color, 2)
  end,
  
  -- Item icon: rectangle (media item)
  ["Item"] = function(draw_list, cx, cy, size, color)
    local s = size * 0.6
    ImGui.DrawList_AddRect(draw_list, cx - s, cy - s*0.5, cx + s, cy + s*0.5, color, 2, 0, 2)
  end,
  
  -- MIDI icon: piano key / note shape
  ["MIDI"] = function(draw_list, cx, cy, size, color)
    local s = size * 0.5
    ImGui.DrawList_AddRectFilled(draw_list, cx - s, cy - s*0.3, cx + s*0.3, cy + s*0.7, color)
    ImGui.DrawList_AddRectFilled(draw_list, cx, cy - s*0.8, cx + s, cy + s*0.2, color)
  end,
  
  -- FX icon: circle with dot (like a knob)
  ["FX"] = function(draw_list, cx, cy, size, color)
    local s = size * 0.6
    ImGui.DrawList_AddCircle(draw_list, cx, cy, s, color, 0, 2)
    ImGui.DrawList_AddCircleFilled(draw_list, cx, cy - s*0.4, s*0.25, color)
  end,
  
  -- Envelope icon: curve/wave
  ["Envelope"] = function(draw_list, cx, cy, size, color)
    local s = size * 0.6
    -- Simple zigzag to represent automation
    ImGui.DrawList_AddLine(draw_list, cx - s, cy + s*0.3, cx - s*0.3, cy - s*0.5, color, 2)
    ImGui.DrawList_AddLine(draw_list, cx - s*0.3, cy - s*0.5, cx + s*0.3, cy + s*0.3, color, 2)
    ImGui.DrawList_AddLine(draw_list, cx + s*0.3, cy + s*0.3, cx + s, cy - s*0.3, color, 2)
  end,
  
  -- Transport icon: play triangle
  ["Transport"] = function(draw_list, cx, cy, size, color)
    local s = size * 0.6
    ImGui.DrawList_AddTriangleFilled(draw_list, cx - s*0.5, cy - s, cx - s*0.5, cy + s, cx + s, cy, color)
  end,
  
  -- View/Nav icon: eye shape
  ["View/Nav"] = function(draw_list, cx, cy, size, color)
    local s = size * 0.6
    ImGui.DrawList_AddCircle(draw_list, cx, cy, s*0.4, color, 0, 2)
    ImGui.DrawList_AddCircleFilled(draw_list, cx, cy, s*0.2, color)
  end,
  
  -- Edit icon: scissors / cut
  ["Edit"] = function(draw_list, cx, cy, size, color)
    local s = size * 0.5
    ImGui.DrawList_AddLine(draw_list, cx - s, cy - s, cx + s, cy + s, color, 2)
    ImGui.DrawList_AddLine(draw_list, cx - s, cy + s, cx + s, cy - s, color, 2)
  end,
  
  -- Markers icon: flag
  ["Markers"] = function(draw_list, cx, cy, size, color)
    local s = size * 0.6
    ImGui.DrawList_AddLine(draw_list, cx - s*0.3, cy - s, cx - s*0.3, cy + s, color, 2)
    ImGui.DrawList_AddTriangleFilled(draw_list, cx - s*0.3, cy - s, cx + s, cy - s*0.5, cx - s*0.3, cy, color)
  end,
  
  -- Script icon: brackets < >
  ["Script"] = function(draw_list, cx, cy, size, color)
    local s = size * 0.5
    ImGui.DrawList_AddLine(draw_list, cx - s*0.3, cy - s, cx - s, cy, color, 2)
    ImGui.DrawList_AddLine(draw_list, cx - s, cy, cx - s*0.3, cy + s, color, 2)
    ImGui.DrawList_AddLine(draw_list, cx + s*0.3, cy - s, cx + s, cy, color, 2)
    ImGui.DrawList_AddLine(draw_list, cx + s, cy, cx + s*0.3, cy + s, color, 2)
  end,
  
  -- Other icon: simple dot
  ["Other"] = function(draw_list, cx, cy, size, color)
    ImGui.DrawList_AddCircleFilled(draw_list, cx, cy, size * 0.3, color)
  end,
}

-- Draw category icon at position
local function draw_category_icon(draw_list, category_name, cx, cy, size, color)
  local drawer = IconDrawers[category_name] or IconDrawers["Other"]
  drawer(draw_list, cx, cy, size, color)
end

--------------------------------------------------------------------------------
-- TOOLBAR ICON PICKER (inspired by Reapertips & Sexan's Track Icon Selector)
--------------------------------------------------------------------------------
local IconPicker = {
  icons = {},              -- Loaded icons { path, name, img_obj }
  categories = {},         -- Icon categories from subfolders
  filtered = {},           -- Filtered icon list
  filter_text = "",
  current_category = 0,    -- 0 = all
  is_open = false,
  target_button = nil,     -- Which button we're picking an icon for
  icon_size = 24,
  loaded = false,
}

-- Scan toolbar_icons folder (based on Reapertips & Sexan's approach)
function IconPicker:scan_icons()
  if self.loaded then return end
  
  local reaper_path = r.GetResourcePath()
  local os_sep = package.config:sub(1, 1)
  
  -- Scan both toolbar_icons (primary) and track_icons (secondary)
  local icon_folders = {
    { path = reaper_path .. "/Data/toolbar_icons", name = "Toolbar" },
    { path = reaper_path .. "/Data/track_icons", name = "Track" },
  }
  
  self.icons = {}
  self.categories = { { name = "All", path = "" } }
  
  -- Scan a directory for png files
  local function scan_dir(dir, category_name)
    local idx = 0
    while true do
      local file = r.EnumerateFiles(dir, idx)
      if not file then break end
      if file:match("%.png$") then
        table.insert(self.icons, {
          path = dir .. os_sep .. file,
          name = file:gsub("%.png$", ""),
          category = category_name or "Root"
        })
      end
      idx = idx + 1
    end
  end
  
  -- Scan each icon folder
  for _, folder in ipairs(icon_folders) do
    -- Check if folder exists
    local test_idx = r.EnumerateFiles(folder.path, 0)
    if test_idx or r.EnumerateSubdirectories(folder.path, 0) then
      -- Add as category
      table.insert(self.categories, { name = folder.name, path = folder.path })
      
      -- Scan root of this folder
      scan_dir(folder.path, folder.name)
      
      -- Scan subdirectories
      local dir_idx = 0
      while true do
        local subdir = r.EnumerateSubdirectories(folder.path, dir_idx)
        if not subdir then break end
        local subpath = folder.path .. os_sep .. subdir
        table.insert(self.categories, { name = folder.name .. "/" .. subdir, path = subpath })
        scan_dir(subpath, folder.name .. "/" .. subdir)
        dir_idx = dir_idx + 1
      end
    end
  end
  
  self.filtered = self.icons
  self.loaded = true
end

function IconPicker:filter(text)
  self.filter_text = text
  if text == "" then
    self.filtered = self.icons
  else
    self.filtered = {}
    local lower_text = text:lower()
    for _, icon in ipairs(self.icons) do
      if icon.name:lower():find(lower_text, 1, true) then
        table.insert(self.filtered, icon)
      end
    end
  end
end

function IconPicker:open(target)
  self:scan_icons()
  self.is_open = true
  self.target_button = target
end

function IconPicker:close()
  self.is_open = false
  self.target_button = nil
end

-- Draw the icon picker popup
function IconPicker:draw()
  if not self.is_open then return nil end
  
  local t = theme()
  local selected_icon = nil
  
  ImGui.SetNextWindowSize(UI.ctx, 400, 350, ImGui.Cond_FirstUseEver)
  
  local visible, open = ImGui.Begin(UI.ctx, "Select Icon", true)
  
  if visible then
    -- Search bar with X to clear
    local changed
    ImGui.SetNextItemWidth(UI.ctx, -50)
    changed, self.filter_text = ImGui.InputText(UI.ctx, "##icon_search", self.filter_text)
    if changed then
      self:filter(self.filter_text)
    end
    ImGui.SameLine(UI.ctx)
    if ImGui.Button(UI.ctx, "X", 20, 0) then
      self.filter_text = ""
      self:filter("")
    end
    if ImGui.IsItemHovered(UI.ctx) then
      ImGui.SetTooltip(UI.ctx, "Clear search")
    end
    
    ImGui.Separator(UI.ctx)
    
    -- Icon grid
    if ImGui.BeginChild(UI.ctx, "icon_grid", -1, -1, CHILD_BORDER) then
      local avail_w = ImGui.GetContentRegionAvail(UI.ctx)
      local icon_size = self.icon_size
      local spacing = 4
      local icons_per_row = math.floor(avail_w / (icon_size + spacing))
      if icons_per_row < 1 then icons_per_row = 1 end
      
      local col = 0
      for i, icon in ipairs(self.filtered) do
        -- Create image object if needed
        if not icon.img_obj then
          local ok, img = pcall(function() return ImGui.CreateImage(icon.path) end)
          if ok and img then
            icon.img_obj = img
            ImGui.Attach(UI.ctx, icon.img_obj)
          end
        end
        
        if icon.img_obj then
          ImGui.PushID(UI.ctx, i)
          if ImGui.ImageButton(UI.ctx, "##icon", icon.img_obj, icon_size, icon_size) then
            selected_icon = icon
            self:close()
          end
          if ImGui.IsItemHovered(UI.ctx) then
            ImGui.SetTooltip(UI.ctx, icon.name)
          end
          ImGui.PopID(UI.ctx)
          
          col = col + 1
          if col < icons_per_row then
            ImGui.SameLine(UI.ctx)
          else
            col = 0
          end
        end
      end
      
      ImGui.EndChild(UI.ctx)
    end
  end
  
  if not open then
    self:close()
  end
  
  ImGui.End(UI.ctx)
  
  return selected_icon
end

--------------------------------------------------------------------------------
-- ACTION CATEGORIES & PARSING
--------------------------------------------------------------------------------
local categories = {
  { name = "Track", prefixes = {"Track:", "SWS/AW:.*track", "SWS:.*track"}, icon = "🎚" },
  { name = "Item", prefixes = {"Item:", "SWS:.*item"}, icon = "📦" },
  { name = "MIDI", prefixes = {"MIDI:", "Edit:.*MIDI", "Edit:.*note", "Edit:.*CC"}, icon = "🎹" },
  { name = "FX", prefixes = {"FX:", "SWS:.*FX"}, icon = "🔌" },
  { name = "Envelope", prefixes = {"Envelope:", "SWS:.*envelope", "SWS:.*env"}, icon = "📈" },
  { name = "Transport", prefixes = {"Transport:", "SWS:.*transport"}, icon = "▶" },
  { name = "View/Nav", prefixes = {"View:", "Navigate:", "Zoom"}, icon = "👁" },
  { name = "Edit", prefixes = {"Edit:", "Cut", "Copy", "Paste", "Delete", "Split"}, icon = "✂" },
  { name = "Markers", prefixes = {"Marker", "Region"}, icon = "🚩" },
  { name = "Script", prefixes = {"Script:"}, icon = "📜" },
  { name = "Other", prefixes = {}, icon = "•" },
}

-- Redundant phrases to strip from action names
local strip_patterns = {
  "^Track: ",
  "^Item: ",
  "^Edit: ",
  "^View: ",
  "^Navigate: ",
  "^Transport: ",
  "^FX: ",
  "^Envelope: ",
  "^Options: ",
  "^Script: ",
  "^SWS/[A-Z]+: ",
  "^SWS: ",
  "%(MIDI CC/OSC only%)",
  "for selected tracks?",
  "for selected items?",
  "on selected tracks?",
  "%(obey time selection[^%)]*%)",
}

local function categorize_action(action_name)
  if not action_name then return categories[#categories] end
  
  for _, cat in ipairs(categories) do
    for _, prefix in ipairs(cat.prefixes) do
      if action_name:match(prefix) then
        return cat
      end
    end
  end
  return categories[#categories] -- "Other"
end

local function clean_action_name(action_name)
  if not action_name then return "Unknown" end
  local cleaned = action_name
  
  for _, pattern in ipairs(strip_patterns) do
    cleaned = cleaned:gsub(pattern, "")
  end
  
  -- Trim whitespace
  cleaned = cleaned:match("^%s*(.-)%s*$")
  
  -- Capitalize first letter if needed
  if #cleaned > 0 then
    cleaned = cleaned:sub(1,1):upper() .. cleaned:sub(2)
  end
  
  return cleaned ~= "" and cleaned or action_name
end

--------------------------------------------------------------------------------
-- UNDO HISTORY DATA STRUCTURE
--------------------------------------------------------------------------------
local UndoTree = {
  nodes = {},           -- All undo states
  root = nil,           -- Root node
  current = nil,        -- Currently active node
  selected = nil,       -- User-selected node in UI
  branches = {},        -- Track branch points
}

-- Node structure
local function create_node(id, name, parent)
  return {
    id = id,
    name = name,
    clean_name = clean_action_name(name),
    category = categorize_action(name),
    parent = parent,
    children = {},
    is_active = false,
    timestamp = os.time(),
  }
end

-- Build tree from Reaper's undo history
function UndoTree:refresh()
  self.nodes = {}
  
  -- Get current undo state
  local current_state = r.Undo_CanUndo2(0) or "Project Start"
  local redo_state = r.Undo_CanRedo2(0)
  
  -- Note: Reaper's undo history is linear - we simulate tree structure
  -- by tracking where branches occur (when you undo and do something new)
  
  -- For now, create linear representation
  -- TODO: Hook into actual undo/redo to detect branching
  
  local root = create_node(0, "Project Start", nil)
  root.is_active = true
  self.root = root
  self.nodes[0] = root
  
  -- Walk back through undo history
  local node_id = 1
  local parent = root
  
  -- We can't directly enumerate undo history, so we use what we know
  -- The current state name tells us where we are
  if current_state and current_state ~= "" then
    local current_node = create_node(node_id, current_state, parent)
    current_node.is_active = true
    parent.children[#parent.children + 1] = current_node
    self.nodes[node_id] = current_node
    self.current = current_node
    node_id = node_id + 1
  else
    self.current = root
  end
  
  -- If there's redo available, it means there's a branch
  if redo_state and redo_state ~= "" then
    local redo_node = create_node(node_id, redo_state .. " (redo)", self.current.parent or root)
    redo_node.is_active = false
    if self.current.parent then
      self.current.parent.children[#self.current.parent.children + 1] = redo_node
    else
      root.children[#root.children + 1] = redo_node
    end
    self.nodes[node_id] = redo_node
  end
  
  return self
end

-- Get path from root to a node
function UndoTree:get_path_to_node(node)
  local path = {}
  local current = node
  while current do
    table.insert(path, 1, current)
    current = current.parent
  end
  return path
end

--------------------------------------------------------------------------------
-- UNDO STATE TRACKER (Hooks into Reaper's undo system)
--------------------------------------------------------------------------------
local StateTracker = {
  last_state = nil,
  history = {},        -- Full history of states we've seen
  max_history = 1000,
}

function StateTracker:check_for_changes()
  local current = r.Undo_CanUndo2(0) or ""
  local redo = r.Undo_CanRedo2(0) or ""
  
  local state_sig = current .. "|" .. redo
  
  if state_sig ~= self.last_state then
    self.last_state = state_sig
    
    -- Record this state
    table.insert(self.history, {
      timestamp = os.time(),
      undo_name = current,
      redo_name = redo,
    })
    
    -- Trim history if too long
    while #self.history > self.max_history do
      table.remove(self.history, 1)
    end
    
    return true -- State changed
  end
  
  return false
end

--------------------------------------------------------------------------------
-- UI STATE
--------------------------------------------------------------------------------
local UI = {
  ctx = nil,
  open = true,
  
  -- Tree view state
  scroll_x = 0,
  scroll_y = 0,
  zoom = 1.0,
  dragging = false,
  drag_start_x = 0,
  drag_start_y = 0,
  
  -- Search/filter
  search_text = "",
  filter_category = nil,
  
  -- Sidebar
  sidebar_scroll = 0,
  
  -- Context menus
  context_menu_node = nil,
  
  -- Action list (4th column)
  action_list_scroll = 0,
  action_search_text = "",
}

--------------------------------------------------------------------------------
-- DRAWING FUNCTIONS - HORIZONTAL TREE (time flows left → right)
--------------------------------------------------------------------------------

-- Hit test: is mouse over this node?
local function is_mouse_over_node(x, y, radius)
  local mx, my = ImGui.GetMousePos(UI.ctx)
  local dx, dy = mx - x, my - y
  return (dx * dx + dy * dy) <= (radius * radius)
end

local function draw_tree_node(draw_list, node, x, y, is_on_active_path, is_current)
  local t = theme()
  local radius = config.node_radius * UI.zoom
  local is_hovered = is_mouse_over_node(x, y, radius + 4)
  local is_selected = (node == UndoTree.selected)
  
  -- Update hover state
  if is_hovered then
    HoverState.hovered_node = node
  end
  
  -- Determine color
  local color
  if is_current then
    color = t.node_current  -- Green = you are here
  elseif is_selected then
    color = t.selected_node
  elseif is_hovered then
    color = t.hover_highlight
  elseif is_on_active_path then
    color = t.node_active
  else
    color = t.node_inactive
  end
  
  -- Selection ring
  if is_selected then
    ImGui.DrawList_AddCircle(draw_list, x, y, radius + 5, t.selected_node, 0, 2.5)
  end
  
  -- Hover ring
  if is_hovered and not is_selected then
    ImGui.DrawList_AddCircle(draw_list, x, y, radius + 5, t.hover_highlight, 0, 2.0)
  end
  
  -- Draw node background circle
  ImGui.DrawList_AddCircleFilled(draw_list, x, y, radius, color)
  
  -- Draw category icon inside node
  local icon_color = is_on_active_path and t.background or t.text
  if is_current or is_selected or is_hovered then
    icon_color = t.background
  end
  draw_category_icon(draw_list, node.category.name, x, y, radius * 0.9, icon_color)
  
  -- Draw tooltip on hover
  if is_hovered then
    ImGui.BeginTooltip(UI.ctx)
    ImGui.Text(UI.ctx, node.category.name .. ": " .. node.clean_name)
    if node.name ~= node.clean_name then
      ImGui.TextDisabled(UI.ctx, "(" .. node.name .. ")")
    end
    ImGui.EndTooltip(UI.ctx)
  end
  
  return is_hovered
end

local function draw_branch_line(draw_list, x1, y1, x2, y2, is_active, is_highlighted)
  local t = theme()
  local color
  if is_highlighted then
    color = t.hover_highlight
  elseif is_active then
    color = t.active_branch
  else
    color = t.inactive_branch
  end
  
  local thickness = (is_active or is_highlighted) and 2.5 or 1.5
  
  -- Horizontal tree: draw right-angle or smooth curve
  -- Style: horizontal line, then vertical, then horizontal (like git graphs)
  local mid_x = (x1 + x2) / 2
  
  if y1 == y2 then
    -- Straight horizontal line
    ImGui.DrawList_AddLine(draw_list, x1, y1, x2, y2, color, thickness)
  else
    -- Curved connection for branches
    ImGui.DrawList_AddBezierCubic(draw_list, 
      x1, y1,                    -- Start
      x1 + (x2-x1)*0.5, y1,      -- Control 1 (horizontal out)
      x1 + (x2-x1)*0.5, y2,      -- Control 2 (vertical transition)
      x2, y2,                    -- End
      color, thickness)
  end
end

-- Recursive layout calculation for horizontal tree
-- Returns: total_height of this subtree, populates positions table
local function calculate_tree_layout_horizontal(node, x, y_center, positions, active_path, depth)
  depth = depth or 0
  
  -- Store this node's position
  positions[node.id] = { 
    x = x, 
    y = y_center, 
    node = node,
    depth = depth 
  }
  
  local num_children = #node.children
  if num_children == 0 then
    return config.node_spacing_y * UI.zoom  -- Leaf node height
  end
  
  -- Calculate total height needed for all children
  local child_heights = {}
  local total_children_height = 0
  
  for i, child in ipairs(node.children) do
    -- First pass: get heights
    local child_x = x + config.node_spacing_x * UI.zoom
    local temp_positions = {}
    local h = calculate_tree_layout_horizontal(child, child_x, 0, temp_positions, active_path, depth + 1)
    child_heights[i] = h
    total_children_height = total_children_height + h
  end
  
  -- Add spacing between children
  total_children_height = total_children_height + (num_children - 1) * config.node_spacing_y * UI.zoom * 0.5
  
  -- Second pass: position children centered around parent
  local child_y = y_center - total_children_height / 2
  
  for i, child in ipairs(node.children) do
    local child_x = x + config.node_spacing_x * UI.zoom
    local child_center_y = child_y + child_heights[i] / 2
    
    calculate_tree_layout_horizontal(child, child_x, child_center_y, positions, active_path, depth + 1)
    
    child_y = child_y + child_heights[i] + config.node_spacing_y * UI.zoom * 0.5
  end
  
  return total_children_height
end

local function draw_tree(draw_list, tree, start_x, start_y, canvas_height)
  if not tree.root then return end
  
  -- Reset hover state at start of frame
  HoverState.hovered_node = nil
  
  -- Build active path set (nodes from root to current)
  local active_path = {}
  local current = tree.current
  while current do
    active_path[current.id] = true
    current = current.parent
  end
  
  -- Build selected path set (nodes from root to selected, if different from current)
  local selected_path = {}
  if tree.selected and tree.selected ~= tree.current then
    local sel = tree.selected
    while sel do
      selected_path[sel.id] = true
      sel = sel.parent
    end
  end
  
  -- Calculate positions - center tree vertically in canvas
  local positions = {}
  local center_y = start_y + canvas_height / 2
  calculate_tree_layout_horizontal(tree.root, start_x, center_y, positions, active_path, 0)
  
  -- Build highlighted path (if hovering a node, highlight path to it)
  local highlight_path = {}
  if HoverState.hovered_node then
    local n = HoverState.hovered_node
    while n do
      highlight_path[n.id] = true
      n = n.parent
    end
  end
  
  -- Draw lines first (so nodes appear on top)
  for id, pos in pairs(positions) do
    local node = pos.node
    for _, child in ipairs(node.children) do
      local child_pos = positions[child.id]
      if child_pos then
        local is_active = active_path[node.id] and active_path[child.id]
        local is_highlighted = highlight_path[node.id] and highlight_path[child.id]
        local is_selected_path = selected_path[node.id] and selected_path[child.id]
        draw_branch_line(draw_list, pos.x, pos.y, child_pos.x, child_pos.y, is_active, is_highlighted or is_selected_path)
      end
    end
  end
  
  -- Draw nodes
  for id, pos in pairs(positions) do
    local is_current = (pos.node == tree.current)
    draw_tree_node(draw_list, pos.node, pos.x, pos.y, active_path[id], is_current)
  end
  
  -- Handle node click - select and show that branch
  if ImGui.IsMouseClicked(UI.ctx, ImGui.MouseButton_Left) and HoverState.hovered_node then
    UndoTree.selected = HoverState.hovered_node
  end
  
  -- Handle double-click on empty space to refresh tree from project
  if ImGui.IsMouseDoubleClicked(UI.ctx, ImGui.MouseButton_Left) and not HoverState.hovered_node then
    if ImGui.IsWindowHovered(UI.ctx) then
      UndoTree:refresh()
      StateTracker:check_for_changes()
    end
  end
  
  -- Handle double-click on node to navigate to that undo state
  if ImGui.IsMouseDoubleClicked(UI.ctx, ImGui.MouseButton_Left) and HoverState.hovered_node then
    -- TODO Phase 2: Actually navigate to this state
    UndoTree.selected = HoverState.hovered_node
  end
  
  -- Right-click context menu for nodes
  if ImGui.IsMouseClicked(UI.ctx, ImGui.MouseButton_Right) and HoverState.hovered_node then
    UI.context_menu_node = HoverState.hovered_node
    ImGui.OpenPopup(UI.ctx, "node_context_menu")
  end
  
  -- Draw node context menu
  if ImGui.BeginPopup(UI.ctx, "node_context_menu") then
    local node = UI.context_menu_node
    if node then
      ImGui.TextDisabled(UI.ctx, node.clean_name)
      ImGui.Separator(UI.ctx)
      
      if ImGui.Selectable(UI.ctx, "Create branch from here") then
        -- Mark this as branch point - new actions will branch from here
        node.is_branch_point = true
        UndoTree.branch_from = node
      end
      
      if ImGui.Selectable(UI.ctx, "Add to macro") then
        MacroSystem:add_action(node.id, node.name)
      end
      
      ImGui.Separator(UI.ctx)
      
      if ImGui.Selectable(UI.ctx, "Go to this state") then
        -- TODO Phase 2: Navigate undo history to this point
      end
    end
    ImGui.EndPopup(UI.ctx)
  end
  
  return positions
end

--------------------------------------------------------------------------------
-- SIDEBAR FUNCTIONS (with hover cross-highlighting)
--------------------------------------------------------------------------------

local function draw_selected_branch_info()
  local t = theme()
  
  if not UndoTree.selected then
    ImGui.TextDisabled(UI.ctx, "Click a node to select it")
    return
  end
  
  local node = UndoTree.selected
  ImGui.PushStyleColor(UI.ctx, ImGui.Col_Text, t.selected_node)
  ImGui.Text(UI.ctx, "Selected: " .. node.clean_name)
  ImGui.PopStyleColor(UI.ctx)
  
  ImGui.TextDisabled(UI.ctx, "Category: " .. node.category.name)
  
  -- Show path to this node
  ImGui.Spacing(UI.ctx)
  ImGui.TextDisabled(UI.ctx, "Path to selected:")
  ImGui.Separator(UI.ctx)
  
  local path = UndoTree:get_path_to_node(node)
  for i, path_node in ipairs(path) do
    local prefix = string.rep("  ", i - 1)
    local is_current = (path_node == UndoTree.current)
    
    if is_current then
      ImGui.PushStyleColor(UI.ctx, ImGui.Col_Text, t.node_current)
      ImGui.Text(UI.ctx, prefix .. "● " .. path_node.clean_name)
      ImGui.PopStyleColor(UI.ctx)
    elseif path_node == node then
      ImGui.PushStyleColor(UI.ctx, ImGui.Col_Text, t.selected_node)
      ImGui.Text(UI.ctx, prefix .. "◆ " .. path_node.clean_name)
      ImGui.PopStyleColor(UI.ctx)
    else
      ImGui.Text(UI.ctx, prefix .. "○ " .. path_node.clean_name)
    end
  end
end

local function draw_chronological_list()
  local t = theme()
  ImGui.Text(UI.ctx, "Chronological History")
  ImGui.Separator(UI.ctx)
  
  -- Show current state
  local current_name = r.Undo_CanUndo2(0) or "Project Start"
  local current_clean = clean_action_name(current_name)
  
  -- Highlight if hovered node matches
  local is_highlighted = HoverState.hovered_node and HoverState.hovered_node.name == current_name
  
  if is_highlighted then
    ImGui.PushStyleColor(UI.ctx, ImGui.Col_Text, t.hover_highlight)
  else
    ImGui.PushStyleColor(UI.ctx, ImGui.Col_Text, t.node_current)
  end
  
  if ImGui.Selectable(UI.ctx, "● " .. current_clean, false) then
    -- Already at current state
  end
  ImGui.PopStyleColor(UI.ctx)
  
  -- Show redo if available
  local redo_name = r.Undo_CanRedo2(0)
  if redo_name then
    local redo_highlighted = HoverState.hovered_node and HoverState.hovered_node.name:match(redo_name)
    
    if redo_highlighted then
      ImGui.PushStyleColor(UI.ctx, ImGui.Col_Text, t.hover_highlight)
    else
      ImGui.PushStyleColor(UI.ctx, ImGui.Col_Text, t.inactive_branch)
    end
    
    if ImGui.Selectable(UI.ctx, "○ " .. clean_action_name(redo_name) .. " →", false) then
      r.Undo_DoRedo2(0)
      UndoTree:refresh()
    end
    ImGui.PopStyleColor(UI.ctx)
  end
  
  -- Show tracked history
  ImGui.Spacing(UI.ctx)
  ImGui.TextDisabled(UI.ctx, "Session History:")
  ImGui.Separator(UI.ctx)
  
  for i = #StateTracker.history, math.max(1, #StateTracker.history - 50), -1 do
    local entry = StateTracker.history[i]
    if entry and entry.undo_name ~= "" then
      local display = clean_action_name(entry.undo_name)
      local cat = categorize_action(entry.undo_name)
      
      -- Check if this entry matches hovered node
      local is_match = HoverState.hovered_node and HoverState.hovered_node.name == entry.undo_name
      
      if is_match then
        ImGui.PushStyleColor(UI.ctx, ImGui.Col_Text, t.hover_highlight)
      end
      
      -- Show category icon + clean name
      local selectable_text = cat.icon .. " " .. display
      local clicked, hovered = ImGui.Selectable(UI.ctx, selectable_text, is_match)
      
      -- Track hover on sidebar items (for reverse highlighting)
      if ImGui.IsItemHovered(UI.ctx) then
        HoverState.hovered_history_idx = i
      end
      
      if is_match then
        ImGui.PopStyleColor(UI.ctx)
      end
    end
  end
end

local function draw_category_list()
  local t = theme()
  ImGui.Text(UI.ctx, "By Category")
  ImGui.Separator(UI.ctx)
  
  -- Group history by category
  local by_category = {}
  for _, cat in ipairs(categories) do
    by_category[cat.name] = { category = cat, items = {} }
  end
  
  for idx, entry in ipairs(StateTracker.history) do
    if entry.undo_name and entry.undo_name ~= "" then
      local cat = categorize_action(entry.undo_name)
      table.insert(by_category[cat.name].items, { entry = entry, idx = idx })
    end
  end
  
  -- Check if hovered node's category should be highlighted
  local highlighted_cat = HoverState.hovered_node and HoverState.hovered_node.category.name or nil
  
  -- Draw category trees
  for _, cat in ipairs(categories) do
    local cat_data = by_category[cat.name]
    if #cat_data.items > 0 then
      local is_cat_highlighted = (highlighted_cat == cat.name)
      
      if is_cat_highlighted then
        ImGui.PushStyleColor(UI.ctx, ImGui.Col_Text, t.hover_highlight)
      end
      
      local header = cat.icon .. " " .. cat.name .. " (" .. #cat_data.items .. ")"
      local tree_open = ImGui.TreeNode(UI.ctx, header)
      
      -- Track hover on category header
      if ImGui.IsItemHovered(UI.ctx) then
        HoverState.hovered_category = cat.name
      end
      
      if is_cat_highlighted then
        ImGui.PopStyleColor(UI.ctx)
      end
      
      if tree_open then
        for i = #cat_data.items, math.max(1, #cat_data.items - 20), -1 do
          local item = cat_data.items[i]
          local display = clean_action_name(item.entry.undo_name)
          
          -- Check if this matches hovered node
          local is_match = HoverState.hovered_node and HoverState.hovered_node.name == item.entry.undo_name
          
          if is_match then
            ImGui.PushStyleColor(UI.ctx, ImGui.Col_Text, t.hover_highlight)
            ImGui.Bullet(UI.ctx)
            ImGui.SameLine(UI.ctx)
            ImGui.Text(UI.ctx, display)
            ImGui.PopStyleColor(UI.ctx)
          else
            ImGui.Bullet(UI.ctx)
            ImGui.SameLine(UI.ctx)
            ImGui.TextDisabled(UI.ctx, display)
          end
        end
        ImGui.TreePop(UI.ctx)
      end
    end
  end
end

local function draw_sidebar()
  local t = theme()
  ImGui.BeginChild(UI.ctx, "sidebar", config.sidebar_width, -1, CHILD_BORDER)
  
  -- Icon-only toolbar row
  -- Theme toggle (sun/moon)
  if ImGui.Button(UI.ctx, config.theme == "night" and "##sun" or "##moon", 24, 24) then
    config.theme = config.theme == "night" and "day" or "night"
  end
  if ImGui.IsItemHovered(UI.ctx) then
    ImGui.SetTooltip(UI.ctx, config.theme == "night" and "Day" or "Night")
    if ImGui.IsMouseClicked(UI.ctx, ImGui.MouseButton_Right) then
      IconPicker:open("theme")
    end
  end
  -- Draw icon on button
  local btn_min_x, btn_min_y = ImGui.GetItemRectMin(UI.ctx)
  local btn_draw_list = ImGui.GetWindowDrawList(UI.ctx)
  if config.theme == "night" then
    -- Sun icon (circle with rays)
    ImGui.DrawList_AddCircleFilled(btn_draw_list, btn_min_x + 12, btn_min_y + 12, 5, t.text)
    for i = 0, 7 do
      local angle = i * math.pi / 4
      local x1, y1 = btn_min_x + 12 + math.cos(angle) * 7, btn_min_y + 12 + math.sin(angle) * 7
      local x2, y2 = btn_min_x + 12 + math.cos(angle) * 10, btn_min_y + 12 + math.sin(angle) * 10
      ImGui.DrawList_AddLine(btn_draw_list, x1, y1, x2, y2, t.text, 1.5)
    end
  else
    -- Moon icon (crescent)
    ImGui.DrawList_AddCircleFilled(btn_draw_list, btn_min_x + 12, btn_min_y + 12, 6, t.text)
    ImGui.DrawList_AddCircleFilled(btn_draw_list, btn_min_x + 15, btn_min_y + 10, 5, t.panel_bg)
  end
  
  ImGui.SameLine(UI.ctx)
  
  -- View mode buttons with right-click icon picker
  -- Categories button (grid icon)
  local cat_selected = config.view_mode == "categories"
  if cat_selected then ImGui.PushStyleColor(UI.ctx, ImGui.Col_Button, t.selected_node) end
  if ImGui.Button(UI.ctx, "##categories", 24, 24) then config.view_mode = "categories" end
  if cat_selected then ImGui.PopStyleColor(UI.ctx) end
  if ImGui.IsItemHovered(UI.ctx) then 
    ImGui.SetTooltip(UI.ctx, "Categories") 
    if ImGui.IsMouseClicked(UI.ctx, ImGui.MouseButton_Right) then
      IconPicker:open("categories")
    end
  end
  -- Draw grid icon
  btn_min_x, btn_min_y = ImGui.GetItemRectMin(UI.ctx)
  for row = 0, 1 do
    for col = 0, 1 do
      ImGui.DrawList_AddRectFilled(btn_draw_list, 
        btn_min_x + 5 + col * 8, btn_min_y + 5 + row * 8,
        btn_min_x + 11 + col * 8, btn_min_y + 11 + row * 8, t.text)
    end
  end
  
  ImGui.SameLine(UI.ctx)
  
  -- Chrono button (list icon)
  local chrono_selected = config.view_mode == "chronological"
  if chrono_selected then ImGui.PushStyleColor(UI.ctx, ImGui.Col_Button, t.selected_node) end
  if ImGui.Button(UI.ctx, "##chrono", 24, 24) then config.view_mode = "chronological" end
  if chrono_selected then ImGui.PopStyleColor(UI.ctx) end
  if ImGui.IsItemHovered(UI.ctx) then 
    ImGui.SetTooltip(UI.ctx, "Timeline")
    if ImGui.IsMouseClicked(UI.ctx, ImGui.MouseButton_Right) then
      IconPicker:open("chrono")
    end
  end
  -- Draw list icon (horizontal lines)
  btn_min_x, btn_min_y = ImGui.GetItemRectMin(UI.ctx)
  ImGui.DrawList_AddLine(btn_draw_list, btn_min_x + 5, btn_min_y + 7, btn_min_x + 19, btn_min_y + 7, t.text, 2)
  ImGui.DrawList_AddLine(btn_draw_list, btn_min_x + 5, btn_min_y + 12, btn_min_x + 19, btn_min_y + 12, t.text, 2)
  ImGui.DrawList_AddLine(btn_draw_list, btn_min_x + 5, btn_min_y + 17, btn_min_x + 19, btn_min_y + 17, t.text, 2)
  
  ImGui.SameLine(UI.ctx)
  
  -- Both button (split icon)
  local both_selected = config.view_mode == "both"
  if both_selected then ImGui.PushStyleColor(UI.ctx, ImGui.Col_Button, t.selected_node) end
  if ImGui.Button(UI.ctx, "##both", 24, 24) then config.view_mode = "both" end
  if both_selected then ImGui.PopStyleColor(UI.ctx) end
  if ImGui.IsItemHovered(UI.ctx) then 
    ImGui.SetTooltip(UI.ctx, "Both")
    if ImGui.IsMouseClicked(UI.ctx, ImGui.MouseButton_Right) then
      IconPicker:open("both")
    end
  end
  -- Draw split icon (two panels)
  btn_min_x, btn_min_y = ImGui.GetItemRectMin(UI.ctx)
  ImGui.DrawList_AddRect(btn_draw_list, btn_min_x + 4, btn_min_y + 5, btn_min_x + 11, btn_min_y + 19, t.text, 0, 0, 1.5)
  ImGui.DrawList_AddRect(btn_draw_list, btn_min_x + 13, btn_min_y + 5, btn_min_x + 20, btn_min_y + 19, t.text, 0, 0, 1.5)
  
  ImGui.SameLine(UI.ctx)
  ImGui.Dummy(UI.ctx, 10, 1)  -- Spacer
  ImGui.SameLine(UI.ctx)
  
  -- Action list toggle (list+ icon)
  if config.show_action_list then ImGui.PushStyleColor(UI.ctx, ImGui.Col_Button, t.selected_node) end
  if ImGui.Button(UI.ctx, "##actionlist", 24, 24) then 
    config.show_action_list = not config.show_action_list 
  end
  if config.show_action_list then ImGui.PopStyleColor(UI.ctx) end
  if ImGui.IsItemHovered(UI.ctx) then 
    ImGui.SetTooltip(UI.ctx, "Actions")
    if ImGui.IsMouseClicked(UI.ctx, ImGui.MouseButton_Right) then
      IconPicker:open("actionlist")
    end
  end
  -- Draw action list icon (list with +)
  btn_min_x, btn_min_y = ImGui.GetItemRectMin(UI.ctx)
  ImGui.DrawList_AddLine(btn_draw_list, btn_min_x + 4, btn_min_y + 7, btn_min_x + 14, btn_min_y + 7, t.text, 1.5)
  ImGui.DrawList_AddLine(btn_draw_list, btn_min_x + 4, btn_min_y + 12, btn_min_x + 14, btn_min_y + 12, t.text, 1.5)
  ImGui.DrawList_AddLine(btn_draw_list, btn_min_x + 4, btn_min_y + 17, btn_min_x + 14, btn_min_y + 17, t.text, 1.5)
  -- Plus sign
  ImGui.DrawList_AddLine(btn_draw_list, btn_min_x + 17, btn_min_y + 8, btn_min_x + 17, btn_min_y + 16, t.text, 1.5)
  ImGui.DrawList_AddLine(btn_draw_list, btn_min_x + 13, btn_min_y + 12, btn_min_x + 21, btn_min_y + 12, t.text, 1.5)
  
  ImGui.Separator(UI.ctx)
  
  -- Selected branch info (always show if something is selected)
  if UndoTree.selected then
    draw_selected_branch_info()
    ImGui.Separator(UI.ctx)
  end
  
  -- Search bar with X to clear
  ImGui.SetNextItemWidth(UI.ctx, -30)
  local changed
  changed, UI.search_text = ImGui.InputText(UI.ctx, "##search", UI.search_text)
  if ImGui.IsItemHovered(UI.ctx) then ImGui.SetTooltip(UI.ctx, "Search history") end
  ImGui.SameLine(UI.ctx)
  if ImGui.Button(UI.ctx, "X", 20, 0) then
    UI.search_text = ""
  end
  if ImGui.IsItemHovered(UI.ctx) then ImGui.SetTooltip(UI.ctx, "Clear search") end
  
  ImGui.Separator(UI.ctx)
  
  -- Draw appropriate list(s)
  if config.view_mode == "both" then
    -- Split view
    local avail_h = select(2, ImGui.GetContentRegionAvail(UI.ctx))
    
    ImGui.BeginChild(UI.ctx, "categories_panel", -1, avail_h / 2, CHILD_BORDER)
    draw_category_list()
    ImGui.EndChild(UI.ctx)
    
    ImGui.BeginChild(UI.ctx, "chrono_panel", -1, -1, CHILD_BORDER)
    draw_chronological_list()
    ImGui.EndChild(UI.ctx)
    
  elseif config.view_mode == "categories" then
    draw_category_list()
  else
    draw_chronological_list()
  end
  
  ImGui.EndChild(UI.ctx)
end

--------------------------------------------------------------------------------
-- MAIN UI LOOP
--------------------------------------------------------------------------------

local function draw_main_window()
  local t = theme()
  
  -- Check for undo state changes
  if StateTracker:check_for_changes() then
    UndoTree:refresh()
  end
  
  -- Reset hover states at start of frame
  HoverState.hovered_category = nil
  HoverState.hovered_history_idx = nil
  -- Note: hovered_node is reset in draw_tree()
  
  -- Set up window
  ImGui.SetNextWindowSize(UI.ctx, 1000, 600, ImGui.Cond_FirstUseEver)
  
  local visible, open = ImGui.Begin(UI.ctx, script_name, true, ImGui.WindowFlags_MenuBar)
  UI.open = open
  
  -- Handle ESC key to close window when focused
  if visible and ImGui.IsWindowFocused(UI.ctx, ImGui.FocusedFlags_RootAndChildWindows) then
    if ImGui.IsKeyPressed(UI.ctx, ImGui.Key_Escape) then
      -- TODO: Save any virtual/pending work here before closing
      UI.open = false
    end
  end
  
  if visible then
    -- Menu bar
    if ImGui.BeginMenuBar(UI.ctx) then
      if ImGui.BeginMenu(UI.ctx, "File") then
        if ImGui.MenuItem(UI.ctx, "Create Snapshot") then
          -- TODO: Implement snapshots
        end
        ImGui.Separator(UI.ctx)
        if ImGui.MenuItem(UI.ctx, "Close") then
          UI.open = false
        end
        ImGui.EndMenu(UI.ctx)
      end
      
      if ImGui.BeginMenu(UI.ctx, "View") then
        if ImGui.MenuItem(UI.ctx, "Reset Zoom") then
          UI.zoom = 1.0
          UI.scroll_x = 0
          UI.scroll_y = 0
        end
        if ImGui.MenuItem(UI.ctx, "Zoom In", "Scroll Up") then
          UI.zoom = math.min(UI.zoom * 1.2, 3.0)
        end
        if ImGui.MenuItem(UI.ctx, "Zoom Out", "Scroll Down") then
          UI.zoom = math.max(UI.zoom / 1.2, 0.3)
        end
        ImGui.Separator(UI.ctx)
        if ImGui.MenuItem(UI.ctx, "Center on Current") then
          -- TODO: Auto-scroll to current node
        end
        ImGui.Separator(UI.ctx)
        if ImGui.MenuItem(UI.ctx, "Day Theme", nil, config.theme == "day") then
          config.theme = "day"
        end
        if ImGui.MenuItem(UI.ctx, "Night Theme", nil, config.theme == "night") then
          config.theme = "night"
        end
        ImGui.EndMenu(UI.ctx)
      end
      
      ImGui.EndMenuBar(UI.ctx)
    end
    
    -- Main content area - tree view + sidebar
    local content_w, content_h = ImGui.GetContentRegionAvail(UI.ctx)
    
    -- Tree canvas (left side)
    local tree_width = content_w - config.sidebar_width - 10
    ImGui.BeginChild(UI.ctx, "tree_canvas", tree_width, -1, CHILD_BORDER)
    
    local canvas_w, canvas_h = ImGui.GetContentRegionAvail(UI.ctx)
    local draw_list = ImGui.GetWindowDrawList(UI.ctx)
    local canvas_pos_x, canvas_pos_y = ImGui.GetCursorScreenPos(UI.ctx)
    
    -- Handle pan/zoom
    if ImGui.IsWindowHovered(UI.ctx) then
      local wheel = ImGui.GetMouseWheel(UI.ctx)
      if wheel ~= 0 then
        local old_zoom = UI.zoom
        UI.zoom = math.max(0.3, math.min(3.0, UI.zoom + wheel * 0.1))
        -- Adjust scroll to zoom toward mouse position (TODO: improve)
      end
      
      if ImGui.IsMouseDragging(UI.ctx, ImGui.MouseButton_Middle) or 
         ImGui.IsMouseDragging(UI.ctx, ImGui.MouseButton_Right) then
        local dx, dy = ImGui.GetMouseDelta(UI.ctx)
        UI.scroll_x = UI.scroll_x + dx
        UI.scroll_y = UI.scroll_y + dy
      end
    end
    
    -- Draw tree (horizontal layout, centered vertically)
    local tree_x = canvas_pos_x + config.tree_padding + UI.scroll_x
    local tree_y = canvas_pos_y + UI.scroll_y
    draw_tree(draw_list, UndoTree, tree_x, tree_y, canvas_h)
    
    -- Info overlay
    ImGui.SetCursorPos(UI.ctx, 10, 10)
    ImGui.PushStyleColor(UI.ctx, ImGui.Col_Text, t.text_dim)
    ImGui.Text(UI.ctx, string.format("Zoom: %.0f%%", UI.zoom * 100))
    ImGui.SetCursorPos(UI.ctx, 10, 26)
    ImGui.Text(UI.ctx, "Pan: Middle/Right drag | Zoom: Scroll")
    ImGui.PopStyleColor(UI.ctx)
    
    -- Show current position indicator
    ImGui.SetCursorPos(UI.ctx, 10, canvas_h - 25)
    local current_name = r.Undo_CanUndo2(0) or "Project Start"
    ImGui.PushStyleColor(UI.ctx, ImGui.Col_Text, t.node_current)
    ImGui.Text(UI.ctx, "● Current: " .. clean_action_name(current_name))
    ImGui.PopStyleColor(UI.ctx)
    
    ImGui.EndChild(UI.ctx)
    
    ImGui.SameLine(UI.ctx)
    
    -- Sidebar (right side)
    draw_sidebar()
  end
  
  ImGui.End(UI.ctx)
end

--------------------------------------------------------------------------------
-- MAIN
--------------------------------------------------------------------------------

local function init()
  UI.ctx = ImGui.CreateContext(script_name)
  UndoTree:refresh()
end

local function loop()
  if not UI.open then return end
  
  draw_main_window()
  
  -- Draw icon picker if open
  local selected_icon = IconPicker:draw()
  if selected_icon then
    -- TODO: Apply selected icon to target button
    -- For now just print it
    -- r.ShowConsoleMsg("Selected icon: " .. selected_icon.name .. "\n")
  end
  
  if UI.open then
    r.defer(loop)
  end
end

local function cleanup()
  -- Nothing to clean up currently
end

-- Run
init()
loop()
r.atexit(cleanup)
