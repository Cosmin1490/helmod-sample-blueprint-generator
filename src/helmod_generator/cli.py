"""Command-line interface for helmod-generator."""

import argparse
import json
import subprocess
import sys

from .blueprint import generate_blueprint
from .decode import decode_helmod_string
from .encode import decode_blueprint_string, encode_blueprint_string
from .model import parse_model


def _read_clipboard() -> str:
    """Read text from the system clipboard (macOS pbpaste)."""
    try:
        result = subprocess.run(
            ["pbpaste"], capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except FileNotFoundError:
        # Try xclip for Linux
        try:
            result = subprocess.run(
                ["xclip", "-selection", "clipboard", "-o"],
                capture_output=True, text=True, check=True,
            )
            return result.stdout.strip()
        except FileNotFoundError:
            print("Error: No clipboard tool found (pbpaste or xclip)", file=sys.stderr)
            sys.exit(1)


def _copy_to_clipboard(text: str) -> bool:
    """Copy text to the system clipboard. Returns True on success."""
    try:
        subprocess.run(["pbcopy"], input=text, text=True, check=True)
        return True
    except FileNotFoundError:
        try:
            subprocess.run(
                ["xclip", "-selection", "clipboard"],
                input=text, text=True, check=True,
            )
            return True
        except FileNotFoundError:
            return False


def main():
    parser = argparse.ArgumentParser(
        prog="helmod-generator",
        description="Generate Factorio blueprints from Helmod production line exports.",
    )

    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument(
        "export_string",
        nargs="?",
        help="Helmod export string (base64-encoded)",
    )
    input_group.add_argument(
        "--file", "-f",
        type=str,
        help="Read Helmod export from a file",
    )
    input_group.add_argument(
        "--clipboard", "-c",
        action="store_true",
        help="Read Helmod export from clipboard",
    )
    input_group.add_argument(
        "--decode-blueprint",
        type=str,
        metavar="BLUEPRINT",
        help="Decode an existing Factorio blueprint string to JSON (debug tool)",
    )

    parser.add_argument(
        "--grid-spacing", "-g",
        type=int,
        default=12,
        help="Grid spacing between buildings (default: 12)",
    )
    parser.add_argument(
        "--per-row", "-r",
        type=int,
        default=10,
        help="Max buildings per row (default: 10)",
    )
    parser.add_argument(
        "--label", "-l",
        type=str,
        default=None,
        help="Blueprint label",
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output raw blueprint JSON instead of encoded string",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print parsed model summary",
    )
    parser.add_argument(
        "--copy",
        action="store_true",
        help="Copy output to clipboard",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Print raw decoded Helmod data (debug tool)",
    )

    args = parser.parse_args()

    # Handle --decode-blueprint (debug utility)
    if args.decode_blueprint:
        bp = decode_blueprint_string(args.decode_blueprint)
        print(json.dumps(bp, indent=2))
        return

    # Get input string
    if args.clipboard:
        export_string = _read_clipboard()
    elif args.file:
        with open(args.file) as f:
            export_string = f.read().strip()
    elif args.export_string:
        export_string = args.export_string
    else:
        parser.print_help()
        sys.exit(1)

    # Decode Helmod export
    try:
        raw = decode_helmod_string(export_string)
    except Exception as e:
        print(f"Error decoding Helmod export: {e}", file=sys.stderr)
        sys.exit(1)

    if args.raw:
        print(json.dumps(raw, indent=2, default=str))
        return

    # Parse model
    try:
        model = parse_model(raw)
    except Exception as e:
        print(f"Error parsing production model: {e}", file=sys.stderr)
        sys.exit(1)

    if args.verbose:
        _print_model_summary(model)

    # Generate blueprint
    blueprint = generate_blueprint(
        model,
        grid_spacing=args.grid_spacing,
        per_row=args.per_row,
        label=args.label,
    )

    if args.json:
        output = json.dumps(blueprint, indent=2)
    else:
        output = encode_blueprint_string(blueprint)

    print(output)

    if args.copy:
        if _copy_to_clipboard(output):
            print("(copied to clipboard)", file=sys.stderr)
        else:
            print("(could not copy to clipboard)", file=sys.stderr)


def _print_model_summary(model):
    """Print a human-readable summary of the parsed model."""
    for i, block in enumerate(model.blocks):
        print(f"Block {i}: {block.name}", file=sys.stderr)
        for recipe in block.recipes:
            mods = ", ".join(f"{m.count}x {m.name}" for m in recipe.factory.modules)
            mod_str = f" [{mods}]" if mods else ""
            print(
                f"  {recipe.building_count}x {recipe.factory.name}"
                f" -> {recipe.name}{mod_str}",
                file=sys.stderr,
            )
        print(file=sys.stderr)


if __name__ == "__main__":
    main()
