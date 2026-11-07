# Workflow

## Canonical path

```text
GitHub Issue → branch → Pull Request → required CI → merge to main
→ immutable dev-v candidate → physical acceptance → explicit promotion
→ immutable prod-v release → local prod-stable pointer
```

This repository owns its **local release tags only**. A successful `main`
validation creates an immutable `dev-vYYYY.MM.*` candidate and updates the
mutable `dev-latest` pointer. Production promotion is an explicit human
`workflow_dispatch` for one exact candidate; it verifies candidate provenance,
the successful validation of that exact commit, and `main` ancestry before it
creates an immutable `prod-vYYYY.MM.*` tag and moves only this repository's
`prod-stable` pointer.

The release workflow neither creates an Argo CD Application nor changes an
existing Application source, environment, credential, stateful identity, or
security boundary. A root-registration/Argo handoff and the required physical
acceptance remain separately reviewed work.

## Required review questions

1. Does the change stay within this repository's responsibility?
2. Are any new platform/service requirements declared through the contract model?
3. Does it alter an active Argo CD owner, a release BOM, stateful identity, or a security boundary? If yes, stop and use the dedicated orchestration/migration issue.
4. Are all applicable CI checks green, with no unexpected skipped required job?
