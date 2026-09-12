#!/usr/bin/env bash
# Assemble target/knowledge/knowledgenet-foundation/ from the sibling knowledgenet
# repo's docs/. Only a curated subset of docs/ is included -- see the usage text
# below and tools/README.md for the full rationale.
set -euo pipefail

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
rulegen_dir=$(cd "$script_dir/.." && pwd)
default_source_docs=$(cd "$rulegen_dir/../../knowledgenet/docs" 2>/dev/null && pwd || true)
default_dest_dir="$rulegen_dir/target/knowledge/knowledgenet-foundation"

usage() {
  cat <<EOF
Usage: $(basename "$0") [-n] [-s SOURCE_DOCS_DIR] [-o DEST_DIR]

Assembles target/knowledge/knowledgenet-foundation/ from the sibling knowledgenet
repo's docs/ -- only the subset relevant to authoring rules against an
already-bootstrapped application:

  concepts.md              -> knowledgenet-foundation/concepts.md
  rules-authoring.md       -> knowledgenet-foundation/rules-authoring.md
  api/*.md (not index.md)  -> knowledgenet-foundation/api-reference/*.md

Deliberately excluded:
  rule-service.md        platform/bootstrap-framework guide (installing knowledgenet,
                          designing a fact model, wiring up the Service) -- not
                          rule-authoring. Its rule-authoring-relevant parts (Collectors,
                          EventFacts, fact hashability) are already covered by
                          rules-authoring.md's own sections.
  rule-creation.md        redundant with rules-authoring.md's Rule Structure/@ruledef
                          sections -- a shorter restatement, no new information.
  readme-development.md  contributor tooling for the knowledgenet library itself
                          (pytest, mypy, sphinx, publish) -- not relevant to rule
                          authoring.
  index.md, api/index.md navigation pages, not content.

Options:
  -s SOURCE_DOCS_DIR   knowledgenet repo's docs/ directory
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
  echo "Error: could not locate the knowledgenet repo's docs/ directory automatically. Pass -s SOURCE_DOCS_DIR." >&2
  exit 1
fi
if [[ ! -d "$source_docs" ]]; then
  echo "Error: source docs directory not found: $source_docs" >&2
  exit 1
fi

included_files=(concepts.md rules-authoring.md)
for f in "${included_files[@]}"; do
  if [[ ! -f "$source_docs/$f" ]]; then
    echo "Error: expected source file not found: $source_docs/$f" >&2
    exit 1
  fi
done

api_src="$source_docs/api"
if [[ ! -d "$api_src" ]]; then
  echo "Error: expected api/ directory not found under $source_docs" >&2
  exit 1
fi

api_files=()
while IFS= read -r -d '' f; do
  api_files+=("$f")
done < <(find "$api_src" -maxdepth 1 -name '*.md' ! -name 'index.md' -print0 | sort -z)

if [[ ${#api_files[@]} -eq 0 ]]; then
  echo "Error: no api/*.md files found under $api_src (besides index.md)" >&2
  exit 1
fi

if [[ $dry_run -eq 1 ]]; then
  echo "Would assemble into: $dest_dir"
  for f in "${included_files[@]}"; do
    echo "  $source_docs/$f -> $dest_dir/$f"
  done
  for f in "${api_files[@]}"; do
    echo "  $f -> $dest_dir/api-reference/$(basename "$f")"
  done
  exit 0
fi

rm -rf "$dest_dir"
mkdir -p "$dest_dir/api-reference"

for f in "${included_files[@]}"; do
  cp "$source_docs/$f" "$dest_dir/$f"
done

for f in "${api_files[@]}"; do
  cp "$f" "$dest_dir/api-reference/$(basename "$f")"
done

echo "Assembled knowledgenet-foundation/ at $dest_dir"
echo "  ${#included_files[@]} prose doc(s), ${#api_files[@]} api-reference file(s)"
