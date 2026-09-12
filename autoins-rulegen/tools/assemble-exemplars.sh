#!/usr/bin/env bash
# Assemble target/knowledge/exemplars/ from the sibling autoins repo's rules/
# directory -- only the three rulesets rule generation is actually scoped to
# (see knowledgexpert/.plans/001-2026-09-05-deepagents-modernization-plan-INPROG.md's
# "Explicitly out of scope" section: 05_finalization is framework code, not
# generated). Straight per-file copies, phase subdirectory structure preserved,
# __pycache__ excluded.
#
# rules/ is not sourced "from src/" and doesn't need to be: rule files have no
# fully-qualified module path to preserve in the first place. knowledgenet's own
# scanner (src/knowledgenet/scanner.py, load_rules_from_filepaths/_find_modules)
# loads each rule file by bare filename via sys.path.append(dir) +
# importlib.import_module(module_name) -- never a dotted package path (the
# 02_/03_/04_-prefixed directory names aren't even valid Python identifiers).
# What matters for an exemplar -- what it imports -- is already stated inline in
# the file and travels with it regardless of where it's copied.
set -euo pipefail

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
rulegen_dir=$(cd "$script_dir/.." && pwd)
default_rules_dir=$(cd "$rulegen_dir/../autoins/rules" 2>/dev/null && pwd || true)
default_dest_dir="$rulegen_dir/target/knowledge/exemplars"

usage() {
  cat <<EOF
Usage: $(basename "$0") [-n] [-r RULES_DIR] [-o DEST_DIR]

Assembles target/knowledge/exemplars/ from the sibling autoins repo's rules/ --
only the in-scope rulesets:

  rules/02_validation/*.py  -> exemplars/02_validation/*.py
  rules/03_contract/*.py    -> exemplars/03_contract/*.py
  rules/04_fraud/*.py       -> exemplars/04_fraud/*.py

rules/05_finalization/ is deliberately excluded -- framework code (payment
computation, action selection), not something rule generation produces. Within
each included directory, __pycache__ and dunder files (__init__.py etc.) are
skipped.

Options:
  -r RULES_DIR   autoins repo's rules/ directory
                  (default: ${default_rules_dir:-<not found>})
  -o DEST_DIR     Destination directory
                  (default: $default_dest_dir)
  -n              Dry run: show what would be copied without copying.
  -h              Show this help.
EOF
}

rules_dir="$default_rules_dir"
dest_dir="$default_dest_dir"
dry_run=0

while getopts "r:o:nh" opt; do
  case "$opt" in
    r) rules_dir=$OPTARG ;;
    o) dest_dir=$OPTARG ;;
    n) dry_run=1 ;;
    h) usage; exit 0 ;;
    *) usage; exit 1 ;;
  esac
done

if [[ -z "$rules_dir" ]]; then
  echo "Error: could not locate the autoins repo's rules/ directory automatically. Pass -r RULES_DIR." >&2
  exit 1
fi
if [[ ! -d "$rules_dir" ]]; then
  echo "Error: rules directory not found: $rules_dir" >&2
  exit 1
fi

rulesets=(02_validation 03_contract 04_fraud)
for rs in "${rulesets[@]}"; do
  if [[ ! -d "$rules_dir/$rs" ]]; then
    echo "Error: expected ruleset directory not found: $rules_dir/$rs" >&2
    exit 1
  fi
done

declare -A ruleset_files=()
total=0
for rs in "${rulesets[@]}"; do
  files=()
  while IFS= read -r -d '' f; do
    files+=("$f")
  done < <(find "$rules_dir/$rs" -maxdepth 1 -name '*.py' ! -name '__*' -print0 | sort -z)
  ruleset_files[$rs]="${files[*]}"
  total=$((total + ${#files[@]}))
done

if [[ $total -eq 0 ]]; then
  echo "Error: no rule .py files found under $rules_dir/{${rulesets[*]}}" >&2
  exit 1
fi

if [[ $dry_run -eq 1 ]]; then
  echo "Would assemble into: $dest_dir"
  for rs in "${rulesets[@]}"; do
    for f in ${ruleset_files[$rs]}; do
      echo "  $f -> $dest_dir/$rs/$(basename "$f")"
    done
  done
  exit 0
fi

rm -rf "$dest_dir"
for rs in "${rulesets[@]}"; do
  mkdir -p "$dest_dir/$rs"
  for f in ${ruleset_files[$rs]}; do
    cp "$f" "$dest_dir/$rs/$(basename "$f")"
  done
done

echo "Assembled exemplars/ at $dest_dir"
echo "  $total file(s) across ${#rulesets[@]} ruleset(s)"
