#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
EXAMPLE="${1:-$ROOT/examples/ticket}"
NAME="$(basename "$EXAMPLE")"
WORKDIR="${TMPDIR:-/tmp}/codex/typesafe-compare/$NAME"
mkdir -p "$WORKDIR"
cp "$EXAMPLE/state.json" "$WORKDIR/state.json"
cp "$EXAMPLE/questions.json" "$WORKDIR/questions.json"

run_one() {
  local bin=$1
  if ! command -v "$bin" >/dev/null 2>&1; then
    echo "missing $bin" >&2
    return 1
  fi
  echo "== $bin ask =="
  "$bin" ask --state-file "$WORKDIR/state.json" --questions-file "$WORKDIR/questions.json" \
    | tee "$WORKDIR/${bin}-ask.json"
  echo "== $bin decide =="
  "$bin" decide --answers-file "$WORKDIR/${bin}-ask.json" \
    | tee "$WORKDIR/${bin}-decide.json"
}

run_one typesafe || echo "skip typesafe (not on PATH)"
run_one typesafe2 || echo "skip typesafe2 (not on PATH)"

echo "wrote $WORKDIR"
