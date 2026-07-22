"""Labeled exact normal-form evaluator for DD-018."""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Sequence
from dataclasses import asdict, dataclass
from fractions import Fraction
from itertools import combinations, product
from typing import Any

from distributed_discovery.threshold_discovery.model import occupancy_vectors, planner_value

Profile = tuple[int, ...]
Support = tuple[tuple[Fraction, Profile], ...]


@dataclass(frozen=True)
class MechanismSpec:
    name: str
    information_observed: str
    actions_observed: str
    commitment: str
    transfers: str
    subsidy: str
    anonymity: str
    identity_selection: str
    deviation_class: str
    report_truthfulness: str = "not-applicable-common-posterior-input"


MECHANISMS = (
    MechanismSpec(
        "central-assignment",
        "common posterior and named agents",
        "assigned actions",
        "authoritative action assignment",
        "none",
        "none",
        "no",
        "fixed identity order",
        "none after commitment",
    ),
    MechanismSpec(
        "random-matching",
        "common posterior",
        "matched-team assignments",
        "authoritative random matching and assignment",
        "none",
        "none",
        "yes ex ante",
        "uniform random perfect matching",
        "none after commitment",
    ),
    MechanismSpec(
        "team-tokens",
        "common posterior and own token",
        "submitted actions",
        "none; token eligibility is binding",
        "discovery prize restricted to matching tokens",
        "none",
        "no after token realization",
        "fixed balanced token endowment",
        "unilateral, pair, and tau-player strict-member deviations",
    ),
    MechanismSpec(
        "exclusive-coalition-rights",
        "common posterior and coalition charter",
        "submitted actions",
        "none; coalition rights are binding",
        "discovery prize restricted to chartered coalition",
        "none",
        "no",
        "fixed named coalitions",
        "unilateral, pair, and tau-player strict-member deviations",
    ),
    MechanismSpec(
        "correlated-mediator",
        "common posterior and private recommendation",
        "submitted actions",
        "nonbinding recommendation",
        "threshold-adjusted equal split only",
        "none",
        "yes ex ante",
        "uniform correlated team recommendation",
        "obedience, unilateral, pair, and tau-player strict-member deviations",
    ),
    MechanismSpec(
        "universal-pooling",
        "common posterior",
        "submitted actions",
        "none",
        "threshold-adjusted equal split only",
        "none",
        "yes",
        "none; common lexicographic mode",
        "unilateral, pair, and tau-player strict-member deviations",
    ),
    MechanismSpec(
        "sole-team-rescue",
        "common posterior",
        "submitted actions and viable-team count",
        "none",
        "prize paid only when exactly one candidate is viable",
        "none",
        "yes",
        "none; common lexicographic mode",
        "unilateral, pair, and tau-player strict-member deviations",
    ),
    MechanismSpec(
        "marginal-coalition-contribution",
        "common posterior",
        "submitted actions and occupancies",
        "none",
        "prize shared only by an exactly minimal viable team",
        "none",
        "yes",
        "fixed recommendation selects identities",
        "unilateral, pair, and tau-player strict-member deviations",
    ),
    MechanismSpec(
        "threshold-adjusted-equal-split",
        "common posterior",
        "submitted actions and occupancies",
        "none",
        "candidate prize split across every member of a viable team",
        "none",
        "yes",
        "fixed recommendation selects identities",
        "unilateral, pair, and tau-player strict-member deviations",
    ),
    MechanismSpec(
        "pairwise-matching-market",
        "common posterior and matched teammate",
        "team candidate choices",
        "binding within-pair action; no cross-pair assignment",
        "threshold-adjusted equal split only",
        "none",
        "yes across pairs",
        "fixed pair partition",
        "pair deviations; tau-player deviations coincide with pairs",
    ),
)


def validate_fixture(posterior: Sequence[Fraction], agents: int, threshold: int) -> Profile:
    values = tuple(posterior)
    if len(values) != 3 or any(value <= 0 for value in values):
        raise ValueError("DD-018 fixes three positive posterior candidates")
    if sum(values, Fraction()) != 1 or tuple(sorted(values, reverse=True)) != values:
        raise ValueError("posterior must be normalized and weakly descending")
    if agents != 4 or threshold != 2:
        raise ValueError("DD-018 v1 fixes N=4 and tau=2")
    return tuple(range(len(values)))


def profile_space(candidates: int, agents: int) -> Iterator[Profile]:
    yield from product(range(candidates), repeat=agents)


def occupancy(profile: Sequence[int], candidates: int) -> tuple[int, ...]:
    return tuple(profile.count(candidate) for candidate in range(candidates))


def discovery(profile: Sequence[int], posterior: Sequence[Fraction], threshold: int) -> Fraction:
    counts = occupancy(profile, len(posterior))
    return sum(
        (posterior[candidate] for candidate, count in enumerate(counts) if count >= threshold),
        Fraction(),
    )


