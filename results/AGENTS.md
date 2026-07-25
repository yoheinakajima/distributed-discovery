# Result-artifact instructions

- Result directories are immutable evidence after creation; never overwrite or
  rerun a passing primary configuration for freshness.
- Follow `docs/reproducibility.md`: preserve source commit, inputs, commands,
  environment, timestamps, seeds, hashes, stdout/stderr, outputs, validation,
  and failures.
- A generated value is claim-eligible only through a separate claim audit.
- Do not move private evaluation state into public results. Redacted engineering
  records are not scientific runs unless separately registered.
