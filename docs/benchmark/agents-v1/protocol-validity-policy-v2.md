# TreasureBench Agents v1 protocol-validity policy v2

Status: prospective, frozen, not executed. Authority: AO-0010 and DD-010
engineering only.

Policy v2 applies only to future campaigns that explicitly register it. It
does not rewrite or reclassify any historical policy, schema, campaign, trace,
or decision. AO-0008 and all earlier campaigns remain permanently closed and
immutable.

## Four separate statuses

`batch-integrity-valid` says the custody, identity, cap, ledger, response,
trace, pairing, inventory, lock, unseal-order, contamination, verification,
redaction, and retained-state invariants pass. It is a batch property.

Each intended pairing receives exactly one terminal pairing status.
`provider-terminal-missing` means bounded transport attempts ended without a
completed provider response. `protocol-valid` means independent Method C
accepts the completed terminal trace. `protocol-invalid` means a completed
provider response remains nonconforming after the one schema-only repair or
otherwise violates the registered protocol.

A protocol-invalid pairing is evaluated-system behavior. It is neither a
provider-terminal-missing outcome nor, by itself, a batch-integrity failure.

## Invalid outputs

Every protocol-invalid terminal trace and its safe classification is
preserved. The pairing remains in every intended-pairing denominator and is
never replaced or rerun. No invalid action is parsed or credited, and no
substitute action or valid portfolio is constructed. Protocol conformance is
reported separately.

The transport and action bounds do not change: at most two bounded transport
attempts for the same logical request, exactly one schema-only repair, zero
semantic-answer or outcome-dependent retries, zero silent normalization, and
exactly one final action per required agent. Method C runs before performance
interpretation.

## Metric bounds

An invalid output has exact operational no-valid-action credit where the
registered operational record is defined by submitted valid actions. That
credit is not presented as a known unconditional architecture-performance
value. Instead, every registered metric has a prospective feasible interval
for protocol-invalid pairings. Valid pairings have a degenerate interval at
their exact metric; invalid pairings use the metric-specific support or
task-specific comparator bounds in the machine-readable policy.

For a paired contrast, if the left interval is `[L₁, U₁]` and the right
interval is `[L₀, U₀]`, the contrast interval is
`[L₁ − U₀, U₁ − L₀]`. Aggregate bounds average those endpoints over every
intended paired unit. A second implementation must reconstruct the same
bounds.

Valid-output-conditional estimates are allowed only as secondary,
selection-conditioned diagnostics. Complete-case estimates cannot be labeled
as unconditional architecture effects. No composite score, provider/model
ranking, or leaderboard may be created.

## Batch disposition

Protocol-invalid traces alone do not quarantine a v2-policy batch. Engineering
completion requires both public canaries, fresh custody, one unique terminal
protocol-valid or protocol-invalid trace for all 500 intended pairings, zero
provider-terminal-missing outcomes, exact response-ledger-trace identity
correspondence, complete pairings, zero contamination, cap and lock
compliance, post-lock unseal and commitment verification, Methods A/B
agreement wherever metrics are defined, Method C classification for every
pairing, independent bound agreement, and passing corruption and redaction
checks.

The batch is still quarantined for provider-terminal missingness; a missing or
duplicate pairing; response, ledger, trace, inventory, or retained-state
integrity failure; contamination; cap or execution-identity breach;
output-lock or unseal-order failure; Method disagreement; bounds
reconstruction disagreement; or unsafe retained state.

There is no global conformance threshold derived from AO-0008 and no rerun
until a preferred invalid rate appears. Whether later evidence is informative
depends on the width of the registered all-pairing bounds.
