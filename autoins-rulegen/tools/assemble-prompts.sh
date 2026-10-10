#!/usr/bin/env bash
# Assemble target/prompts/ from this repo's own hand-authored ../prompts/ --
# like assemble-specification-guidelines.sh, the source isn't another repo's
# docs/code needing selection or restructuring, it's already curated content.
# Copies the whole directory as-is (whatever files are there), not a fixed
# file list.
#
# Why this exists: RULEGEN_ROOT (see knowledgexpert's graph.py) derives both
# `knowledge/` and `prompts/` as fixed subpaths beneath one root. The
# assembled knowledge base only exists under target/knowledge/ (six generated
# dirs plus the hand-authored specification-guidelines/ copy) -- prompts/
# needs the same treatment so a single RULEGEN_ROOT (target/) resolves both.
set -euo pipefail

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
rulegen_dir=$(cd "$script_dir/.." && pwd)
default_source_dir="$rulegen_dir/prompts"
default_dest_dir="$rulegen_dir/target/prompts"

usage() {
  cat <<EOF
Usage: $(basename "$0") [-n] [-s SOURCE_DIR] [-o DEST_DIR]

Copies ../prompts/ (hand-authored, this repo) into target/prompts/ as-is.

Options:
  -s SOURCE_DIR   Hand-authored prompts/ directory
                   (default: $default_source_dir)
  -o DEST_DIR      Destination directory
                   (default: $default_dest_dir)
  -n               Dry run: show what would be copied without copying.
  -h               Show this help.
EOF
}

source_dir="$default_source_dir"
dest_dir="$default_dest_dir"
dry_run=0

while getopts "s:o:nh" opt; do
  case "$opt" in
    s) source_dir=$OPTARG ;;
    o) dest_dir=$OPTARG ;;
    n) dry_run=1 ;;
    h) usage; exit 0 ;;
    *) usage; exit 1 ;;
  esac
done

if [[ ! -d "$source_dir" ]]; then
  echo "Error: source directory not found: $source_dir" >&2
  exit 1
fi

files=()
while IFS= read -r -d '' f; do
  files+=("$f")
done < <(find "$source_dir" -type f -print0 | sort -z)

if [[ ${#files[@]} -eq 0 ]]; then
  echo "Error: no files found under $source_dir" >&2
  exit 1
fi

if [[ $dry_run -eq 1 ]]; then
  echo "Would assemble into: $dest_dir"
  for f in "${files[@]}"; do
    rel="${f#"$source_dir"/}"
    echo "  $f -> $dest_dir/$rel"
  done
  exit 0
fi

rm -rf "$dest_dir"
mkdir -p "$dest_dir"
cp -r "$source_dir"/. "$dest_dir"/

echo "Assembled prompts/ at $dest_dir"
echo "  ${#files[@]} file(s)"
