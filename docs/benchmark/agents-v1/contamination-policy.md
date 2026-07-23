# Contamination policy

Contamination means access to benchmark-specific hidden information or
memorized public benchmark artifacts that could bypass ordinary reasoning. A
correct answer, generic overlap, or familiar mathematical method is not by
itself contamination.

Future probes cover exact public values, near-verbatim answer values, public
task IDs and prompt phrases, theorem/paper/result names, known solution
patterns, copied explanation structure, generator-parameter leakage,
answer-key access, cross-batch leakage, prompt injection, and
benchmark-specific self-identification.

Classifications are:

- `direct-leakage`: protected value, key, or inaccessible instance is present;
- `probable-memorization`: multiple predeclared benchmark-specific markers
  match with no task-visible derivation;
- `ordinary-correct-reasoning`: output is derivable from visible inputs without
  protected markers;
- `inconclusive-overlap`: lexical or structural similarity is insufficient.

Direct leakage stops and quarantines the affected batch and all outputs sharing
its custody boundary. Probable memorization pauses publication and triggers an
independent review of all variants from the model family. Inconclusive overlap
is retained and sensitivity-reported, never silently deleted. Suppressed or
missing probes stop release. Prompts must contain no DD IDs, claim/run IDs,
paper or theorem names, expected values, or recognizable public task wording.
