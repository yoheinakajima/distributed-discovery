# DD-003 research brief — Effective Channels in Source Networks

## Motivating question

Which features of a latent evidence-source network predict posterior quality, action concentration, and discovery beyond nominal report count or pairwise signal correlation?

## Minimum viable model

- One target over \(M=3\) locations.
- Up to three latent sources \(Z_k\), conditionally independent given the target in the first model, each with a stated accuracy.
- A bipartite source-to-searcher graph; each searcher observes either one source output or a deterministic bundle summary.
- Searchers follow private reports, pooled consensus, or a pooled planner; strategic action is deferred.
- Graphs are compared up to source/searcher relabeling, with source accuracies held fixed.

This generalizes the canonical common-cue process: the upstream scalar copier count becomes one star-like graph family, not the definition of source dependence.

## Relationship to the canonical benchmark

The canonical common cue collapses \(K\) copying agents into one generative draw and defines a model-specific effective-channel count. DD-003 tests which diagnostics survive when sources overlap through arbitrary small graphs. It preserves the atomic coverage objective initially so evidence structure is the only changed link.

## Main quantities

- Exact discovery for private, consensus, and planner protocols.
- Number of latent generative draws and observed reports.
- Source-degree and exposure Herfindahl indices.
- Pairwise report correlation matrix and higher-order agreement probabilities.
- Provenance overlap between searcher pairs.
- Planner gain, protocol loss, and expected distinct actions.
- Candidate diagnostics such as effective rank or entropy, always labeled by definition.

## Adjacent literature

Network epistemology (Zollman 2007), organizational exploration (March 1991), division of cognitive labor (Kitcher 1990), and the canonical common-cue computation are direct starting points. Effective-sample-size, rank, and information-capacity traditions use different objects; no terminology is imported without a definition.

## Likely methods

Graph-isomorphism reduction; exact latent-state enumeration; symbolic moment matching; enumeration of nonisomorphic bipartite graphs; counterexample search for diagnostics; sensitivity to source accuracy heterogeneity; later latent-variable identification analysis.

## Falsifiable questions

1. Do two nonisomorphic source graphs exist with the same pairwise report-correlation matrix but different discovery or planner gain?
2. Is any scalar based only on source degrees sufficient on the minimum graph class?
3. Does the canonical effective-channel count order discovery outside the common-cue family?
4. Which higher-order provenance statistic resolves the first pairwise-correlation counterexample?

## Dependencies and risks

Depends on DD-000 dependence terminology and canonical results; DD-007 will consume diagnostics only after DD-003 defines them. Risks include nonidentifiability from reports, conflating a latent source with an independent draw, silently assuming conditional independence, graph symmetries that inflate apparent sample size, and calling a descriptive scalar universal.

## First executable experiment

Enumerate every nonisomorphic bipartite graph with at most three sources and four searchers under a fixed rational accuracy. Compute exact joint report distributions and group graphs by identical pairwise moments; search within groups for differing protocol discovery. Record graph canonical labels and exact witnesses.

## Completion criteria

- The source unit and generative assumptions are explicit.
- Graph enumeration is complete for a stated class.
- Any insufficiency result has an exact paired witness.
- Proposed diagnostics are tested for invariance and counterexamples.
- Identifiability from observable reports is distinguished from predictive usefulness with known provenance.
