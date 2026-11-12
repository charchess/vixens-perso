# NetBird Perso policy contract

This directory records the reviewed, deny-by-default intent from issue #52 and decision #49. `policy-contract.yaml` is a design contract only: it is not included by any Kustomization, is not a Kubernetes resource, and is not a NetBird API payload. It creates no peer, group membership, route, DNS record, firewall rule, account, key, or external access.

## Allow / deny matrix

| Source | Destination | Decision | Boundary |
| --- | --- | --- | --- |
| `perso-operators` | `perso-control-plane` | Allow (design intent only) | Future authenticated NetBird policy administration; no peer or subnet route is granted. |
| Any source | Any unlisted destination | Deny | Baseline deny-by-default. |
| Any source | `shared-cluster` | Deny | Explicitly excluded from Perso. |
| Any source | `talos` | Deny | Explicitly excluded from Perso. |
| Any source | `storage` | Deny | Explicitly excluded from Perso. |
| Any source | `openbao-infra` | Deny | Explicitly excluded from Perso. |
| Any source | `fabric` | Deny | Explicitly excluded from Perso. |

## Routes and identities

`routes: []` is deliberate. No CIDR/subnet route, group membership, service identity, or peer is known or approved in this Git-only change. An allow rule names the future operator-to-control-plane control path but cannot become effective until a separately reviewed management-plane implementation maps these design groups to real NetBird objects and passes the explicit runtime gate.

## Static review

Run the local contract check from the repository root:

    apps/40-network/netbird/policy/validate.sh

The check verifies the deny default, the empty route list, the baseline deny rule, the bounded control-plane allow intent, and every required exclusion. It is source-level evidence only; it does not qualify connectivity or runtime behavior.

## Rollback

Rollback is Git-only: revert the commit that introduces this directory, then let the normal review and delivery process handle any future application. Since this contract is intentionally excluded from Kustomize and is not an API payload, this PR has no runtime effect to reverse.
