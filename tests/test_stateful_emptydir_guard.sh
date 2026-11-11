#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
guard=(python3 "$root/tools/stateful_emptydir_guard.py" --kustomize "${KUSTOMIZE:-kustomize}")
fixtures="$root/tests/fixtures/stateful-emptydir"

expect_green() {
  local name=$1
  "${guard[@]}" --target "$fixtures/$name" --contract "$fixtures/$name/contract.json" >"${TMPDIR:-/tmp}/$name.json"
  grep -Fq '"status": "pass"' "${TMPDIR:-/tmp}/$name.json"
}

expect_red() {
  local name=$1
  if "${guard[@]}" --target "$fixtures/$name" --contract "$fixtures/$name/contract.json" >"${TMPDIR:-/tmp}/$name.json" 2>&1; then
    echo "expected $name to fail" >&2
    exit 1
  fi
  grep -Eq '"status": "(fail|error)"' "${TMPDIR:-/tmp}/$name.json"
}

expect_green green-pvc
expect_green green-exception
expect_red red-config
expect_red red-data
expect_red red-invalid-exception
expect_red red-invalid-created-at
expect_red red-mount-path-mismatch
expect_red red-missing-rule
expect_red red-ambiguous-rule

echo 'stateful emptyDir guard: RED and GREEN fixtures verified'
