-- Blueprint generation logic for Helmod Sample Blueprint Generator
-- Pure logic module — no Factorio API dependencies.
-- Factorio-specific lookups (entity sizes, inventory defines) are injected via opts.

local M = {}

local DEFAULT_GAP = 2
local DEFAULT_PER_ROW = 10
local BLOCK_GAP_ROWS = 2
local FALLBACK_SIZE = 3

--- Recursively collect all recipes from a block's children tree.
---@param node table block or recipe with children
---@return table[] flat list of recipe tables
function M.collect_recipes(node)
  local result = {}
  local children = node.children or {}
  for _, recipe in pairs(children) do
    table.insert(result, recipe)
    if recipe.children and next(recipe.children) then
      for _, sub in ipairs(M.collect_recipes(recipe)) do
        table.insert(result, sub)
      end
    end
  end
  -- Sort by index for deterministic layout (Helmod assigns index=0,1,2,...)
  table.sort(result, function(a, b)
    return (a.index or 0) < (b.index or 0)
  end)
  return result
end

--- Build the items table for modules in Factorio 2.0 blueprint format.
---@param modules table[] array of {name, quality, amount} from Helmod
---@param module_inventory number defines.inventory value for assembling_machine_modules
---@return table[]|nil items array or nil if no modules
function M.build_module_items(modules, module_inventory)
  if not modules then return nil end
  local items = {}
  local slot = 0
  for _, mod in pairs(modules) do
    if mod.name and mod.name ~= "" then
      local mod_quality = mod.quality or "normal"
      local mod_count = mod.amount or 1
      for _ = 1, mod_count do
        items[#items + 1] = {
          id = {name = mod.name, quality = mod_quality},
          items = {
            in_inventory = {{
              inventory = module_inventory,
              stack = slot,
              count = 1,
            }},
          },
        }
        slot = slot + 1
      end
    end
  end
  if #items == 0 then return nil end
  return items
end

--- Generate blueprint entities from a Helmod model.
---@param model table Helmod model from get_models()
---@param block_id string|nil specific block ID, or nil for all blocks
---@param opts table {get_entity_size=fn(name)->w,h; module_inventory=number; per_row=number; gap=number}
---@return table[] entities for set_blueprint_entities
function M.generate_entities(model, block_id, opts)
  opts = opts or {}
  local get_entity_size = opts.get_entity_size or function() return FALLBACK_SIZE, FALLBACK_SIZE end
  local module_inventory = opts.module_inventory or 4 -- defines.inventory.assembling_machine_modules
  local per_row = opts.per_row or DEFAULT_PER_ROW
  local gap = opts.gap or DEFAULT_GAP

  local entities = {}
  local entity_number = 1
  local cursor_y = 0

  -- Collect blocks to process
  local blocks_to_process = {}
  if model.block_root then
    if block_id and model.block_root.id == block_id then
      table.insert(blocks_to_process, model.block_root)
    elseif not block_id then
      table.insert(blocks_to_process, model.block_root)
    end
  end
  for _, block in pairs(model.blocks or {}) do
    if not block_id or block.id == block_id then
      table.insert(blocks_to_process, block)
    end
  end

  for block_idx, block in ipairs(blocks_to_process) do
    if block_idx > 1 then
      cursor_y = cursor_y + BLOCK_GAP_ROWS * gap
    end

    local all_recipes = M.collect_recipes(block)

    for _, recipe in ipairs(all_recipes) do
      if recipe.factory and recipe.factory.name then
        local factory = recipe.factory
        local count = math.max(1, math.ceil(factory.count or factory.amount or 1))
        local w, h = get_entity_size(factory.name)
        local cell_w = w + gap
        local cell_h = h + gap
        local col = 0

        for _ = 1, count do
          local x = col * cell_w + w / 2
          local y = cursor_y + h / 2

          local entity = {
            entity_number = entity_number,
            name = factory.name,
            position = {x = x, y = y},
          }

          -- Recipe assignment (only for crafting recipes, not resources/boilers)
          if recipe.name and recipe.type == "recipe" then
            entity.recipe = recipe.name
          end

          -- Quality (Factorio 2.0)
          if factory.quality and factory.quality ~= "normal" and factory.quality ~= "" then
            entity.quality = factory.quality
          end

          -- Modules
          local items = M.build_module_items(factory.modules, module_inventory)
          if items then
            entity.items = items
          end

          table.insert(entities, entity)
          entity_number = entity_number + 1

          col = col + 1
          if col >= per_row then
            col = 0
            cursor_y = cursor_y + cell_h
          end
        end

        -- Advance Y past this recipe's row(s)
        cursor_y = cursor_y + cell_h
      end
    end
  end

  return entities
end

return M
