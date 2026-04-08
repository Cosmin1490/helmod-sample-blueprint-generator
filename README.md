# Helmod Sample Blueprint Generator

A Factorio 2.0 mod that generates placement blueprints from [Helmod](https://mods.factorio.com/mod/helmod) production plans.

Design your production line in Helmod, open the summary panel, and click **Generate Blueprint** to get a blueprint with the correct buildings, recipes, and modules laid out on a grid — ready to stamp down.

## How it works

1. Open Helmod and view a production model's summary panel
2. Click the **Generate Blueprint** button (injected at the bottom of the panel)
3. A blueprint is placed in your cursor with all buildings, recipes, and modules from the plan
4. Stamp it down and wire things up

Building sizes are read from the game's prototype data, so spacing is correct even with large modded buildings (e.g. Pyanodon's).

## Installation

Copy or symlink the repository folder into your Factorio mods directory:

```
~/Library/Application Support/factorio/mods/    # macOS
~/.factorio/mods/                               # Linux
%APPDATA%\Factorio\mods\                        # Windows
```

Or build a zip for distribution:

```bash
./build.sh
# produces helmod-sample-blueprint-generator_0.1.0.zip
```

## Requirements

- Factorio 2.0
- [Helmod](https://mods.factorio.com/mod/helmod) >= 2.2.6

## Development

The blueprint generation logic lives in `blueprint.lua` (pure Lua, no Factorio API dependencies). `control.lua` handles GUI injection and Factorio-specific calls.

Run tests with [busted](https://lunarmodules.github.io/busted/):

```bash
busted
```

## Limitations

- **Grid layout only** — buildings are placed in rows with no belt, pipe, or inserter connections. You connect them manually after placing.
- **No beacon placement** — beacon data from Helmod is not yet included in the blueprint.
