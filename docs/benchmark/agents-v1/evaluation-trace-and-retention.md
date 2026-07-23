# Evaluation trace and retention

Raw traces contain visible prompts/messages/actions, declared tools (none),
errors, response/request IDs, usage, timing, sampling configuration, exact
model identity, retry events, and operational metadata. They are encrypted at
rest under campaign custody.

Redacted public traces remove credentials, private task/answer material,
secret paths, account/project identifiers, and fields outside the registered
schema. Audit summaries retain commitments, hashes, counts, errors, cost, and
redaction results. Hidden chain of thought is never requested, collected,
inferred, stored, or scored.

Raw and redacted trace retention is fixed to 365 days after campaign closeout
unless legal/provider constraints require a documented shorter quarantine.
Deletion requires a logged owner-authorized event after verification and
release obligations. Failures and error-class summaries remain preserved.
