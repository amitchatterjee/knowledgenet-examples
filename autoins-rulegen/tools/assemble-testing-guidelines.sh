#!/usr/bin/env bash
# Assemble target/knowledge/testing-guidelines/ from the sibling autoins repo's
# docs/testing.md. Restructured 2026-09-12 (see
# knowledgexpert/.plans/001-2026-09-05-deepagents-modernization-plan-INPROG.md's
# "Knowledge-base assembly" section) to deduplicate an internally-repeated
# section, extract the general rule-config.json structure out to docs/
# configuration.md (configuration-guidelines/'s source, not this one), fix
# stale `python -m pytest` commands to `uv run pytest`, and add a note
# explaining why finalization-produced `pay` actions show up in a
# validation/contract/fraud-only test's expected.csv. So this is a straight
# file copy now, not an excerpt.
set -euo pipefail

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
rulegen_dir=$(cd "$script_dir/.." && pwd)
default_source_docs=$(cd "$rulegen_dir/../autoins/docs" 2>/dev/null && pwd || true)
default_dest_dir="$rulegen_dir/target/knowledge/testing-guidelines"

usage() {
  cat <<EOF
Usage: $(basename "$0") [-n] [-s SOURCE_DOCS_DIR] [-o DEST_DIR]

Assembles target/knowledge/testing-guidelines/ from the sibling autoins repo's docs/:

  testing.md  -> testing-guidelines/testing.md

Test artifact formats (EDI transaction format, expected.csv schema) and workflow
(the "write data -> run -> dump_result -> promote to expected" loop) -- not
rule-config.json's general structure (that's configuration-guidelines/'s source,
docs/configuration.md, extracted out of this file) and not the fact model
(application-architecture/'s source).

Options:
  -s SOURCE_DOCS_DIR   autoins repo's docs/ directory
                        (default: ${default_source_docs:-<not found>})
  -o DEST_DIR           Destination directory
                        (default: $default_dest_dir)
  -n                    Dry run: show what would be copied without copying.
  -h                    Show this help.
EOF
}

source_docs="$default_source_docs"
dest_dir="$default_dest_dir"
dry_run=0

while getopts "s:o:nh" opt; do
  case "$opt" in
    s) source_docs=$OPTARG ;;
    o) dest_dir=$OPTARG ;;
    n) dry_run=1 ;;
    h) usage; exit 0 ;;
    *) usage; exit 1 ;;
  esac
done

if [[ -z "$source_docs" ]]; then
  echo "Error: could not locate the autoins repo's docs/ directory automatically. Pass -s SOURCE_DOCS_DIR." >&2
  exit 1
fi
if [[ ! -d "$source_docs" ]]; then
  echo "Error: source docs directory not found: $source_docs" >&2
  exit 1
fi

included_files=(testing.md)
for f in "${included_files[@]}"; do
  if [[ ! -f "$source_docs/$f" ]]; then
    echo "Error: expected source file not found: $source_docs/$f" >&2
    exit 1
  fi
done

if [[ $dry_run -eq 1 ]]; then
  echo "Would assemble into: $dest_dir"
  for f in "${included_files[@]}"; do
    echo "  $source_docs/$f -> $dest_dir/$f"
  done
  exit 0
fi

rm -rf "$dest_dir"
mkdir -p "$dest_dir"

for f in "${included_files[@]}"; do
  cp "$source_docs/$f" "$dest_dir/$f"
done

echo "Assembled testing-guidelines/ at $dest_dir"
echo "  ${#included_files[@]} file(s)"
