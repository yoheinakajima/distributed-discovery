# Evaluation authorization policy

The repository may prepare but cannot exercise financial authority for the
owner. Intent, a recommended tier, a cost estimate, a suggested cap, an issue,
or a merged registration is not authorization.

A future active artifact must name a unique authorization ID, UTC decision
timestamp, exact authorized commit, issue #173, branch, one campaign tier,
exact cloud models, the local model decision, an absolute total cap,
provider-specific caps, local resource caps, expiration, custody and trace
policies, batch IDs, revocation convention, and an explicit owner attestation.
The attestation must be committed through a separately authorized owner action.

Execution is fail-closed. It stops when the artifact is pending, expired,
revoked, mismatched to Git/model/batch state, missing an attestation, or outside
any cap. The template is intentionally inactive with zero caps and
`execution_allowed: false`.
