# Public calibration policy

Public cases exist only for schema conformance, prompt debugging, capability
isolation, metric hand checks, deterministic mock behavior, and custody toy
vectors. They are presumed contaminated for model-evaluation purposes.

Exactly ten public calibration cases are planned: two per registered task
family. Their identifiers, inputs, and answers are public. They may never be
included in a final evaluation estimate, reused as private holdouts, or cited
as model performance evidence.

Public prompts carry a calibration banner outside the model-scored payload.
Final holdout prompts remove benchmark IDs and exact public wording, but retain
the same machine-gradable semantic contract.
