"""Generate Factorio blueprint JSON from a Helmod ProductionModel."""

from __future__ import annotations

from .model import Factory, ModuleSpec, ProductionModel

# Factorio 2.0 blueprint version number (2.0.x)
# Format: major<<54 | minor<<30 | patch<<14 | dev
# 2.0.11.0 = 562949953945600
BLUEPRINT_VERSION = 562949953945600

BLOCK_GAP = 2  # extra grid rows between blocks


def _build_module_items(modules: list[ModuleSpec]) -> list[dict]:
    """Build the Factorio 2.0 blueprint items array for modules.

    In Factorio 2.0, modules in blueprint entities use:
    {"id": {"name": "module-name", "quality": "normal"}, "items": {"in_inventory": [...]}}

    But the simpler flat format also works for import:
    [{"item": {"name": "module-name"}, "index": N}]
    """
    items = []
    index = 1
    for mod in modules:
        for _ in range(mod.count):
            items.append({
                "item": {"name": mod.name, "quality": "normal"},
                "index": index,
            })
            index += 1
    return items


def _build_entity(
    entity_number: int,
    factory: Factory,
    recipe_name: str,
    x: float,
    y: float,
) -> dict:
    """Build a single blueprint entity dict."""
    entity: dict = {
        "entity_number": entity_number,
        "name": factory.name,
        "position": {"x": x, "y": y},
    }

    if recipe_name:
        entity["recipe"] = recipe_name

    if factory.modules:
        items = _build_module_items(factory.modules)
        if items:
            entity["items"] = items

    return entity


def generate_blueprint(
    model: ProductionModel,
    grid_spacing: int = 12,
    per_row: int = 10,
    label: str | None = None,
) -> dict:
    """Generate a Factorio blueprint dict from a ProductionModel.

    Places buildings on a simple grid, left to right, top to bottom.
    Each block's recipes are placed in sequence with a gap between blocks.

    Args:
        model: The parsed Helmod production model.
        grid_spacing: Distance between building centers (default 12, fits Pyanodon's large buildings).
        per_row: Max buildings per row before wrapping to next row.
        label: Optional blueprint label.
    """
    entities = []
    entity_number = 1
    current_row = 0
    current_col = 0

    for block_idx, block in enumerate(model.blocks):
        if block_idx > 0:
            # Gap between blocks
            current_row += BLOCK_GAP
            current_col = 0

        for recipe in block.recipes:
            for _i in range(recipe.building_count):
                x = current_col * grid_spacing + grid_spacing / 2
                y = current_row * grid_spacing + grid_spacing / 2

                entity = _build_entity(
                    entity_number=entity_number,
                    factory=recipe.factory,
                    recipe_name=recipe.name,
                    x=x,
                    y=y,
                )
                entities.append(entity)
                entity_number += 1

                current_col += 1
                if current_col >= per_row:
                    current_col = 0
                    current_row += 1

            # New row for next recipe
            if current_col > 0:
                current_col = 0
                current_row += 1

    blueprint: dict = {
        "blueprint": {
            "entities": entities,
            "item": "blueprint",
            "version": BLUEPRINT_VERSION,
        }
    }

    if label:
        blueprint["blueprint"]["label"] = label

    return blueprint
