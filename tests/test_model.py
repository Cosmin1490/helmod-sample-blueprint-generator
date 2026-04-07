"""Tests for model parsing."""

from helmod_generator.model import ModuleSpec, parse_model


def _make_helmod_data():
    """Create a minimal Helmod-like data structure for testing."""
    return {
        "blocks": {
            1: {
                "name": "test-block",
                "children": {
                    1: {
                        "name": "iron-gear-wheel",
                        "type": "recipe",
                        "factory": {
                            "name": "assembling-machine-3",
                            "count": 2.5,
                            "modules": {
                                "productivity-module-3": 4,
                            },
                            "module_priority": {
                                1: {"name": "productivity-module-3", "amount": 4},
                            },
                        },
                        "beacons": {
                            1: {
                                "name": "beacon",
                                "per_factory": 8,
                                "per_factory_constant": 0,
                                "modules": {
                                    "speed-module-3": 2,
                                },
                                "module_priority": {
                                    1: {"name": "speed-module-3", "amount": 2},
                                },
                            },
                        },
                    },
                    2: {
                        "name": "electronic-circuit",
                        "type": "recipe",
                        "factory": {
                            "name": "assembling-machine-2",
                            "count": 1.0,
                            "modules": {},
                        },
                        "beacons": {},
                    },
                },
            },
        },
    }


def test_parse_model_basic():
    """Should parse blocks and recipes from Helmod data."""
    raw = _make_helmod_data()
    model = parse_model(raw)

    assert len(model.blocks) == 1
    block = model.blocks[0]
    assert block.name == "test-block"
    assert len(block.recipes) == 2


def test_parse_recipe_factory():
    """Should parse factory name and building count."""
    raw = _make_helmod_data()
    model = parse_model(raw)
    recipe = model.blocks[0].recipes[0]

    assert recipe.name == "iron-gear-wheel"
    assert recipe.factory.name == "assembling-machine-3"
    assert recipe.building_count == 3  # ceil(2.5)


def test_parse_modules_from_priority():
    """Should prefer module_priority over modules dict."""
    raw = _make_helmod_data()
    model = parse_model(raw)
    recipe = model.blocks[0].recipes[0]

    assert len(recipe.factory.modules) == 1
    assert recipe.factory.modules[0] == ModuleSpec(name="productivity-module-3", count=4)


def test_parse_beacons():
    """Should parse beacon configuration."""
    raw = _make_helmod_data()
    model = parse_model(raw)
    recipe = model.blocks[0].recipes[0]

    assert len(recipe.beacons) == 1
    beacon = recipe.beacons[0]
    assert beacon.name == "beacon"
    assert beacon.per_factory == 8
    assert len(beacon.modules) == 1
    assert beacon.modules[0].name == "speed-module-3"


def test_parse_empty_modules():
    """Recipe with no modules should have empty list."""
    raw = _make_helmod_data()
    model = parse_model(raw)
    recipe = model.blocks[0].recipes[1]

    assert recipe.factory.modules == []
