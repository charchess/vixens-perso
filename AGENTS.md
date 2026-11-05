# AGENTS.md

`WORKFLOW.md` is authoritative. This repository contains desired-state and CI source only; do not apply persistent Kubernetes changes directly.

- Read the linked issue and current `main` before modifying files.
- Use a scoped branch and PR; never push directly to `main`.
- Do not add plaintext credentials, kubeconfigs, Terraform state, or generated secret values.
- Do not introduce an Argo CD Application source or production promotion without an explicitly approved migration issue and orchestrator BOM change.
- A passing repository check is not proof of cross-repository compatibility or physical platform health.
