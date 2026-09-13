#!/usr/bin/env bash
# Assemble target/knowledge/configuration-guidelines/ from the sibling autoins
# repo's docs/configuration.md -- extracted 2026-09-12 out of docs/testing.md
# (see knowledgexpert/.plans/001-2026-09-05-deepagents-modernization-plan-INPROG.md's
# "Knowledge-base assembly" section) since rule-config.json's general structure
# had no other home. Verified directly against util.py's rule_config()/
# create_action(), selection_rules.py's rank-based sort, and the real
# autoins/data/rule-config.json (including its G1 group override). Straight
# file copy, no excerpting.
set -euo pipefail

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
rulegen_dir=$(cd "$script_dir/.." && pwd)
default_source_docs=$(cd "$rulegen_dir/../autoins/docs" 2>/dev/null && pwd || true)
default_dest_dir="$rulegen_dir/target/knowledge/configuration-guidelines"

usage() {
  cat <<EOF
Usage: $(basename "$0") [-n] [-s SOURCE_DOCS_DIR] [-o DEST_DIR]

Assembles target/knowledge/configuration-guidelines/ from the sibling autoins repo's docs/:

  configuration.md  -> configuration-guidelines/configuration.md

rule-config.json's general structure and conventions (top-level ruleset keys, the
default/rules nesting, group-specific overrides, the standard per-rule fields).
Not a test's specific rule-config.json needs (that's testing-guidelines/'s job,
docs/testing.md's "rule-config.json for tests" section) and not what a spec
should state about a new rule's configuration (that's specification-guidelines/'s
Configuration section, which references this directory for the mechanical shape).

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

included_files=(configuration.md)
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

echo "Assembled configuration-guidelines/ at $dest_dir"
echo "  ${#included_files[@]} file(s)"
