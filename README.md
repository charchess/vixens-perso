# vixens-perso

Personal applications consuming Vixens Core and Infra contracts.

## Bootstrap status

This repository is a **no-cutover bootstrap**. It is not an active Argo CD source and contains no copied production manifests, credentials or runtime state.

## Non-goals

Cluster primitives, shared service lifecycle, TXO Fabric product work and platform-wide promotion logic.

## CI scope

Targeted YAML, Kustomize and application configuration checks. It must not run unrelated Fabric/controller suites.

## Delivery model

Changes follow Issue → branch → PR → required CI → merge. The retained `charchess/vixens` repository remains the future multi-repository GitOps orchestrator and release/BOM authority.
