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

## Known bugs

### Pitch-refining block: `distilled-raw-coal` recipe not assigned

The following Helmod in-game export string produces a block where the `distilled-raw-coal` recipe (raw-coal -> coal + coal-gas + tar + iron-oxide) is not assigned. Needs investigation.

```
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
```

Partial decompression shows: model "pitch-refining", owner "cosmin1490", input raw-coal=15, intermediates coal/coke/coal-gas/tar/pitch, outputs syngas/middle-oil/creosote/anthracene-oil/hydrogen. The recipe entries section is corrupted during decompression — may need a fresh copy from the game.
