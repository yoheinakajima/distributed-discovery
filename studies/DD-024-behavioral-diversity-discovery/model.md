# DD-024 model boundary

This campaign contains three separately specified finite diagnostic games. They share the Shared Discovery Paradox's finite targets, dispersed evidence, individual actions, and collective discovery objective; they do not use a simulator that returns registered expected answers.

- [Track 02](tracks/track-02/model.md): ambiguous private/public source reliability, a common diagnostic, restricted contingent role policies, independent departures and coordinated mixtures; 18 parameter cells.
- [Track 03](tracks/track-03/model.md): four inspections with matched ex ante detection rates and different failure dependence; 80 parameter cells.
- [Track 04](tracks/track-04/model.md): three clues, four inspections, one message, explicit information in silence/time, and two receiver policy classes; 36 parameter cells.

Every model specifies its stronger comparator and its limitation. A coordinated policy can have more assignment authority while receiving the same evidence and action count; that authority is disclosed. Optimal means only the explicitly enumerated finite policy class or a matching certificate within it. No objective is actual societal welfare, and no policy is a measured personality trait.

The complete primary configurations are bound by [registered-configs.json](registered-configs.json). Small development fixtures are not primary runs and cannot be passed to the primary runner after its grid-hash gate. Maximum primary allocation is three simultaneous workers, each limited to 120 seconds and 1024 MiB. The full primary includes persistence, independent verification, and corruption checks within that wall-time cap.

Each run consumes an exclusive per-track reservation in the common Git directory before launching. An incomplete manifest exists before computation; failures, interruptions, missing outputs, signal exits, and corrupt verification remain visible. Reservations are shared by detached worktrees and never cleared to obtain another primary attempt. Results become immutable after finalization. A separately authorized and registered independent reproduction uses the frozen source commit in a separate clone. This campaign authorizes no second primary through a fresh clone; existing evidence can be rechecked without a new primary using `--verify-existing`.
