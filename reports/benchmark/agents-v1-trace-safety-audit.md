# Agents v1 trace safety audit

The trace contract is safe to register offline. It stores visible protocol
state and declared actions, not hidden reasoning. It defines raw,
redacted-public, and audit-summary layers and makes redaction hash-verifiable.

Release stops on credentials, PII, proprietary data, host paths, secret
provider fields, answer material, an unverified redaction transform, or a trace
hash mismatch. No trace exists in this registration.
