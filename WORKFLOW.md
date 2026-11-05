# Workflow

## Canonical path

```text
GitHub Issue → branch → Pull Request → required CI → merge to main
```

This repository has no independent deployment or production-promotion authority. Until an approved Argo CD handoff exists, `main` is source preparation only.

## Required review questions

1. Does the change stay within this repository's responsibility?
2. Are any new platform/service requirements declared through the contract model?
3. Does it alter an active Argo CD owner, a release BOM, stateful identity, or a security boundary? If yes, stop and use the dedicated orchestration/migration issue.
4. Are all applicable CI checks green, with no unexpected skipped required job?
