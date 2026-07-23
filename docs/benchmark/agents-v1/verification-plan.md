# Independent verification plan

Method A is the future instrument path: generator, capability view, protocol
state machine, structured-output validation, and metric evaluator.

Method B is independently implemented from primitive records. It reconstructs
the task from its commitment, recomputes exact study baselines, checks each
information/message/action event, recomputes every numerator, denominator, zero
convention and aggregation, and verifies custody, trace, redaction, and version
hashes. Where a primitive recalculation is possible, Method B may not import
Method A's metric classification.

Release requires exact agreement on primitive validity and exact comparators.
Numerical summaries may use only a predeclared tolerance after both paths
independently compute them. Any disagreement quarantines the batch. This
registration implements schema and public-fixture checks only, not provider
execution or a scientific evaluator.
