# Trace policy

Only task-visible messages, declared actions, declared tool-call records,
timestamps and durations, token/cost metadata, retries/errors, validation
outcomes, version IDs, and cryptographic hashes are collected. Hidden chain of
thought is neither requested nor stored. Tools are disabled, so the declared
tool-call list must be empty.

The raw layer is sealed and access-logged. The redacted-public layer replaces
instance text, answer-bearing task state, host paths, request/account
identifiers, and any detected secret pattern with typed placeholders. The
audit-summary layer contains only counts, commitments, validations, metrics,
and release decisions. Every transformation records input and output hashes and
the redaction rule version.

Credentials, tokens, private keys, PII, proprietary data, provider-secret
fields, repository contents, and host paths are prohibited. A trace failing any
prohibition is quarantined and cannot enter analysis.
