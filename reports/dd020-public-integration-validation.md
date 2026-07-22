# DD-020 public integration validation

Date: 2026-07-22 UTC

Issue #139 and PR #140 own this presentation-only milestone. It adds no
claim, run, paper, submission, or research authorization. The Lab reads only
immutable run `20260722T142551Z_DD-020_3854fff6_37c11a850a`.

## Exact data contract

- The generated public copies of `point-census.json` and
  `channel-profiles.json` are byte-identical to the immutable run outputs.
- The Lab derives 2,044 adjacent point transitions from all 2,555 census rows
  and ten transitions from all five registered channel profiles.
- Every transition satisfies exact rational
  `aggregation gain - lost rescue = net increment`.
- The canonical point row reports `0 - 1/8 = -1/8`; the guaranteed-shortlist
  row reports `1/6 - 1/8 = 1/24`.
- The half-accurate noisy point and guaranteed shortlist preserve opposite
  increment signs without implying an arbitrary-channel theorem.

## Local site and browser validation

The generated surface has 72 HTML routes, 71 public data files, 17 Labs, and
24 studies. The Incremental Sharing route preserves all 2,054 transitions in a
captioned no-JavaScript table and offers direct immutable-source downloads.

In-app browser QA over the local HTTP build verified:

- point and registered-channel modes, including the same-accuracy comparison;
- negative noisy-point and positive guaranteed-shortlist paths;
- `s=2→3` guaranteed-shortlist decomposition `1/9 - 1/12 = 1/36`;
- a terminal `M=5`, `N=8`, `p=2/5`, `s=7→8` point transition;
- one labeled native control per selector, polite live status, keyboard focus,
  and an accessible chart label;
- 390×844 document containment with wide tables scrolling inside their
  regions; and
- zero browser warnings or errors.

Authoritative repository gates and branch/post-merge workflow identifiers are
recorded in the ExecPlan and final acceptance after they complete. Before the
branch evidence commit, `git diff --check`, bootstrap, Ruff, strict MyPy over
142 source files, all 224 tests, all 96 claims, all 49 manifests, and the
72-route/24-study site build passed. Claims, immutable runs, and paper PDFs are
unchanged.

## Deployment

Push CI `29932990915`, PR CI `29932992256`, and paper/site build
`29932992268` passed. PR #140 squash-merged as `57270680`, issue #139 closed,
and post-merge CI `29933212532` plus Pages `29933212171` passed. The nine
required routes returned HTTP 200; a subsequent final-acceptance sweep found
all 171 generated public files live. The deployed point census SHA-256 is
`742ece76da5d4746772c5b9065e754b5e24012cae8c899f36d54469c6e796a59` and
the deployed channel-profile SHA-256 is
`a4f63d52f402ce14f91e469d4b425ce65a92740b31530c7da9384cc726030e3a`,
matching the immutable run exactly. Deployed desktop/mobile interaction and
console checks pass.
