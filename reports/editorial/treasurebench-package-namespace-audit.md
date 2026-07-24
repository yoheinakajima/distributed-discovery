# TreasureBench package and namespace audit

Audit date: 2026-07-23 PDT.

This file records transient public observations. It performs no reservation,
registration, purchase, publication, or legal clearance.

| Namespace | Observed state | Owner action |
|---|---|---|
| PyPI `treasurebench` | project JSON endpoint returned HTTP 404 | reserve through an owner-controlled account if desired before standalone packaging |
| npm `treasurebench` | registry endpoint returned HTTP 404 | reserve through an owner-controlled account if desired |
| GitHub `TreasureBench` repositories | connected repository search returned zero results | decide repository/organization/name reservation |
| GitHub `treasurebench` users | public user search returned zero results | optional only; no account was created |
| Hugging Face models/datasets/Spaces | exact search returned empty lists | decide namespace or collection reservation |
| `treasurebench.com` | RDAP object not found | optional owner purchase decision |
| `treasurebench.org` | RDAP object not found | optional owner purchase decision |
| `treasurebench.ai` | RDAP object not found | optional owner purchase decision |
| `treasurebench.dev` | RDAP object not found | optional owner purchase decision |
| USPTO/EUIPO | no exact indexed result in bounded official-domain search | perform a one-time owner-controlled preliminary register scan before first DOI or package publication |

All observations can change without notice. A 404 or empty result is not a
reservation, guarantee, ownership right, or legal conclusion. The root Python
distribution remains `distributed-discovery`; this milestone does not publish
a standalone `treasurebench` package.
