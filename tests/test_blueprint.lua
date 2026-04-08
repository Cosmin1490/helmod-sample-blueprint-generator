package.path = package.path .. ";../?.lua"
local bp = require("blueprint")

-- Helper: mock get_entity_size returning fixed sizes per entity name
local function make_size_fn(sizes)
  return function(name)
    local s = sizes[name]
    if s then return s[1], s[2] end
    return 3, 3
  end
end

-- Helper: check no two entities overlap (axis-aligned bounding boxes)
local function assert_no_overlaps(entities, sizes)
  for i = 1, #entities do
    local a = entities[i]
    local aw, ah = (sizes[a.name] or {3,3})[1], (sizes[a.name] or {3,3})[2]
    local ax1, ay1 = a.position.x - aw/2, a.position.y - ah/2
    local ax2, ay2 = a.position.x + aw/2, a.position.y + ah/2
    for j = i+1, #entities do
      local b = entities[j]
      local bw, bh = (sizes[b.name] or {3,3})[1], (sizes[b.name] or {3,3})[2]
      local bx1, by1 = b.position.x - bw/2, b.position.y - bh/2
      local bx2, by2 = b.position.x + bw/2, b.position.y + bh/2
      local overlap = ax1 < bx2 and ax2 > bx1 and ay1 < by2 and ay2 > by1
      assert.is_false(overlap,
        string.format("Entity %d (%s @ %.1f,%.1f) overlaps entity %d (%s @ %.1f,%.1f)",
          i, a.name, a.position.x, a.position.y,
          j, b.name, b.position.x, b.position.y))
    end
  end
end

-- Helper: count entities by name
local function count_by_name(entities)
  local counts = {}
  for _, e in ipairs(entities) do
    counts[e.name] = (counts[e.name] or 0) + 1
  end
  return counts
end

-- ── Test fixtures from real Helmod data ──

-- Coal-gas-from-coke: 1 recipe, factory.count=11.25 → 12 distilators
local coal_model = {
  block_root = {
    class = "Block",
    id = "block_1",
    name = "coal-gas-from-coke",
    children = {
      R1 = {
        class = "Recipe",
        name = "coal-gas-from-coke",
        type = "recipe",
        count = 2.25,
        factory = {
          name = "distilator",
          count = 11.25,
          amount = 5,
          modules = {},
        },
      },
    },
  },
  blocks = {},
}

-- Tin-plate-2: 5 recipes, different factory types and sizes
local tin_model = {
  block_root = {
    class = "Block",
    id = "block_1",
    name = "tin-plate-2",
    children = {
      R1 = {
        class = "Recipe", name = "tin-plate-2", type = "recipe",
        factory = {name = "steel-furnace", count = 12.5, amount = 12.5, modules = {}},
      },
      R2 = {
        class = "Recipe", name = "grade-2-crush-tin", type = "recipe",
        factory = {name = "jaw-crusher", count = 4, amount = 4, modules = {}},
      },
      R3 = {
        class = "Recipe", name = "grade-1-tin", type = "recipe",
        factory = {name = "automated-screener-mk01", count = 3, amount = 3, modules = {}},
      },
      R4 = {
        class = "Recipe", name = "ore-tin", type = "resource",
        factory = {name = "fluid-drill-mk02", count = 1, amount = 1, modules = {}},
      },
      R5 = {
        class = "Recipe", name = "water->steam#250", type = "boiler",
        factory = {name = "oil-boiler-mk01", count = 1, amount = 1, modules = {}},
      },
    },
  },
  blocks = {},
}

local tin_sizes = {
  ["steel-furnace"] = {3, 3},
  ["jaw-crusher"] = {5, 5},
  ["automated-screener-mk01"] = {7, 7},
  ["fluid-drill-mk02"] = {5, 5},
  ["oil-boiler-mk01"] = {5, 5},
}

-- ── Tests ──

