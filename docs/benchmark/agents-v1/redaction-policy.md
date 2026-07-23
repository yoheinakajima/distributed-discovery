# Redaction policy

Redaction is deterministic and versioned as `agents-redaction-v1`. Before
public release it removes API keys and bearer strings, account/request IDs,
email/IP patterns, absolute paths, private seed/key material, ciphertext
plaintext mappings, hidden instance bodies, answer keys, and provider fields
not named in the trace schema.

Redaction never changes declared actions, validation outcomes, metric inputs,
or the order of visible messages. Each replacement is a typed token such as
`[REDACTED:HOST_PATH]`; the record stores only category and count. The verifier
recomputes the public trace hash after redaction and checks that prohibited
patterns are absent.

No redaction is used to conceal protocol violations or adverse results. If a
scientifically necessary field cannot be released safely, publish an
audit-summary record and retain the raw trace under custody.
