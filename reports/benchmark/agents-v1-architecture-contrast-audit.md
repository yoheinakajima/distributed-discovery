# Agents v1 architecture contrast audit

Five agent architectures and one exact comparator family are registered. Each
architecture has explicit information rights, action rights, topology, rounds,
message budget, scientific contrast, no-answer-access rule, and machine
grading. The set is intentionally small:

1. isolated private agents;
2. full broadcast/shared transcript;
3. designated reader/selective sharing;
4. pooled consensus;
5. portfolio-preserving structured roles;
6. exact algorithmic baselines as non-agent comparators.

The structured portfolio protocol is not presented as spontaneous autonomy: it
predeclares opaque action slots and measures what role structure changes. It
does not expose expected answers or evaluator state. No arbitrary agent
framework, live orchestration package, or provider adapter is registered.
