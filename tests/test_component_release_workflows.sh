#!/usr/bin/env bash
set -euo pipefail

candidate=.github/workflows/auto-tag-dev.yaml
promotion=.github/workflows/promote-prod.yaml

test -f "$candidate"
test -f "$promotion"

# Candidates may only be minted from a successful main validation workflow.
grep -Fq 'workflow_run:' "$candidate"
grep -Fq 'workflows: ["Validate & Security"]' "$candidate"
grep -Fq "github.event.workflow_run.conclusion == 'success'" "$candidate"
grep -Fq "github.event.workflow_run.head_branch == 'main'" "$candidate"
grep -Fq 'dev-v${version}' "$candidate"
grep -Fq 'refs/tags/dev-latest' "$candidate"

# Production is manual, exact, locally scoped, and traceably verified.
grep -Fq 'workflow_dispatch:' "$promotion"
grep -Fq 'actions: read' "$promotion"
grep -Fq 'contents: write' "$promotion"
grep -Fq 'dev-v${version}' "$promotion"
grep -Fq 'prod-v${version}' "$promotion"
grep -Fq 'merge-base --is-ancestor' "$promotion"
grep -Fq 'actions/workflows/validate.yaml/runs?head_sha=' "$promotion"
grep -Fq 'refs/tags/prod-stable' "$promotion"
grep -Fq "git rev-parse 'prod-stable^{commit}'" "$promotion"

# The release channel must remain repository-local.
if grep -Eq 'https://github\.com/charchess/(vixens-core|vixens-infra|vixens-fabric)(\.git)?' "$candidate" "$promotion"; then
  echo 'cross-repository release authority is forbidden' >&2
  exit 1
fi
