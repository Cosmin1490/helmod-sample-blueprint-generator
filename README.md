# helmod-generator

Generate Factorio blueprints from [Helmod](https://mods.factorio.com/mod/helmod) production line exports.

Design your production line in Helmod, export it, and run this tool to get a blueprint string you can import directly into Factorio — with the correct buildings, recipes, and modules already assigned.

Built for **Factorio 2.0** and particularly useful with complex modpacks like **Pyanodon's**.

## How it works

1. Design a production line in Helmod in-game
2. Use Helmod's "Download" or "Copy to clipboard" to export it
3. Run `helmod-generator` on the export string
4. Paste the resulting blueprint string into Factorio

The tool places buildings on a simple grid layout (no belt/pipe connections). Each building gets the correct recipe and modules assigned. You wire things up manually after placing the blueprint.

## Installation

Requires Python 3.10+.

```bash
git clone https://github.com/your-user/helmod-generator.git
cd helmod-generator
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Usage

```bash
# From clipboard (copy the export in Helmod first)
helmod-generator --clipboard

# From a file
helmod-generator --file export.txt

# Directly as an argument
helmod-generator "0eNq..."

# Copy the output blueprint straight to clipboard
helmod-generator --clipboard --copy
```

### Options

| Flag | Description |
|------|-------------|
| `--clipboard`, `-c` | Read Helmod export from clipboard |
| `--file`, `-f` | Read Helmod export from a file |
| `--copy` | Copy output blueprint to clipboard |
| `--grid-spacing`, `-g` | Distance between buildings (default: 12) |
| `--per-row`, `-r` | Buildings per row before wrapping (default: 10) |
| `--label`, `-l` | Set a label on the blueprint |
| `--verbose`, `-v` | Print a summary of the parsed production line |
| `--json`, `-j` | Output raw blueprint JSON instead of encoded string |
| `--raw` | Output raw decoded Helmod data (for debugging) |
| `--decode-blueprint` | Decode an existing Factorio blueprint string to JSON |

### Examples

See what Helmod exported before generating:

```bash
helmod-generator --clipboard --verbose
```

```
Block 0: petroleum-processing
  3x oil-refinery -> advanced-oil-processing [4x productivity-module-3]
  1x chemical-plant -> solid-fuel-from-light-oil [3x productivity-module-3]

0eNq...
```

Adjust layout for larger buildings:

```bash
helmod-generator --clipboard --grid-spacing 8 --per-row 6
```

Inspect an existing Factorio blueprint:

```bash
helmod-generator --decode-blueprint "0eNq..." | python3 -m json.tool
```

## Development

```bash
pip install -e ".[dev]"
pytest
```

## Limitations

- **Grid layout only** — buildings are placed in rows with no belt, pipe, or inserter connections. You connect them manually after importing.
- **No beacon placement** — beacon data is parsed but not placed in the blueprint yet.
- **Helmod format compatibility** — the decoder handles standard `serpent.dump` Lua serialization. If you encounter a parsing error with your export, open an issue with the export string.
