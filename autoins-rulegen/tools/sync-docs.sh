#!/usr/bin/env bash
# Upload files from a local folder into an S3-compatible bucket via s3cmd
# sync.
set -euo pipefail

usage() {
  cat <<EOF
Usage: $(basename "$0") [-n] SOURCE_DIR S3_DEST

  SOURCE_DIR   Local directory to upload from -- normally ../target/knowledge,
               the assembled knowledge base built by the other tools/ scripts
               (see tools/README.md), but any local folder works.
  S3_DEST      Destination, e.g. s3://knowledgexpert/autoins/knowledge. Should
               match RULEGEN_ROOT's s3:// value with /knowledge appended --
               knowledgexpert's _create_knowledge_backend() (see
               ../../../knowledgexpert/src/knowledgexpert/graph.py) derives
               the knowledge prefix from RULEGEN_ROOT the same way.

Options:
  -n           Dry run: show what would be uploaded without uploading.
  -h           Show this help.

Requires s3cmd already configured against your S3-compatible endpoint
(~/.s3cfg pointing at RustFS or equivalent) -- not yet documented in this
project.

Example:
  $(basename "$0") ../target/knowledge s3://knowledgexpert/autoins/knowledge
EOF
}

dry_run=()
while getopts "nh" opt; do
  case "$opt" in
    n) dry_run=(--dry-run) ;;
    h) usage; exit 0 ;;
    *) usage; exit 1 ;;
  esac
done
shift $((OPTIND - 1))

if [[ $# -ne 2 ]]; then
  usage
  exit 1
fi

source_dir=$1
s3_dest=$2

if ! command -v s3cmd >/dev/null 2>&1; then
  echo "Error: s3cmd not found on PATH. Install it and configure ~/.s3cfg against your S3-compatible endpoint." >&2
  exit 1
fi

if [[ ! -d "$source_dir" ]]; then
  echo "Error: source directory not found: $source_dir" >&2
  exit 1
fi

if [[ "$s3_dest" != s3://* ]]; then
  echo "Error: S3_DEST must start with s3:// (got: $s3_dest)" >&2
  exit 1
fi

# Trailing slash matters to s3cmd sync: with it on the source, the
# directory's *contents* land directly under S3_DEST; without it, the
# source directory itself becomes an extra nested prefix under S3_DEST.
# Force it on both sides so callers don't have to think about it.
s3cmd sync "${dry_run[@]}" "${source_dir%/}/" "${s3_dest%/}/"