describe("collect_recipes", function()
  it("collects flat children", function()
    local recipes = bp.collect_recipes(coal_model.block_root)
    assert.equals(1, #recipes)
    assert.equals("coal-gas-from-coke", recipes[1].name)
  end)

  it("collects nested children recursively", function()
    local block = {
      children = {
        R1 = {
          class = "Recipe", name = "parent", type = "recipe",
          factory = {name = "a", count = 1},
          children = {
            R1a = {
              class = "Recipe", name = "child", type = "recipe",
              factory = {name = "b", count = 2},
            },
          },
        },
      },
    }
    local recipes = bp.collect_recipes(block)
    assert.equals(2, #recipes)
    local names = {}
    for _, r in ipairs(recipes) do names[r.name] = true end
    assert.is_true(names["parent"])
    assert.is_true(names["child"])
  end)
end)

describe("build_module_items", function()
  local INV = 4 -- mock defines.inventory.assembling_machine_modules

  it("returns nil for empty modules", function()
    assert.is_nil(bp.build_module_items({}, INV))
  end)

  it("expands single module type with amount", function()
    local modules = {{name = "fawogae", quality = "normal", amount = 10}}
    local items = bp.build_module_items(modules, INV)
    assert.equals(10, #items)
    for i, item in ipairs(items) do
      assert.equals("fawogae", item.id.name)
      assert.equals("normal", item.id.quality)
      assert.equals(i - 1, item.items.in_inventory[1].stack)
    end
  end)

  it("expands mixed module types with correct slot ordering", function()
    local modules = {
      {name = "fawogae", quality = "normal", amount = 5},
      {name = "fawogae-mk02", quality = "normal", amount = 5},
    }
    local items = bp.build_module_items(modules, INV)
    assert.equals(10, #items)
    -- First 5: fawogae, slots 0-4
    for i = 1, 5 do
      assert.equals("fawogae", items[i].id.name)
      assert.equals(i - 1, items[i].items.in_inventory[1].stack)
    end
    -- Next 5: fawogae-mk02, slots 5-9
    for i = 6, 10 do
      assert.equals("fawogae-mk02", items[i].id.name)
      assert.equals(i - 1, items[i].items.in_inventory[1].stack)
    end
  end)

  it("preserves module quality", function()
    local modules = {{name = "speed-module-3", quality = "rare", amount = 2}}
    local items = bp.build_module_items(modules, INV)
    assert.equals(2, #items)
    assert.equals("rare", items[1].id.quality)
    assert.equals("rare", items[2].id.quality)
  end)

  it("skips modules with empty name", function()
    local modules = {{name = "", quality = "normal", amount = 5}}
    assert.is_nil(bp.build_module_items(modules, INV))
  end)

  it("defaults amount to 1 when missing", function()
    local modules = {{name = "beacon-module", quality = "normal"}}
    local items = bp.build_module_items(modules, INV)
    assert.equals(1, #items)
  end)
end)

describe("generate_entities", function()
  describe("simple model (coal-gas-from-coke)", function()
    local sizes = {distilator = {8, 8}}
    local opts = {get_entity_size = make_size_fn(sizes)}
    local entities = bp.generate_entities(coal_model, "block_1", opts)

    it("generates correct building count from factory.count", function()
      assert.equals(12, #entities)
    end)

    it("sets correct entity name", function()
      for _, e in ipairs(entities) do
        assert.equals("distilator", e.name)
      end
    end)

    it("sets recipe for recipe-type entries", function()
      for _, e in ipairs(entities) do
        assert.equals("coal-gas-from-coke", e.recipe)
      end
    end)

    it("assigns sequential entity numbers", function()
      for i, e in ipairs(entities) do
        assert.equals(i, e.entity_number)
      end
    end)

    it("produces no overlapping buildings", function()
      assert_no_overlaps(entities, sizes)
    end)
  end)

  describe("multi-recipe model (tin-plate-2)", function()
    local opts = {get_entity_size = make_size_fn(tin_sizes)}
    local entities = bp.generate_entities(tin_model, "block_1", opts)

    it("generates correct total building count", function()
      -- ceil(12.5) + 4 + 3 + 1 + 1 = 22
      assert.equals(22, #entities)
    end)

    it("generates correct count per factory type", function()
      local counts = count_by_name(entities)
      assert.equals(13, counts["steel-furnace"])
      assert.equals(4, counts["jaw-crusher"])
      assert.equals(3, counts["automated-screener-mk01"])
      assert.equals(1, counts["fluid-drill-mk02"])
      assert.equals(1, counts["oil-boiler-mk01"])
    end)

    it("does not set recipe on resource/boiler types", function()
      for _, e in ipairs(entities) do
        if e.name == "fluid-drill-mk02" or e.name == "oil-boiler-mk01" then
          assert.is_nil(e.recipe)
        end
      end
    end)

    it("produces no overlapping buildings", function()
      assert_no_overlaps(entities, tin_sizes)
    end)
  end)

  describe("row wrapping", function()
    local model = {
      block_root = {
        id = "block_1",
        children = {
          R1 = {
            class = "Recipe", name = "test", type = "recipe",
            factory = {name = "machine", count = 25, modules = {}},
          },
        },
      },
      blocks = {},
    }
    local sizes = {machine = {3, 3}}
    local opts = {get_entity_size = make_size_fn(sizes), per_row = 10}
    local entities = bp.generate_entities(model, nil, opts)

    it("generates all 25 entities", function()
      assert.equals(25, #entities)
    end)

    it("wraps into 3 rows", function()
      local y_values = {}
      for _, e in ipairs(entities) do
        y_values[e.position.y] = (y_values[e.position.y] or 0) + 1
      end
      local row_count = 0
      for _ in pairs(y_values) do row_count = row_count + 1 end
      assert.equals(3, row_count)
    end)

    it("has 10, 10, 5 per row", function()
      local rows = {}
      for _, e in ipairs(entities) do
        rows[e.position.y] = (rows[e.position.y] or 0) + 1
      end
      local counts = {}
      for _, c in pairs(rows) do table.insert(counts, c) end
      table.sort(counts)
      assert.same({5, 10, 10}, counts)
    end)

    it("produces no overlapping buildings", function()
      assert_no_overlaps(entities, sizes)
    end)
  end)

  describe("block_id filtering", function()
    it("returns empty when block_id does not match", function()
      local entities = bp.generate_entities(coal_model, "nonexistent", {})
      assert.equals(0, #entities)
    end)
  end)

  describe("quality", function()
    it("sets quality on entity when not normal", function()
      local model = {
        block_root = {
          id = "b1",
          children = {
            R1 = {
              class = "Recipe", name = "test", type = "recipe",
              factory = {name = "machine", count = 1, quality = "rare", modules = {}},
            },
          },
        },
        blocks = {},
      }
      local entities = bp.generate_entities(model, nil, {})
      assert.equals("rare", entities[1].quality)
    end)

    it("omits quality when normal", function()
      local entities = bp.generate_entities(coal_model, nil, {})
      assert.is_nil(entities[1].quality)
    end)
  end)
end)
