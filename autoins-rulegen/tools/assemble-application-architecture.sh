#!/usr/bin/env bash
# Assemble target/knowledge/application-architecture/ from the sibling autoins
# repo's docs/entity-relationships.md and three real source files under
# src/autoins/. Straight file copies -- entities.py/fact_io.py/util.py are real
# application code and are deliberately NOT restructured/cleaned for this (see
# knowledgexpert/.plans/001-2026-09-05-deepagents-modernization-plan-INPROG.md's
# "Knowledge-base assembly" section); edi_parser.py and bluebook.py are
# excluded -- see that plan's "Explicitly out of scope" section for why
# (parsing internals a rule author doesn't touch, and finalization-only
# pricing lookup, respectively -- finalization is framework code, out of
# scope for rule generation).
set -euo pipefail

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
rulegen_dir=$(cd "$script_dir/.." && pwd)
default_docs_dir=$(cd "$rulegen_dir/../autoins/docs" 2>/dev/null && pwd || true)
default_src_dir=$(cd "$rulegen_dir/../autoins/src/autoins" 2>/dev/null && pwd || true)
default_dest_dir="$rulegen_dir/target/knowledge/application-architecture"

usage() {
  cat <<EOF
Usage: $(basename "$0") [-n] [-d DOCS_DIR] [-c CODE_DIR] [-o DEST_DIR]

Assembles target/knowledge/application-architecture/ from the sibling autoins repo:

  docs/entity-relationships.md  -> application-architecture/entity-relationships.md
  src/autoins/entities.py       -> application-architecture/entities.py
  src/autoins/fact_io.py        -> application-architecture/fact_io.py
  src/autoins/util.py           -> application-architecture/util.py

entity-relationships.md is business-meaning framing + cardinalities. entities.py is
the Pydantic fact model -- ground truth for exact field names/types. fact_io.py shows
how rule-config.json/EDI/CSV become FactSet facts (the Wrapper per-ruleset-config and
per-claim Action Collector wiring). util.py has the rule-author helper conventions
every rule uses instead of reinventing (execute()/rule_config()/create_action()).

Deliberately excluded: edi_parser.py (EDI parsing internals, not rule-author-facing)
and bluebook.py (used only by 05_finalization's payment computation, which is
framework code -- rule generation is scoped to 02_validation/03_contract/04_fraud
only).

Options:
  -d DOCS_DIR   autoins repo's docs/ directory
                (default: ${default_docs_dir:-<not found>})
  -c CODE_DIR   autoins repo's src/autoins/ directory
                (default: ${default_src_dir:-<not found>})
  -o DEST_DIR    Destination directory
                (default: $default_dest_dir)
  -n             Dry run: show what would be copied without copying.
  -h             Show this help.
EOF
}

docs_dir="$default_docs_dir"
src_dir="$default_src_dir"
dest_dir="$default_dest_dir"
dry_run=0

while getopts "d:c:o:nh" opt; do
  case "$opt" in
    d) docs_dir=$OPTARG ;;
    c) src_dir=$OPTARG ;;
    o) dest_dir=$OPTARG ;;
    n) dry_run=1 ;;
    h) usage; exit 0 ;;
    *) usage; exit 1 ;;
  esac
done

if [[ -z "$docs_dir" ]]; then
  echo "Error: could not locate the autoins repo's docs/ directory automatically. Pass -d DOCS_DIR." >&2
  exit 1
fi
if [[ ! -d "$docs_dir" ]]; then
  echo "Error: docs directory not found: $docs_dir" >&2
  exit 1
fi
if [[ -z "$src_dir" ]]; then
  echo "Error: could not locate the autoins repo's src/autoins/ directory automatically. Pass -c CODE_DIR." >&2
  exit 1
fi
if [[ ! -d "$src_dir" ]]; then
  echo "Error: source code directory not found: $src_dir" >&2
  exit 1
fi

doc_files=(entity-relationships.md)
for f in "${doc_files[@]}"; do
  if [[ ! -f "$docs_dir/$f" ]]; then
    echo "Error: expected doc file not found: $docs_dir/$f" >&2
    exit 1
  fi
done

code_files=(entities.py fact_io.py util.py)
for f in "${code_files[@]}"; do
  if [[ ! -f "$src_dir/$f" ]]; then
    echo "Error: expected source file not found: $src_dir/$f" >&2
    exit 1
  fi
done

if [[ $dry_run -eq 1 ]]; then
  echo "Would assemble into: $dest_dir"
  for f in "${doc_files[@]}"; do
    echo "  $docs_dir/$f -> $dest_dir/$f"
  done
  for f in "${code_files[@]}"; do
    echo "  $src_dir/$f -> $dest_dir/$f"
  done
  exit 0
fi

rm -rf "$dest_dir"
mkdir -p "$dest_dir"

for f in "${doc_files[@]}"; do
  cp "$docs_dir/$f" "$dest_dir/$f"
done
for f in "${code_files[@]}"; do
  cp "$src_dir/$f" "$dest_dir/$f"
done

echo "Assembled application-architecture/ at $dest_dir"
echo "  $((${#doc_files[@]} + ${#code_files[@]})) file(s)"
