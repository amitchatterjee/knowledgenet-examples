#!/usr/bin/env bash
# Orchestrates all seven per-directory assemble-*.sh scripts to build a
# complete target/knowledge/ from scratch: clears it entirely, then
# repopulates every directory (six generated + one hand-authored copy).
#
# Requires KNOWLEDGENET_HOME (knowledgenet repo root) and KNOWLEDGENET_EX_HOME
# (knowledgenet-examples repo root, per that repo's own CLAUDE.md convention)
# already set in the environment -- no defaults, fails loud if either is
# missing, matching this project's convention elsewhere (e.g. RULEGEN_ROOT).
set -euo pipefail

usage() {
  cat <<EOF
Usage: $(basename "$0") [-n]

Clears \$KNOWLEDGENET_EX_HOME/autoins-rulegen/target/knowledge/ and rebuilds it
by running every assemble-*.sh script in this directory:

  knowledgenet-foundation, application-domain, application-architecture,
  exemplars, testing-guidelines, configuration-guidelines (all generated from
  \$KNOWLEDGENET_HOME / \$KNOWLEDGENET_EX_HOME/autoins), plus
  specification-guidelines (hand-authored, copied from ../knowledge/).

Requires KNOWLEDGENET_HOME and KNOWLEDGENET_EX_HOME to already be set.

Options:
  -n   Dry run: pass -n through to every sub-script, and skip clearing
       target/knowledge/ (show what would happen without changing anything).
  -h   Show this help.
EOF
}

dry_run=0
while getopts "nh" opt; do
  case "$opt" in
    n) dry_run=1 ;;
    h) usage; exit 0 ;;
    *) usage; exit 1 ;;
  esac
done

: "${KNOWLEDGENET_HOME:?Error: KNOWLEDGENET_HOME is not set -- point it at the knowledgenet repo root.}"
: "${KNOWLEDGENET_EX_HOME:?Error: KNOWLEDGENET_EX_HOME is not set -- point it at the knowledgenet-examples repo root.}"

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
rulegen_dir="$KNOWLEDGENET_EX_HOME/autoins-rulegen"
autoins_dir="$KNOWLEDGENET_EX_HOME/autoins"
knowledge_dir="$rulegen_dir/target/knowledge"

if [[ ! -d "$rulegen_dir" ]]; then
  echo "Error: autoins-rulegen/ not found under KNOWLEDGENET_EX_HOME ($KNOWLEDGENET_EX_HOME)" >&2
  exit 1
fi
if [[ ! -d "$autoins_dir" ]]; then
  echo "Error: autoins/ not found under KNOWLEDGENET_EX_HOME ($KNOWLEDGENET_EX_HOME)" >&2
  exit 1
fi
if [[ ! -d "$KNOWLEDGENET_HOME" ]]; then
  echo "Error: KNOWLEDGENET_HOME directory not found: $KNOWLEDGENET_HOME" >&2
  exit 1
fi

dry_flag=()
if [[ $dry_run -eq 1 ]]; then
  dry_flag=(-n)
  echo "Dry run -- target/knowledge/ will not be cleared, sub-scripts run with -n."
else
  echo "Clearing $knowledge_dir"
  rm -rf "$knowledge_dir"
  mkdir -p "$knowledge_dir"
fi

echo "==> knowledgenet-foundation"
"$script_dir/assemble-knowledgenet-foundation.sh" "${dry_flag[@]}" \
  -s "$KNOWLEDGENET_HOME/docs" \
  -o "$knowledge_dir/knowledgenet-foundation"

echo "==> application-domain"
"$script_dir/assemble-application-domain.sh" "${dry_flag[@]}" \
  -s "$autoins_dir/docs" \
  -o "$knowledge_dir/application-domain"

echo "==> application-architecture"
"$script_dir/assemble-application-architecture.sh" "${dry_flag[@]}" \
  -d "$autoins_dir/docs" \
  -c "$autoins_dir/src/autoins" \
  -o "$knowledge_dir/application-architecture"

echo "==> exemplars"
"$script_dir/assemble-exemplars.sh" "${dry_flag[@]}" \
  -r "$autoins_dir/rules" \
  -o "$knowledge_dir/exemplars"

echo "==> testing-guidelines"
"$script_dir/assemble-testing-guidelines.sh" "${dry_flag[@]}" \
  -s "$autoins_dir/docs" \
  -o "$knowledge_dir/testing-guidelines"

echo "==> configuration-guidelines"
"$script_dir/assemble-configuration-guidelines.sh" "${dry_flag[@]}" \
  -s "$autoins_dir/docs" \
  -o "$knowledge_dir/configuration-guidelines"

echo "==> specification-guidelines"
"$script_dir/assemble-specification-guidelines.sh" "${dry_flag[@]}" \
  -s "$rulegen_dir/knowledge/specification-guidelines" \
  -o "$knowledge_dir/specification-guidelines"

if [[ $dry_run -eq 0 ]]; then
  echo
  echo "target/knowledge/ assembled at $knowledge_dir"
  find "$knowledge_dir" -type f | sort
fi
