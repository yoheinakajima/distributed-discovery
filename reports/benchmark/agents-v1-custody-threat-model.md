# Agents v1 custody threat model

Protected future assets are generator seed material, hidden instances, answer
keys, model outputs before lock, and the mapping from instances to answers.
There are no protected assets today.

Threats include repository or CI log disclosure; a key committed beside
ciphertext; nonce reuse; generator/config substitution; early answer unsealing;
evaluator access outside the audit log; answer-key mismatch; partial reruns
after observing outputs; provider retention beyond the approved setting; and
loss of immutable raw outputs.

Controls are domain-separated SHA-256 commitments, maintained AEAD libraries,
separate key storage, least-privilege service identity rather than a named human
custodian, append-only access and execution logs, predeclared batch quarantine,
and two-path verification. Custody is automated and role-based; it creates no
people-related workflow.

Residual risk remains from provider infrastructure, account compromise,
operating-system compromise, and undisclosed pretraining exposure. Those risks
must be recorded, not converted into claims of secrecy or independence.
