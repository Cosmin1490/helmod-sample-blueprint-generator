#!/usr/bin/env bash
set -euo pipefail

# Read mod name and version from info.json
NAME=$(python3 -c "import json; print(json.load(open('info.json'))['name'])")
VERSION=$(python3 -c "import json; print(json.load(open('info.json'))['version'])")
PREFIX="${NAME}_${VERSION}"
OUTPUT="${PREFIX}.zip"

rm -f "$OUTPUT"

# Factorio expects the zip to contain a top-level folder named name_version
tmpdir=$(mktemp -d)
trap 'rm -rf "$tmpdir"' EXIT

mkdir "$tmpdir/$PREFIX"
cp info.json control.lua blueprint.lua "$tmpdir/$PREFIX/"
cp -r locale "$tmpdir/$PREFIX/"

(cd "$tmpdir" && zip -r - "$PREFIX") > "$OUTPUT"

echo "Built $OUTPUT"
