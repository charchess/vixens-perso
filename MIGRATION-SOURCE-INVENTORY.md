# Staged monorepo source inventory

These source blocks were copied from `charchess/vixens` at commit `c6aafee2c7a6c6d90aa9b43dece229568ee13c0c` to prepare the multi-repository split.

## Safety boundary

- This repository is **not** an active Argo CD source.
- No Argo CD Application, root registration, BOM pin, promotion reference, or live Kubernetes object is changed by this staging commit.
- This copy does not move data, PVCs, PVs, database state, or secrets.
- A future live source handoff must follow the `argocd-stateful-ownership-transfer` procedure: one authority, no prune, no PVC recreation, exact render comparison, and live identity proof.

## Source blocks

- `apps/10-home`
- `apps/20-media`
- `apps/70-tools`
- `apps/40-network/contacts`
- `apps/40-network/mail-gateway`
- `apps/40-network/netbird`
- `apps/40-network/netvisor`
- `apps/60-services/docspell`
- `apps/60-services/firefly-iii`
- `apps/60-services/firefly-iii-importer`
- `apps/60-services/gluetun`
- `apps/60-services/mail`
- `apps/60-services/n8n`
- `apps/60-services/sakapuss`
- `apps/60-services/vaultwarden`

`apps/_shared` is copied as a temporary local build dependency. Its long-term ownership and any public contract extraction remain part of the orchestrator/BOM design; no cross-repository mutable import is introduced here.
