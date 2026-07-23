# Compatibility policy

Compatibility is explicit and deny-by-default.

- A task family declares allowed team sizes, information rights, action space,
  timing, and supported architectures.
- An architecture is compatible only if it stays within those rights and the
  registered message/tool budget.
- A provider/model candidate is execution-eligible only if an exact or datable
  identifier, required structured-action path, context ceiling, terms/license
  boundary, retention configuration, and reproducibility limitations are
  recorded at the future gate.
- A task/model pair is excluded when the context, structured-output, licensing,
  or local-resource requirement cannot be met.
- An unsupported metric is omitted, never zero-filled.
- Content v1/v2/v3 and `agents-v1` compatibility is recorded independently.

Public calibration, deterministic mocks, and exact algorithmic baselines never
establish provider/model eligibility. Moving aliases may be observed but may
not replace frozen execution identifiers.
