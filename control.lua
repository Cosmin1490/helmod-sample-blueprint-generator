-- Helmod Sample Blueprint Generator
-- Injects a "Generate Blueprint" button into Helmod's summary panel.

local blueprint = require("blueprint")

local BUTTON_NAME = "helmod-sample-blueprint-generator-button"
local DEBUG = false

local function debug_print(msg)
  if DEBUG then
    log("[HSBG] " .. msg)
  end
end

---@param factory_name string
---@return number width, number height
local function get_entity_size(factory_name)
  local proto = prototypes.entity[factory_name]
  if proto then
    return proto.tile_width, proto.tile_height
  end
  game.print({"helmod-sample-blueprint-generator.prototype-not-found", factory_name})
  return 3, 3
end

---@param name string
---@return string[] parts split by "="
local function split_element_name(name)
  local parts = {}
  for part in string.gmatch(name, "[^=]+") do
    table.insert(parts, part)
  end
  return parts
end

---@param player LuaPlayer
---@param model_id string
---@param block_id string|nil
local function create_blueprint(player, model_id, block_id)
  local models = remote.call("helmod_interface", "get_models")
  if not models then
    player.print({"helmod-sample-blueprint-generator.no-models"})
    return
  end

  local model = models[model_id]
  if not model then
    player.print({"helmod-sample-blueprint-generator.no-models"})
    return
  end

  local entities = blueprint.generate_entities(model, block_id, {
    get_entity_size = get_entity_size,
    module_inventory = defines.inventory.assembling_machine_modules,
  })

  if #entities == 0 then
    player.print({"helmod-sample-blueprint-generator.no-recipes"})
    return
  end

  player.clear_cursor()
  local cursor = player.cursor_stack
  if not cursor then return end

  cursor.set_stack({name = "blueprint"})
  local ok, err = pcall(function() cursor.set_blueprint_entities(entities) end)
  if not ok then
    debug_print("ERROR setting blueprint entities: " .. tostring(err))
    cursor.set_stack({name = "blueprint"})
    -- Retry without items/modules
    for _, e in ipairs(entities) do e.items = nil end
    cursor.set_blueprint_entities(entities)
    player.print("[HSBG] Blueprint created without modules (format error). Check log.")
  end

  local label = "Helmod"
  if model.block_root and model.block_root.name then
    label = "Helmod: " .. model.block_root.name
  end
  cursor.label = label

  player.print({"helmod-sample-blueprint-generator.blueprint-created", #entities})
end

---@param player LuaPlayer
---@param model_id string
---@param block_id string|nil
local function inject_button(player, model_id, block_id)
  local screen = player.gui.screen
  local summary_panel = screen["HMSummaryPanel"]
  if not summary_panel or not summary_panel.valid then return end

  local content_panel = summary_panel["content_panel"]
  if not content_panel or not content_panel.valid then return end

  -- Remove existing button if present
  local existing = content_panel[BUTTON_NAME]
  if existing and existing.valid then
    existing.destroy()
  end

  content_panel.add{
    type = "button",
    name = BUTTON_NAME,
    caption = {"helmod-sample-blueprint-generator.generate-blueprint"},
    tooltip = {"helmod-sample-blueprint-generator.generate-blueprint-tooltip"},
    tags = {model_id = model_id, block_id = block_id or ""},
    style = "confirm_button",
  }
end

script.on_event(defines.events.on_gui_click, function(event)
  if not event.element or not event.element.valid then return end

  local name = event.element.name
  local player = game.get_player(event.player_index)
  if not player then return end

  -- Detect Helmod summary panel opening
  local parts = split_element_name(name)
  if parts[1] == "HMSummaryPanel" and parts[2] == "OPEN" then
    local model_id = parts[3]
    local block_id = parts[4]
    debug_print("Summary panel OPEN — model=" .. tostring(model_id) .. " block=" .. tostring(block_id))
    -- Defer injection by 1 tick so Helmod finishes building the panel
    script.on_nth_tick(1, function()
      script.on_nth_tick(1, nil)
      if player.valid then
        inject_button(player, model_id, block_id)
      end
    end)
    return
  end

  -- Handle our own button click
  if name == BUTTON_NAME then
    local tags = event.element.tags
    if tags then
      create_blueprint(player, tags.model_id, tags.block_id ~= "" and tags.block_id or nil)
    end
    return
  end
end)
