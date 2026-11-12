#!/usr/bin/env sh
set -eu

policy="$(dirname "$0")/policy-contract.yaml"

test -s "$policy"
test "$(yq -r '.kind' "$policy")" = "NetBirdPersoPolicyContract"
test "$(yq -r '.spec.defaultAction' "$policy")" = "deny"
test "$(yq -r '.spec.routes | length' "$policy")" = "0"
test "$(yq -r '.spec.rules[] | select(.id == "deny-unlisted-overlay-traffic") | .action' "$policy")" = "deny"
test "$(yq -r '.spec.rules[] | select(.id == "allow-perso-operators-to-control-plane") | .action' "$policy")" = "allow"
yq -e '.spec.exclusions[] | select(.id == "shared-cluster")' "$policy" >/dev/null
yq -e '.spec.exclusions[] | select(.id == "talos")' "$policy" >/dev/null
yq -e '.spec.exclusions[] | select(.id == "storage")' "$policy" >/dev/null
yq -e '.spec.exclusions[] | select(.id == "openbao-infra")' "$policy" >/dev/null
yq -e '.spec.exclusions[] | select(.id == "fabric")' "$policy" >/dev/null
printf '%s\n' 'PASS: NetBird Perso policy contract is deny-by-default, has no subnet routes, and lists all required exclusions.'
