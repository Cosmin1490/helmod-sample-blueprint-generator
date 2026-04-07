"""Tests for blueprint generation."""

from helmod_generator.blueprint import generate_blueprint
from helmod_generator.model import (
    Block,
    Factory,
    ModuleSpec,
    ProductionModel,
    Recipe,
)


def _make_model():
    return ProductionModel(
        blocks=[
            Block(
                name="test",
                recipes=[
                    Recipe(
                        name="iron-gear-wheel",
                        recipe_type="recipe",
                        factory=Factory(
                            name="assembling-machine-3",
                            modules=[ModuleSpec("productivity-module-3", 4)],
                        ),
                        count=3.0,
                    ),
                    Recipe(
                        name="electronic-circuit",
                        recipe_type="recipe",
                        factory=Factory(name="assembling-machine-2", modules=[]),
                        count=1.0,
                    ),
                ],
            )
        ]
    )


def test_entity_count():
    """Should create correct number of entities."""
    model = _make_model()
    bp = generate_blueprint(model)
    entities = bp["blueprint"]["entities"]
    # 3 assemblers for gears + 1 for circuits = 4
    assert len(entities) == 4


def test_entity_numbers_sequential():
    """Entity numbers should be 1-indexed and sequential."""
    model = _make_model()
    bp = generate_blueprint(model)
    entities = bp["blueprint"]["entities"]
    numbers = [e["entity_number"] for e in entities]
    assert numbers == [1, 2, 3, 4]


def test_entity_recipe():
    """Each entity should have the correct recipe."""
    model = _make_model()
    bp = generate_blueprint(model)
    entities = bp["blueprint"]["entities"]
    assert all(e["recipe"] == "iron-gear-wheel" for e in entities[:3])
    assert entities[3]["recipe"] == "electronic-circuit"


def test_entity_modules():
    """Entities with modules should have items array."""
    model = _make_model()
    bp = generate_blueprint(model)
    entities = bp["blueprint"]["entities"]

    # First entity should have 4 prod modules
    items = entities[0]["items"]
    assert len(items) == 4
    assert all(i["item"]["name"] == "productivity-module-3" for i in items)

    # Last entity has no modules
    assert "items" not in entities[3]


def test_grid_layout():
    """Buildings should be placed on a grid with correct spacing."""
    model = _make_model()
    bp = generate_blueprint(model, grid_spacing=6, per_row=10)
    entities = bp["blueprint"]["entities"]

    # First 3 entities (gear recipe) should be in a row
    for i in range(3):
        assert entities[i]["position"]["x"] == i * 6 + 3
        assert entities[i]["position"]["y"] == 0 * 6 + 3

    # 4th entity (circuit recipe) should be on next row
    assert entities[3]["position"]["x"] == 0 * 6 + 3
    assert entities[3]["position"]["y"] == 1 * 6 + 3


def test_row_wrapping():
    """Buildings should wrap to next row after per_row."""
    model = ProductionModel(
        blocks=[
            Block(
                name="test",
                recipes=[
                    Recipe(
                        name="test-recipe",
                        recipe_type="recipe",
                        factory=Factory(name="assembler", modules=[]),
                        count=5.0,
                    ),
                ],
            )
        ]
    )
    bp = generate_blueprint(model, grid_spacing=6, per_row=3)
    entities = bp["blueprint"]["entities"]

    # 5 entities: 3 on row 0, 2 on row 1
    assert entities[0]["position"]["y"] == 3  # row 0
    assert entities[2]["position"]["y"] == 3  # row 0
    assert entities[3]["position"]["y"] == 9  # row 1


def test_blueprint_structure():
    """Output should be valid blueprint structure."""
    model = _make_model()
    bp = generate_blueprint(model)
    assert "blueprint" in bp
    assert bp["blueprint"]["item"] == "blueprint"
    assert "version" in bp["blueprint"]
    assert "entities" in bp["blueprint"]
