#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
EXAMPLE="${1:-$ROOT/examples/ticket}"
WORKDIR="${TMPDIR:-/tmp}/codex/typesafe-compare"
mkdir -p "$WORKDIR"
cp "$EXAMPLE/state.json" "$WORKDIR/state.json"
cp "$EXAMPLE/questions.json" "$WORKDIR/questions.json"

run_one() {
  local bin=$1
  local tag=$2
  if ! command -v "$bin" >/dev/null 2>&1; then
    echo "missing $bin" >&2
    return 1
  fi
  echo "== $bin ask =="
  "$bin" ask --state-file "$WORKDIR/state.json" --questions-file "$WORKDIR/questions.json" \
    | tee "$WORKDIR/${tag}-ask.json"
  echo "== $bin decide =="
  "$bin" decide --answers-file "$WORKDIR/${tag}-ask.json" \
    | tee "$WORKDIR/${tag}-decide.json"
}

run_one typesafe baseline || echo "skip typesafe (install typesafeai-cli for the baseline)"
run_one typesafe2 safer || echo "skip typesafe2 (pipx install -e this checkout)"

echo "wrote $WORKDIR/*-ask.json and $WORKDIR/*-decide.json"
