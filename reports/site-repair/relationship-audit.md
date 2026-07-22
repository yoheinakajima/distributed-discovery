# Relationship registry audit

Date: 2026-07-22. Source: `site/content/relations.yml`. Generated public artifact: `site/dist/data/relations.json`.

## Validated entity coverage

| Entity | Count |
| --- | ---: |
| Programs | 5 |
| Theorem families | 9 |
| Studies | 24 |
| Findings | 10 |
| Labs | 16 |
| Papers | 6 |
| Benchmark tasks | 24 |
| Experiment modules | 6 |
| Claims | 96 |
| Claim-linked passing runs | 36 |
| Public data routes | 20 |

## Validation rules exercised

- The configured study set exactly equals the 24 public study records.
- Every result belongs to the study declared by the Findings registry.
- Every claim exists and retains its ledger study owner.
- Every run exists among passing immutable manifests; legitimate cross-study evidence references are retained.
- Every Lab, paper, experiment, benchmark fragment, and public-data route exists.
- Benchmark task ownership is derived from its reference claims; DD-010 remains the benchmark owner.
- Relation lists reject duplicate values, local paths, parent traversal, and unregistered entities.
- No claim statement or exact scientific value is duplicated in the presentation registry.

## Reverse-link coverage

- 24/24 study pages render “Where this work appears,” program/family context, and related artifacts.
- 16/16 canonical Labs link studies, findings where present, papers where present, claims, runs, and data. The preserved `labs/audience.html` alias receives the same generated panel.
- 6/6 paper pages render studies used, claims, interactive Labs, findings, and build provenance.
- 24/24 benchmark task anchors link their supporting studies and claims.
- All six Experiment Kit modules receive generated supporting-study context from DD-011 and the applicable Program V3/V4 studies.
- 10/10 findings link their study and claims; available Lab, paper, and data links are rendered from the result registry.

Result: pass. The registry contains no dangling entity, route, claim, run, or data reference.
