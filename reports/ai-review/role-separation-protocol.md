# Internal AI role-separation protocol

Each audit assignment declares one role from the canonical ten-role registry,
the artifact under review, allowed context, prohibited sources, expected
method, output schema, stop conditions, and escalation path. A producing role
cannot certify its own work. Reproduction, distinct-method verification,
adversarial proof, and final acceptance outputs remain separate records even
when executed by the same underlying system at different times.

Separation is documented, not presumed. The record names shared code,
prompts, models, context, libraries, and generated artifacts. A materially
distinct method must change the proof route, state representation, algorithm,
or independently checkable certificate; restating or rerunning the producing
method is not sufficient.

No role is executed by this architecture milestone.
