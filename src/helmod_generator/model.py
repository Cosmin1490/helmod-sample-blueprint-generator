"""Data classes for Helmod production model and parsing logic."""

from __future__ import annotations

import math
from dataclasses import dataclass, field


@dataclass
class ModuleSpec:
    name: str
    count: int


@dataclass
class Factory:
    name: str
    modules: list[ModuleSpec] = field(default_factory=list)


@dataclass
class Beacon:
    name: str
    modules: list[ModuleSpec] = field(default_factory=list)
    per_factory: float = 0
    per_factory_constant: float = 0


@dataclass
class Recipe:
    name: str
    recipe_type: str
    factory: Factory
    beacons: list[Beacon] = field(default_factory=list)
    count: float = 1.0

    @property
    def building_count(self) -> int:
        """Number of buildings to place (rounded up)."""
        return max(1, math.ceil(self.count))


@dataclass
class Block:
    name: str
    recipes: list[Recipe] = field(default_factory=list)


@dataclass
class ProductionModel:
    blocks: list[Block] = field(default_factory=list)


def _parse_modules(raw: dict) -> list[ModuleSpec]:
    """Extract modules from a factory/beacon dict.

    Prefers module_priority (ordered list) over modules (dict).
    """
    # Try module_priority first (newer Helmod format)
    priority = raw.get("module_priority")
    if priority and isinstance(priority, dict):
        modules = []
        for _idx, entry in sorted(priority.items(), key=lambda x: x[0]):
            if isinstance(entry, dict) and entry.get("name"):
                name = entry["name"]
                amount = int(entry.get("amount", 1))
                if amount > 0:
                    modules.append(ModuleSpec(name=name, count=amount))
        if modules:
            return modules

    # Fallback to modules dict
    modules_dict = raw.get("modules")
    if modules_dict and isinstance(modules_dict, dict):
        return [
            ModuleSpec(name=name, count=int(count))
            for name, count in modules_dict.items()
            if isinstance(count, (int, float)) and count > 0
        ]

    return []


def _parse_factory(raw: dict) -> Factory:
    """Parse a factory dict into a Factory object."""
    return Factory(
        name=raw.get("name", "unknown"),
        modules=_parse_modules(raw),
    )


def _parse_beacon(raw: dict) -> Beacon:
    """Parse a beacon dict into a Beacon object."""
    return Beacon(
        name=raw.get("name", "beacon"),
        modules=_parse_modules(raw),
        per_factory=float(raw.get("per_factory", 0)),
        per_factory_constant=float(raw.get("per_factory_constant", 0)),
    )


def _parse_recipe(raw: dict) -> Recipe:
    """Parse a recipe/child dict into a Recipe object."""
    factory_raw = raw.get("factory", {})
    factory = _parse_factory(factory_raw) if factory_raw else Factory(name="unknown")

    beacons = []
    beacons_raw = raw.get("beacons")
    if beacons_raw and isinstance(beacons_raw, dict):
        for _idx, beacon_raw in sorted(beacons_raw.items(), key=lambda x: x[0]):
            if isinstance(beacon_raw, dict) and beacon_raw.get("name"):
                beacons.append(_parse_beacon(beacon_raw))

    # The factory count (how many buildings needed)
    count = float(factory_raw.get("count", 1)) if factory_raw else 1.0

    return Recipe(
        name=raw.get("name", "unknown"),
        recipe_type=raw.get("type", ""),
        factory=factory,
        beacons=beacons,
        count=count,
    )


def parse_model(raw: dict) -> ProductionModel:
    """Parse a raw Helmod export dict into a typed ProductionModel."""
    blocks = []

    # Helmod stores blocks in a dict keyed by block id
    raw_blocks = raw.get("blocks")
    if not raw_blocks or not isinstance(raw_blocks, dict):
        # Maybe the export is a single block
        children = raw.get("children")
        if children:
            block = _parse_block("exported", raw)
            return ProductionModel(blocks=[block])
        raise ValueError("No blocks found in Helmod export")

    for _block_id, block_raw in sorted(raw_blocks.items(), key=lambda x: x[0]):
        if isinstance(block_raw, dict):
            block = _parse_block(
                block_raw.get("name", f"block_{_block_id}"), block_raw
            )
            blocks.append(block)

    return ProductionModel(blocks=blocks)


def _parse_block(name: str, raw: dict) -> Block:
    """Parse a block dict into a Block object."""
    recipes = []
    children = raw.get("children")
    if children and isinstance(children, dict):
        for _child_id, child_raw in sorted(children.items(), key=lambda x: x[0]):
            if isinstance(child_raw, dict):
                recipes.append(_parse_recipe(child_raw))
    return Block(name=name, recipes=recipes)
