# Durable configuration ownership — issue #21

This PR is intentionally limited to the five workloads qualified by #21. Each has a retained, Git-owned PVC; BirdNET-Go keeps its existing NFS clips path and persists configuration plus `/data` through its dedicated claim.

| Workload | Claim | Durable paths |
|---|---|---|
| sabnzbd | `sabnzbd-config-pvc` | `/config` |
| radarr | `radarr-config-pvc` | `/config` |
| sonarr | `sonarr-config-pvc` | `/config` |
| prowlarr | `prowlarr-config-pvc` | `/config` |
| birdnet-go | `birdnet-go-data-pvc` | config subpath and `/data`; clips remain existing NFS |

This is declarative GitOps only: no manual UI patch, secret, runtime action, data copy, live cutover, or Argo handoff is included. Electra validates reconciliation/runtime after merge.
