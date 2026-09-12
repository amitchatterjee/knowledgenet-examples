#!/usr/bin/env bash
# Assemble target/knowledge/application-domain/ from the sibling autoins repo's
# docs/description.md. description.md was restructured (see
# knowledgexpert/.plans/001-2026-09-05-deepagents-modernization-plan-INPROG.md's
# "Knowledge-base assembly" section) to hold exactly this directory's content --
# business purpose and rulesets overview only -- so this is a straight file copy,
# not an excerpt.
set -euo pipefail

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
rulegen_dir=$(cd "$script_dir/.." && pwd)
default_source_docs=$(cd "$rulegen_dir/../autoins/docs" 2>/dev/null && pwd || true)
default_dest_dir="$rulegen_dir/target/knowledge/application-domain"

usage() {
  cat <<EOF
Usage: $(basename "$0") [-n] [-s SOURCE_DOCS_DIR] [-o DEST_DIR]

Assembles target/knowledge/application-domain/ from the sibling autoins repo's docs/:

  description.md  -> application-domain/description.md

description.md holds only business/domain content (what problem this solves, the
business purpose of each rule phase) -- not the fact model (that's
entity-relationships.md, application-architecture/'s source) and not a catalog of
current rules (that's exemplars/'s job, sourced live from autoins/rules/ so it
can't drift the way a hand-maintained list would).

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

included_files=(description.md)
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

echo "Assembled application-domain/ at $dest_dir"
echo "  ${#included_files[@]} file(s)"