def planner_profile(posterior: Sequence[Fraction], agents: int, threshold: int) -> Profile:
    validate_fixture(posterior, agents, threshold)
    return tuple(candidate for candidate in range(agents // threshold) for _ in range(threshold))


def _balanced_support() -> Support:
    profiles = []
    for top_team in combinations(range(4), 2):
        profile = tuple(0 if agent in top_team else 1 for agent in range(4))
        profiles.append(profile)
    probability = Fraction(1, len(profiles))
    return tuple((probability, profile) for profile in profiles)


def recommendation_support(
    mechanism: str, posterior: Sequence[Fraction], agents: int, threshold: int
) -> Support:
    planned = planner_profile(posterior, agents, threshold)
    if mechanism in {"random-matching", "correlated-mediator"}:
        return _balanced_support()
    if mechanism in {"universal-pooling", "sole-team-rescue"}:
        return ((Fraction(1), (0,) * agents),)
    return ((Fraction(1), planned),)


def is_committed(mechanism: str) -> bool:
    return mechanism in {"central-assignment", "random-matching"}


def agent_utility(
    mechanism: str,
    posterior: Sequence[Fraction],
    profile: Profile,
    agent: int,
    threshold: int,
    assignment: Profile,
) -> Fraction:
    counts = occupancy(profile, len(posterior))
    action = profile[agent]
    if mechanism in {"team-tokens", "exclusive-coalition-rights"}:
        if action != assignment[agent]:
            return Fraction()
        eligible = sum(
            profile[other] == action and assignment[other] == action
            for other in range(len(profile))
        )
        return posterior[action] / eligible if eligible >= threshold else Fraction()
    if mechanism == "sole-team-rescue":
        viable = [candidate for candidate, count in enumerate(counts) if count >= threshold]
        return (
            posterior[action] / counts[action]
            if len(viable) == 1 and action == viable[0]
            else Fraction()
        )
    if mechanism == "marginal-coalition-contribution":
        return posterior[action] / threshold if counts[action] == threshold else Fraction()
    return posterior[action] / counts[action] if counts[action] >= threshold else Fraction()


def _deviated(profile: Profile, coalition: Sequence[int], destinations: Sequence[int]) -> Profile:
    changed = list(profile)
    for member, destination in zip(coalition, destinations, strict=True):
        changed[member] = destination
    return tuple(changed)


def strict_coalition_witness(
    mechanism: str,
    posterior: Sequence[Fraction],
    profile: Profile,
    coalition_size: int,
    threshold: int,
    assignment: Profile,
    allowed_coalitions: Iterable[tuple[int, ...]] | None = None,
) -> dict[str, Any] | None:
    coalitions = (
        tuple(allowed_coalitions)
        if allowed_coalitions is not None
        else tuple(combinations(range(len(profile)), coalition_size))
    )
    for coalition in coalitions:
        current = tuple(
            agent_utility(mechanism, posterior, profile, member, threshold, assignment)
            for member in coalition
        )
        for destinations in product(range(len(posterior)), repeat=len(coalition)):
            if all(
                profile[member] == destination
                for member, destination in zip(coalition, destinations, strict=True)
            ):
                continue
            changed = _deviated(profile, coalition, destinations)
            candidate = tuple(
                agent_utility(mechanism, posterior, changed, member, threshold, assignment)
                for member in coalition
            )
            if all(after > before for before, after in zip(current, candidate, strict=True)):
                return {
                    "coalition": coalition,
                    "destinations": destinations,
                    "old_utilities": current,
                    "new_utilities": candidate,
                }
    return None


def strict_unilateral_obedience(
    mechanism: str,
    posterior: Sequence[Fraction],
    profile: Profile,
    threshold: int,
    assignment: Profile,
) -> bool:
    for agent in range(len(profile)):
        current = agent_utility(mechanism, posterior, profile, agent, threshold, assignment)
        for destination in range(len(posterior)):
            if destination == profile[agent]:
                continue
            changed = _deviated(profile, (agent,), (destination,))
            if (
                agent_utility(mechanism, posterior, changed, agent, threshold, assignment)
                >= current
            ):
                return False
    return True


def _unilateral_nash(
    mechanism: str,
    posterior: Sequence[Fraction],
    profile: Profile,
    threshold: int,
    assignment: Profile,
) -> bool:
    return strict_coalition_witness(mechanism, posterior, profile, 1, threshold, assignment) is None


def equilibrium_count(
    mechanism: str,
    posterior: Sequence[Fraction],
    agents: int,
    threshold: int,
    assignment: Profile,
) -> int | str:
    if is_committed(mechanism):
        return "not-applicable-authoritative-commitment"
    if mechanism == "pairwise-matching-market":
        teams = ((0, 1), (2, 3))
        count = 0
        for choices in product(range(len(posterior)), repeat=2):
            profile = (choices[0], choices[0], choices[1], choices[1])
            if (
                strict_coalition_witness(
                    mechanism,
                    posterior,
                    profile,
                    2,
                    threshold,
                    assignment,
                    allowed_coalitions=teams,
                )
                is None
            ):
                count += 1
        return count
    return sum(
        _unilateral_nash(mechanism, posterior, profile, threshold, assignment)
        for profile in profile_space(len(posterior), agents)
    )


def _budget_safe(
    mechanism: str,
    posterior: Sequence[Fraction],
    agents: int,
    threshold: int,
    assignment: Profile,
) -> bool:
    return all(
        sum(
            (
                agent_utility(mechanism, posterior, profile, agent, threshold, assignment)
                for agent in range(agents)
            ),
            Fraction(),
        )
        <= discovery(profile, posterior, threshold)
        for profile in profile_space(len(posterior), agents)
    )


def evaluate_mechanism(
    spec: MechanismSpec,
    posterior: Sequence[Fraction],
    agents: int,
    threshold: int,
) -> dict[str, Any]:
    validate_fixture(posterior, agents, threshold)
    support = recommendation_support(spec.name, posterior, agents, threshold)
    assignment = planner_profile(posterior, agents, threshold)
    expected_discovery = sum(
        (
            probability * discovery(profile, posterior, threshold)
            for probability, profile in support
        ),
        Fraction(),
    )
    expected_payout = sum(
        (
            probability
            * sum(
                (
                    agent_utility(spec.name, posterior, profile, agent, threshold, assignment)
                    for agent in range(agents)
                ),
                Fraction(),
            )
            for probability, profile in support
        ),
        Fraction(),
    )
    if is_committed(spec.name):
        obedience: bool | str = "not-applicable-authoritative-commitment"
        strictness: bool | str = "not-applicable-authoritative-commitment"
        pair_stable: bool | str = "not-applicable-authoritative-commitment"
        tau_stable: bool | str = "not-applicable-authoritative-commitment"
    elif spec.name == "pairwise-matching-market":
        obedience = "not-applicable-binding-within-pair"
        strictness = "not-applicable-binding-within-pair"
        pair_groups = ((0, 1), (2, 3))
        pair_stable = all(
            strict_coalition_witness(
                spec.name,
                posterior,
                profile,
                2,
                threshold,
                assignment,
                allowed_coalitions=pair_groups,
            )
            is None
            for _, profile in support
        )
        tau_stable = pair_stable
    else:
        obedience = all(
            strict_coalition_witness(spec.name, posterior, profile, 1, threshold, assignment)
            is None
            for _, profile in support
        )
        strictness = all(
            strict_unilateral_obedience(spec.name, posterior, profile, threshold, assignment)
            for _, profile in support
        )
        pair_stable = all(
            strict_coalition_witness(
                spec.name,
                posterior,
                profile,
                2,
                threshold,
                assignment,
            )
            is None
            for _, profile in support
        )
        tau_stable = all(
            strict_coalition_witness(
                spec.name,
                posterior,
                profile,
                threshold,
                threshold,
                assignment,
            )
            is None
            for _, profile in support
        )
    utilities = [
        agent_utility(spec.name, posterior, profile, agent, threshold, assignment)
        for _, profile in support
        for agent in range(agents)
    ]
    return {
        **asdict(spec),
        "posterior": tuple(posterior),
        "agents": agents,
        "threshold": threshold,
        "recommendation_support": support,
        "recommendation_support_count": len(support),
        "planner_discovery": planner_value(posterior, agents, threshold),
        "expected_discovery": expected_discovery,
        "implements_planner_portfolio": expected_discovery
        == planner_value(posterior, agents, threshold),
        "participation": min(utilities) >= 0,
        "obedience": obedience,
        "strict_unilateral_obedience": strictness,
        "pairwise_strict_stable": pair_stable,
        "tau_player_strict_stable": tau_stable,
        "weak_budget_balance": _budget_safe(spec.name, posterior, agents, threshold, assignment),
        "external_subsidy": Fraction(),
        "expected_total_payout": expected_payout,
        "exact_budget_balance_at_recommendation": expected_payout == expected_discovery,
        "equilibrium_concept": (
            "not-applicable-after-authoritative-commitment"
            if is_committed(spec.name)
            else (
                "pure-pair-choice-equilibrium"
                if spec.name == "pairwise-matching-market"
                else "labeled-pure-nash-under-unilateral-deviations"
            )
        ),
        "equilibrium_multiplicity": equilibrium_count(
            spec.name, posterior, agents, threshold, assignment
        ),
    }


def evaluate_registry(config: dict[str, Any]) -> dict[str, Any]:
    agents = int(config["agents"])
    threshold = int(config["threshold"])
    rows = []
    for fixture in config["posterior_fixtures"]:
        posterior = tuple(Fraction(value) for value in fixture["posterior"])
        for spec in MECHANISMS:
            row = evaluate_mechanism(spec, posterior, agents, threshold)
            row["fixture"] = fixture["name"]
            rows.append(row)
    return {
        "rows": rows,
        "fixture_count": len(config["posterior_fixtures"]),
        "mechanism_count": len(MECHANISMS),
        "mechanism_fixture_rows": len(rows),
        "labeled_action_profiles_per_fixture": len(
            tuple(profile_space(int(config["candidates"]), agents))
        ),
    }


def exhaustive_planner_check(
    posterior: Sequence[Fraction], agents: int, threshold: int
) -> Fraction:
    return max(
        sum(
            (posterior[index] for index, count in enumerate(counts) if count >= threshold),
            Fraction(),
        )
        for counts in occupancy_vectors(len(posterior), agents)
    )
