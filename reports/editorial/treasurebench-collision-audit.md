# TreasureBench collision audit

Audit date: 2026-07-23 PDT

UTC completion timestamp: 2026-07-24T02:17:58Z

Decision scope: exact formal token `TreasureBench`, spaced variant
`Treasure Bench`, and the required formal/companion adjacency checks.

This is a dated, bounded factual screen. It is not an exhaustive search,
worldwide namespace search, trademark opinion, legal review, availability
guarantee, or ownership claim.

## Decision

`treasurebench-selected-and-implemented`

As of the recorded audit date, no disqualifying same-domain scholarly,
AI-benchmark, multi-agent-system, package, or active high-confusion product
collision for the exact name TreasureBench was found in the declared search
channels.

The implementation decision remains conditional on the repository
compatibility, validation, CI, Pages, and live-route gates. No partial rename
is permitted if one of those gates fails.

## Search method

The following public queries were run:

- `TreasureBench`;
- `"Treasure Bench"`;
- `treasurebench`;
- `TreasureBench benchmark`;
- `TreasureBench AI`;
- `TreasureBench multi-agent`;
- `TreasureBench software`;
- `TreasureBench package`;
- `TreasureBench game`;
- `Treasure Hunt benchmark`;
- `Treasure Hunt multi-agent`.

The audit used direct public APIs or first-party search surfaces when
available, plus a general-web exact-string screen. Search results are
time-dependent. Dynamic, authenticated, unpublished, unindexed, regional, and
common-law uses may be absent.

## Findings

### Scholarly exact-name

- Crossref's public Works API returned `total-results: 0` for
  `TreasureBench`.
- DBLP's public publication API returned `hits @total: 0`.
- OpenAlex's public Works API returned `count: 0`.
- Exact-site searches of arXiv and official proceedings returned no exact
  `TreasureBench` record. The arXiv export endpoint did not return a
  machine-readable response in this environment, so the arXiv check is bounded
  by its public indexed search surface.

Classification: no exact-name scholarly collision found; nonfatal.

### AI/ML benchmark and multi-agent systems

Exact queries for `TreasureBench benchmark`, `TreasureBench AI`, and
`TreasureBench multi-agent` returned no exact formal-token artifact. A GitHub
repository search through the connected GitHub application returned zero
repositories named or described with `TreasureBench`.

Classification: no Tier 1 exact-name benchmark or multi-agent collision found.

### Adjacent software and product uses

Queries for exact `TreasureBench software`, `TreasureBench package`, and
`TreasureBench product` returned no active same-domain product. The spaced
phrase `Treasure Bench` returned unrelated memorial/furniture products,
including a florist's concrete memorial bench. Those results are cross-domain
lexical residue rather than uses of the formal token.

Classification: Tier 3 acceptable residue; nonfatal.

### Game and consumer uses

No exact `TreasureBench` game was found. `Treasure Hunt` itself is a very
common consumer-game phrase and is also used in technical benchmark examples.
That adjacency applies to the companion label, not the exact formal token.

Classification: the exact formal name passes; the companion requires the
mandatory TreasureBench funnel and “not a separate benchmark” statement.

### Treasure Hunt technical adjacency

The search did identify longstanding technical uses of `treasure hunt`:

- Couëtoux et al.'s *Continuous Rapid Action Value Estimates* uses a
  TreasureHunt benchmark in which an agent navigates a square arena toward a
  treasure while avoiding a hole.
- Chen et al.'s *Heuristic Satisficing Inferential Decision Making in Human and
  Robot Active Perception* calls treasure hunt a benchmark inferential
  decision problem for camera-equipped robots.
- GitHub's `treasure-hunt` topic includes multi-agent classroom and JADE
  projects.
- Distributed/mobile-agent scholarship uses treasure hunt for graph/grid
  navigation to a hidden inert target.

This is not an exact `TreasureBench` collision. It is a material reviewer and
citation-graph adjacency, which is why `Treasure Hunt` is rejected as the
formal token and retained only as the playable companion. A primary-source
related-work distinction is mandatory for a future benchmark paper.

Classification: nonfatal for TreasureBench; formal/companion boundary required.

### Account and handle residue

GitHub's public user search returned zero exact `treasurebench` accounts on the
audit date. No material exact-string account or handle was found in the
declared public searches. Code search required authentication and was not used
as evidence of absence.

Classification: no observed exact-handle residue; search limitation retained.

## Registry and namespace observations

| Channel | Query or endpoint | Observed state | Severity |
|---|---|---|---|
| PyPI | `/pypi/treasurebench/json` | HTTP 404 | nonfatal observation |
| npm | `/treasurebench` | HTTP 404 | nonfatal observation |
| GitHub repositories | `TreasureBench` | zero results | nonfatal observation |
| GitHub users | `treasurebench` | zero results | nonfatal observation |
| Hugging Face models | `search=treasurebench` | empty list | nonfatal observation |
| Hugging Face datasets | `search=treasurebench` | empty list | nonfatal observation |
| Hugging Face Spaces | `search=treasurebench` | empty list | nonfatal observation |
| `treasurebench.com` | Verisign RDAP | HTTP 404 / object not found | nonauthoritative |
| `treasurebench.org` | PIR RDAP | HTTP 404 / object not found | nonauthoritative |
| `treasurebench.ai` | Identity Digital RDAP | HTTP 404 / object not found | nonauthoritative |
| `treasurebench.dev` | Google Registry RDAP | HTTP 404 / object not found | nonauthoritative |

The Hugging Face collections endpoint did not provide a reliable exact filtered
response and is not treated as proof of absence. Registry and RDAP responses
can change immediately and do not reserve a namespace.

## Preliminary trademark-register signal

Exact indexed searches limited to official USPTO and EUIPO domains returned no
`TreasureBench` result. Their interactive register search coverage could not be
established as exhaustive in this environment. This is only a preliminary
nonlegal signal. The owner must perform one-time register checks through
owner-controlled access before the first DOI or package publication.

## Severity conclusion

- Tier 1: none found for exact `TreasureBench`.
- Tier 2: none found for exact `TreasureBench`.
- Tier 3: unrelated spaced-phrase furniture/memorial results and generic
  consumer-language adjacency.
- Material non-collision adjacency: `Treasure Hunt` is established technical
  and consumer vocabulary; it remains the companion only.

## Sources

- [Crossref Works API query](https://api.crossref.org/works?query.bibliographic=TreasureBench&rows=20)
- [DBLP publication API query](https://dblp.org/search/publ/api?q=TreasureBench&format=json&h=20)
- [OpenAlex Works query](https://api.openalex.org/works?search=TreasureBench&per-page=20)
- [PyPI project endpoint](https://pypi.org/pypi/treasurebench/json)
- [npm registry endpoint](https://registry.npmjs.org/treasurebench)
- [Hugging Face model search](https://huggingface.co/api/models?search=treasurebench)
- [GitHub repository search](https://github.com/search?q=TreasureBench&type=repositories)
- [Verisign `.com` RDAP](https://rdap.verisign.com/com/v1/domain/treasurebench.com)
- [Continuous RAVE primary manuscript](https://inria.hal.science/hal-00642459)
- [Chen et al. active-perception paper](https://arxiv.org/abs/2309.07720)

## Limitation

The audit does not establish global uniqueness, legal clearance, trademark
availability, package availability, domain availability, or freedom from
regional or common-law rights. Absence of evidence in the declared channels is
not evidence of ownership.
