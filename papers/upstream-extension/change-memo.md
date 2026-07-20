# Change memo — additive upstream paper extension (DD-000)

## Baseline and scope

Target: `paper/The_Shared_Discovery_Paradox.tex` at upstream commit `5025cc8e8f2f8ca015dff2066f08f81ad5715a51`. The patch adds roughly two pages of framing. It does not change numerical values, proofs, theorem statements/numbers, the title, abstract, canonical example, or conclusion.

## Placements

1. **Keywords:** add “distributed discovery” and “action allocation” to make the framing discoverable.
2. **Introduction:** after the benchmark-method paragraph, insert a working definition that separates information architecture from action protocol. It explicitly disclaims a unique phrase/field claim because DD-C-0017 found terminology collisions.
3. **Framework heading:** rename “Information value and protocol loss” to “Distributed Discovery: Information Frontiers and Protocol Loss.” The underlying atomic definitions and propositions remain unchanged.
4. **Institutional matrix:** after the existing warning about the planner/private comparison, add the 2×2 matrix and explain the missing private-team frontier. This makes the confounded comparison visible without solving DD-001.
5. **Benchmark dictionary:** add two rows to the existing table rather than introduce a duplicate table.
6. **Research program:** immediately before “Limitations and extensions,” add a compact subsection covering DD-001 through DD-007 and explicitly label all directions as questions.

## Why the insertions help

The paper already contains the atomic framework and a strong benchmark dictionary. The additions give those parts one stable umbrella, make the information/assignment distinction operational, and show how the open private-team cell motivates an extension without expanding the original proof burden.

## What must not change

- Preserve “The Shared Discovery Paradox” as title and primary result.
- Keep the sixteen-box story and interactive six-minute explanation primary.
- Do not add a general theorem, novelty assertion, or solved-study implication.
- Do not replace the current lineage/limitations sections.
- Do not push or commit in canonical upstream.

## Reviewer objections and responses

- **“The umbrella is broader than the proved model.”** The added text calls it a research program, preserves the atomic scope, and labels directions as questions.
- **“Distributed discovery is already used elsewhere.”** The introduction calls it a working label and disclaims phrase novelty; the private workspace records the collision.
- **“The planner/private matrix overstates causal isolation.”** The text states exactly which margins change and identifies the missing private-team cell rather than imputing its value.
- **“The additions lengthen an intentionally concise paper.”** Existing material is reused; only two dictionary rows, one matrix, and two compact paragraphs are added.
