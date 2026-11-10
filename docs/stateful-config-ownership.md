# Stateful configuration ownership after DataAngel

This inventory is the Git ownership record for issue #21. Stateful `/config` paths use an application-scoped `storage-rwo-retain` PVC. **No migration is executed by these manifests.**

| Workload | Owner | Classification |
|---|---|---|
| amule | `amule-config-pvc` | persistent user/application state |
| bookshelf | `bookshelf-config-pvc` | persistent user/application state |
| lidarr | `lidarr-config-pvc` | persistent user/application state |
| mylar | `mylar-config-pvc` | persistent user/application state |
| prowlarr | `prowlarr-config-pvc` | persistent user/application state |
| pyload | `pyload-config-pvc` | persistent user/application state |
| qbittorrent | `qbittorrent-config-pvc` | persistent user/application state |
| radarr | `radarr-config-pvc` | persistent user/application state |
| sabnzbd | `sabnzbd-config-pvc` | persistent user/application state |
| sonarr | `sonarr-config-pvc` | persistent user/application state |
| whisparr | `whisparr-config-pvc` | persistent user/application state |
| homepage | `homepage-config-pvc` | persistent user/application state |
| frigate | existing `frigate-config-pvc` | already persistent |
| jellyfin | existing `jellyfin-config-pvc` | already persistent |
| renovate | none | explicit stateless job configuration |

## Production migration gate
1. Capture a **snapshot** and record its identity.
2. **Copy** existing config into the new PVC through an approved, one-shot migration procedure.
3. Perform **verification** against the copied content and the declared application owner.
4. Execute a reviewed **cutover**, then obtain pod-restart evidence that intended configuration persists.
5. Keep the source until acceptance; **rollback** means restoring the prior workload/storage reference using the recorded snapshot.

No destructive PVC/PV action, live Argo handoff, manual UI patch, or copy command is declared here.
