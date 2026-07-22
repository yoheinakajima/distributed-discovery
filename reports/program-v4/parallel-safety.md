# Program V4 parallel-safety audit

Recorded 2026-07-22 before Program V4 edits.

## Local repository state

- Branch: `main` tracking `origin/main`.
- HEAD: `cb60a882e72056c669871b53ef26d10ae9edee27`.
- Working tree: clean before this audit.
- Local Program V4 branches/worktrees: none found.

## Remote-state check

`gh pr list --state open --limit 30` and `gh issue list --state open --limit
50` could not query GitHub because the local CLI reported no authenticated
host. Therefore this audit does not claim that no remote pull request, issue,
or Labs V2 reconstruction is active. Remote issue creation, PR creation,
merge, CI/Pages inspection, and deployment checks require authenticated access
or an explicit alternate credential path.

## Potential overlap

Program V4 could overlap with the static site generator
`src/distributed_discovery/site/build.py`, shared browser code
`site/src/site.js`, styles in `site/src/styles.css`, generated route registry,
site-build tests, and Lab data. The V3 synchronization milestone is limited to
the generator's public copy and presentation tests; it creates no immutable
research evidence and does not change Lab behavior. DD-016 research work will
initially be isolated to its study, source, tests, results, and report files.

If an active Labs V2 PR is later discovered, do not modify the shared site
files until it is merged. Preserve its behavior and tests, rebase the isolated
research changes after merge, and integrate Program V4 routes only then.

## V4.1 outcome

The editorial-only generator and presentation regression changes passed local
make verify, make papers, and make site gates on 2026-07-22. The generated site
has 59 HTML routes and 19 registered studies. Remote CI, Pages, and deployment
remain unverified because GitHub authentication is unavailable.
