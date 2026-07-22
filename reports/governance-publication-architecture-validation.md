# Governance and publication architecture validation

Validated at `2026-07-22T14:05:15Z` on branch
`docs/research-governance-publication-architecture` for issue #133 and draft PR
#134.

## Scope audit

This milestone changes documentation, synthesis maps, presentation-only site
source, and site tests. It creates no registered study, scientific claim,
immutable run, exact research output, or paper PDF. The only changed path under
`src/distributed_discovery` is the site builder and navigation module; the only
changed path under `studies` is the registry prose in `studies/index.md`.

| Inventory | Observed |
| --- | ---: |
| Claims | 91 |
| Manifests | 48 |
| Passing runs | 45 |
| Studies | 23 |
| Validated papers | 6 |
| Public HTML routes | 70 |
| Public data files | 67 |
| Labs | 16 |
| Checksum-registered downloads | 22 |

The claim-ledger SHA-256 remains
`b2fae6de4ef6399d6067ac6101d0cde7186c39ed2a02f047dfce289e16271b2d`.
The sorted manifest-file checksum digest remains
`542024e900d5d31c8d3da99f77b603789ee4c3b29f1c383219935b055beba70a`.
No path under `claims/` or `results/` changed, and no PDF path changed.

The six validated public-paper checksums remain:

- Common-Source Trap: `c997bba31c021bd799f2b3a561e8e558a1334f844aa87a448ade10319dac2ad3`
- Discovery Institutions: `9bad1e7aaebd07851613f7f38a5c1a3654ca78363cc95f092f5b97bf0f9cee7b`
- Foundations: `e096183159f8c016f116b1a97fc0721948bbee2aca6dd1ae251d0a2af95a32e4`
- Incentive to Ignore: `ee9e27f741d25a9597994f18caf2bf406098db7aca4d2ed067a7a011f64be250`
- Three Results: `8ea2afc82a4a9c759774e506fe857363cc4f71677ab707ca246ef5fabf1e5f8e`
- Threshold Discovery: `b38bb30f3ce63889526a092d78dd3f202d3beb54178bcdc272aba85c321b1995`

## Commands and observations

- `git diff --check`: passed.
- YAML parse checks for the paper-family and synthesis maps: passed.
- Targeted site presentation and integration tests: 13 passed in 5.07 seconds
  through the repository source-path environment.
- `make bootstrap`: passed 11 required-file checks and the claim fixture.
- `make verify`: Ruff formatting/lint passed, MyPy passed on 138 source files,
  all 217 tests passed, 91 claims validated, and all 48 manifests validated.
- `make site`: passed with 70 pages and 23 studies.

The earlier direct non-editable targeted-test cache failure is recorded in the
Master ExecPlan; it created no evidence and was not treated as acceptance.
