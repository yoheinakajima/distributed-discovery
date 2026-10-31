"""Exact finite audit of message timing, silence, and receiver restrictions.

The primary optimizer and raw-world verifier intentionally have separate
probability, observation, and decision implementations. Neither function writes
files. The campaign runner owns clean-source provenance and resource limits.
"""

from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from math import lcm
from typing import Any

PROTOCOLS = (
    "early",
    "late",
    "agreement_trigger",
    "disagreement_trigger",
    "yoked_agreement",
    "yoked_disagreement",
    "early_augmented",
    "late_augmented",
)
RECEIVERS = ("individual_map", "coverage_aware")
EVENTS = ("agreement_trigger", "disagreement_trigger")


def _fraction(value: Fraction | int) -> str:
    number = Fraction(value)
    return f"{number.numerator}/{number.denominator}"


def _key(values: tuple[int, ...]) -> str:
    return "|".join(str(item) for item in values)


def _cells(config: dict[str, Any]) -> list[tuple[int, Fraction, Fraction]]:
    expected: dict[str, Any] = {
        "schema_version": "dd024-timing-v1",
        "study_id": "DD-024",
        "track_id": "track-04",
        "protocols": list(PROTOCOLS),
        "receivers": list(RECEIVERS),
        "objective": "terminal_team_union_discovery",
        "sender_policy": "posterior_mode_then_next_after_failure_lowest_label_ties",
        "success_continuation_action": 0,
        "clue_budget": {"sender": 2, "receiver": 1, "total": 3},
        "action_budget": {"sender": 2, "receiver": 2, "total": 4},
        "packet_budget": 1,
        "own_feedback": "perfect_detection",
        "other_agent_actions_and_outcomes": "unobserved",
        "silence": "observed_and_conditioned_on",
        "arithmetic": "exact_rational",
        "tie_break": "lowest_target_label",
        "zero_mass_information_sets": "omitted_with_action_zero_default",
        "time_cap_seconds": 120,
        "memory_cap_mb": 1024,
        "random_seeds": {"algorithm": [], "model": None},
    }
    for name, value in expected.items():
        if config.get(name) != value:
            raise ValueError(f"Unregistered track-04 setting: {name}")
    counts = config.get("target_counts")
    p_values, q_values = config.get("p_values"), config.get("q_values")
    if not isinstance(counts, list) or not counts:
        raise ValueError("target_counts must be a nonempty list")
    if not isinstance(p_values, list) or not isinstance(q_values, list):
        raise ValueError("accuracy grids must be lists")
    if not p_values or not q_values:
        raise ValueError("accuracy grids must be nonempty")
    answer: list[tuple[int, Fraction, Fraction]] = []
    for m in counts:
        if type(m) is not int or m not in (3, 4, 5):
            raise ValueError("Only M=3,4,5 are registered")
        for raw_p, raw_q in product(p_values, q_values):
            p = Fraction(1, m) if raw_p == "chance" else Fraction(raw_p)
            q = Fraction(1, m) if raw_q == "chance" else Fraction(raw_q)
            if not Fraction(1, m) <= p <= 1 or not Fraction(1, m) <= q <= 1:
                raise ValueError("Accuracies must be between chance and one")
            answer.append((m, p, q))
    if len(set(answer)) != len(answer) or len(answer) > 36:
        raise ValueError("Duplicate or expanded source-law grid")
    return answer


def _cell_id(m: int, p: Fraction, q: Fraction) -> str:
    return f"m{m}-p{p.numerator}of{p.denominator}-q{q.numerator}of{q.denominator}"


@dataclass(frozen=True, slots=True)
class _Source:
    target: int
    x: int
    z: int
    y: int
    mass: int
    a_covers: bool


@dataclass(frozen=True, slots=True)
class _Atom:
    target: int
    x: int
    z: int
    y: int
    early: int
    mass: int
    a_covers: bool


def _primary_sources(m: int, p: Fraction, q: Fraction) -> tuple[list[_Source], int, dict[str, Any]]:
    # Integer channel weights share a denominator even at zero/one boundaries.
    pd, qd = p.denominator * (m - 1), q.denominator * (m - 1)
    pw = [
        [p.numerator * (m - 1) if s == t else p.denominator - p.numerator for s in range(m)]
        for t in range(m)
    ]
    qw = [
        [q.numerator * (m - 1) if s == t else q.denominator - q.numerator for s in range(m)]
        for t in range(m)
    ]
    sender: dict[str, Any] = {}
    choices: dict[tuple[int, int], tuple[int, int]] = {}
    for x, z in product(range(m), repeat=2):
        order = sorted(range(m), key=lambda t: (-pw[t][x] * qw[t][z], t))
        choices[x, z] = (order[0], order[1])
        sender[_key((x, z))] = {
            "first": order[0],
            "second_after_failure": order[1],
            "second_after_success": 0,
        }
    atoms: list[_Source] = []
    for t, x, z, y in product(range(m), repeat=4):
        mass = pw[t][x] * qw[t][z] * pw[t][y]
        if mass:
            atoms.append(_Source(t, x, z, y, mass, t in choices[x, z]))
    denominator = m * pd * qd * pd
    if sum(atom.mass for atom in atoms) != denominator:
        raise ValueError("Primary source law is not normalized")
    return atoms, denominator, sender


def _timed_atoms(
    sources: list[_Source], denominator: int, protocol: str, alpha: Fraction
) -> tuple[list[_Atom], int]:
    result: list[_Atom] = []
    if protocol.startswith("yoked_"):
        probability = alpha if protocol == "yoked_agreement" else 1 - alpha
        choices = ((0, probability.denominator - probability.numerator), (1, probability.numerator))
        for source in sources:
            for early, numerator in choices:
                if numerator:
                    result.append(
                        _Atom(
                            source.target,
                            source.x,
                            source.z,
                            source.y,
                            early,
                            source.mass * numerator,
                            source.a_covers,
                        )
                    )
        return result, denominator * probability.denominator
    for source in sources:
        if protocol == "agreement_trigger":
            early = int(source.x == source.z)
        elif protocol == "disagreement_trigger":
            early = int(source.x != source.z)
        else:
            early = int(protocol in ("early", "early_augmented"))
        result.append(
            _Atom(source.target, source.x, source.z, source.y, early, source.mass, source.a_covers)
        )
    return result, denominator


def _first_observation(atom: _Atom, protocol: str) -> tuple[int, ...]:
    see_c = protocol in EVENTS or (protocol.endswith("augmented") and atom.early == 1)
    return (
        atom.y,
        atom.early,
        atom.x if atom.early else -1,
        int(atom.x == atom.z) if see_c else -1,
    )


def _second_observation(atom: _Atom, protocol: str, first: int) -> tuple[int, ...]:
    see_c = protocol in EVENTS or protocol.endswith("augmented")
    return (
        atom.y,
        atom.early,
        atom.x,
        int(atom.x == atom.z) if see_c else -1,
        first,
        int(atom.target == first),
    )


def _primary_channel(
    atoms: list[_Atom],
    denominator: int,
    protocol: str,
    m: int,
    source_count: int,
    alpha: Fraction,
) -> dict[str, Any]:
    information: dict[str, list[int]] = {}
    payloads: set[tuple[int, ...]] = set()
    transcripts: set[tuple[int, ...]] = set()
    augmented = protocol.endswith("augmented")
    for atom in atoms:
        key = _key(_first_observation(atom, protocol))
        information.setdefault(key, [0] * m)[atom.target] += atom.mass
        payload = (atom.x, int(atom.x == atom.z)) if augmented else (atom.x,)
        payloads.add(payload)
        transcripts.add((atom.early, *payload))
    first_information = {
        key: {
            "mass": _fraction(Fraction(sum(masses), denominator)),
            "target_masses": [_fraction(Fraction(v, denominator)) for v in masses],
        }
        for key, masses in sorted(information.items())
    }
    return {
        "protocol": protocol,
        "trigger_early_on": (
            1
            if protocol == "agreement_trigger"
            else 0
            if protocol == "disagreement_trigger"
            else None
        ),
        "arrival_probability": _fraction(
            Fraction(sum(atom.mass for atom in atoms if atom.early), denominator)
        ),
        "agreement_probability": _fraction(alpha),
        "payload_fields": ["X", "C"] if augmented else ["X"],
        "payload_alphabet_max": 2 * m if augmented else m,
        "transcript_alphabet_max": m if protocol in ("early", "late") else 2 * m,
        "reached_payload_symbols": len(payloads),
        "reached_transcript_symbols": len(transcripts),
        "positive_source_worlds": source_count,
        "zero_mass_source_worlds": m**4 - source_count,
        "positive_timed_worlds": len(atoms),
        "probability_mass": _fraction(Fraction(sum(atom.mass for atom in atoms), denominator)),
        "clue_budget": 3,
        "action_budget": 4,
        "packet_budget": 1,
        "first_information": first_information,
    }


def _optimize(
    atoms: list[_Atom], m: int, protocol: str, receiver: str
) -> tuple[int, dict[str, Any]]:
    initial: dict[tuple[int, ...], list[_Atom]] = defaultdict(list)
    for atom in atoms:
        initial[_first_observation(atom, protocol)].append(atom)
    first_policy: dict[str, int] = {}
    second_policy: dict[str, int] = {}
    total = 0
    for observation, group in sorted(initial.items()):
        immediate = [sum(a.mass for a in group if a.target == target) for target in range(m)]
        continuation_values: list[int] = []
        for first in range(m):
            branches: dict[tuple[int, ...], list[_Atom]] = defaultdict(list)
            for atom in group:
                branches[_second_observation(atom, protocol, first)].append(atom)
            value = 0
            for history, branch in branches.items():
                if history[-1] == 1:
                    second = 0
                    value += sum(a.mass for a in branch)
                else:
                    scores = [0] * m
                    for atom in branch:
                        if receiver == "individual_map" or not atom.a_covers:
                            scores[atom.target] += atom.mass
                    second = scores.index(max(scores))
                    value += sum(a.mass for a in branch if a.a_covers or a.target == second)
                second_policy[_key(history)] = second
            continuation_values.append(value)
        objective = immediate if receiver == "individual_map" else continuation_values
        chosen = objective.index(max(objective))
        first_policy[_key(observation)] = chosen
        total += continuation_values[chosen]
    return total, {"first": first_policy, "second": second_policy}


def _primary_execute(atoms: list[_Atom], protocol: str, policy: dict[str, Any]) -> int:
    total = 0
    for atom in atoms:
        first = policy["first"][_key(_first_observation(atom, protocol))]
        second = policy["second"][_key(_second_observation(atom, protocol, first))]
        if atom.a_covers or atom.target in (first, second):
            total += atom.mass
    return total


def _emulate(event: str, policy: dict[str, Any], augmented: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {"first": {}, "second": {}}
    for key in augmented["first"]:
        y, _early, x, c = (int(v) for v in key.split("|"))
        virtual_early = c if event == "agreement_trigger" else 1 - c
        virtual = _key((y, virtual_early, x if virtual_early else -1, c))
        result["first"][key] = policy["first"][virtual]
    for key in augmented["second"]:
        y, _early, x, c, first, hit = (int(v) for v in key.split("|"))
        virtual_early = c if event == "agreement_trigger" else 1 - c
        result["second"][key] = policy["second"][_key((y, virtual_early, x, c, first, hit))]
    return result


def run(config: dict[str, Any]) -> dict[str, Any]:
    """Evaluate the declared grid; call only through the registered primary runner."""
    cells = _cells(config)
    rows: list[dict[str, Any]] = []
    channels: dict[str, Any] = {}
    policies: dict[str, Any] = {}
    senders: dict[str, Any] = {}
    comparisons: list[dict[str, Any]] = []
    emulations: list[dict[str, Any]] = []
    restriction_gaps: list[dict[str, Any]] = []
    for m, p, q in cells:
        cell = _cell_id(m, p, q)
        sources, denominator, sender = _primary_sources(m, p, q)
        senders[cell] = sender
        alpha = p * q + (1 - p) * (1 - q) / (m - 1)
        values: dict[tuple[str, str], Fraction] = {}
        timed: dict[str, tuple[list[_Atom], int]] = {}
        for protocol in PROTOCOLS:
            atoms, timed_denominator = _timed_atoms(sources, denominator, protocol, alpha)
            timed[protocol] = (atoms, timed_denominator)
            channel_id = f"{cell}/{protocol}"
            channels[channel_id] = _primary_channel(
                atoms, timed_denominator, protocol, m, len(sources), alpha
            )
            for receiver in RECEIVERS:
                numerator, policy = _optimize(atoms, m, protocol, receiver)
                if numerator != _primary_execute(atoms, protocol, policy):
                    raise ValueError("Primary policy execution disagrees with backward induction")
                value = Fraction(numerator, timed_denominator)
                row_id = f"{channel_id}/{receiver}"
                values[protocol, receiver] = value
                policies[row_id] = policy
                rows.append(
                    {
                        "id": row_id,
                        "cell_id": cell,
                        "m": m,
                        "p": _fraction(p),
                        "q": _fraction(q),
                        "protocol": protocol,
                        "receiver": receiver,
                        "value": _fraction(value),
                        "policy_id": row_id,
                        "channel_id": channel_id,
                    }
                )
        for event in EVENTS:
            yoked = "yoked_agreement" if event == "agreement_trigger" else "yoked_disagreement"
            contrasts: dict[str, tuple[Fraction, Fraction]] = {}
            for receiver in RECEIVERS:
                event_id = f"{cell}/{event}/{receiver}"
                augmented_id = f"{cell}/early_augmented/{receiver}"
                emulated = _emulate(event, policies[event_id], policies[augmented_id])
                atoms, augmented_denominator = timed["early_augmented"]
                emulated_value = Fraction(
                    _primary_execute(atoms, "early_augmented", emulated), augmented_denominator
                )
                emulation_id = f"{event_id}/emulated_early_augmented"
                policies[emulation_id] = emulated
                event_value = values[event, receiver]
                augmented_value = values["early_augmented", receiver]
                if emulated_value != event_value:
                    raise ValueError(
                        "Event policy did not emulate under early augmented information"
                    )
                if receiver == "coverage_aware" and event_value > augmented_value:
                    raise ValueError("Positive coverage-aware transcript-matched residual")
                emulations.append(
                    {
                        "id": emulation_id,
                        "cell_id": cell,
                        "event_protocol": event,
                        "receiver": receiver,
                        "value": _fraction(emulated_value),
                        "policy_id": emulation_id,
                        "base_row_id": event_id,
                        "channel_id": f"{cell}/early_augmented",
                    }
                )
                best_fixed = max(values["early", receiver], values["late", receiver])
                apparent, timing_matched = (
                    event_value - best_fixed,
                    event_value - values[yoked, receiver],
                )
                contrasts[receiver] = (apparent, timing_matched)
                comparisons.append(
                    {
                        "id": event_id,
                        "cell_id": cell,
                        "event_protocol": event,
                        "receiver": receiver,
                        "event_value": _fraction(event_value),
                        "best_fixed_value": _fraction(best_fixed),
                        "yoked_value": _fraction(values[yoked, receiver]),
                        "early_augmented_value": _fraction(augmented_value),
                        "apparent_timing_gain": _fraction(apparent),
                        "timing_matched_contrast": _fraction(timing_matched),
                        "transcript_matched_residual": _fraction(event_value - augmented_value),
                        "emulation_difference": _fraction(emulated_value - event_value),
                    }
                )
            restriction_gaps.append(
                {
                    "cell_id": cell,
                    "event_protocol": event,
                    "map_minus_coverage_apparent_gain": _fraction(
                        contrasts["individual_map"][0] - contrasts["coverage_aware"][0]
                    ),
                    "map_minus_coverage_timing_matched": _fraction(
                        contrasts["individual_map"][1] - contrasts["coverage_aware"][1]
                    ),
                }
            )
    coverage_residuals = [
        Fraction(c["transcript_matched_residual"])
        for c in comparisons
        if c["receiver"] == "coverage_aware"
    ]
    return {
        "schema_version": "dd024-timing-result-v1",
        "study_id": "DD-024",
        "track_id": "track-04",
        "rows": rows,
        "channels": channels,
        "saved_policies": policies,
        "sender_policies": senders,
        "comparisons": comparisons,
        "emulations": emulations,
        "policy_restriction_gaps": restriction_gaps,
        "summary": {
            "cell_count": len(cells),
            "base_row_count": len(rows),
            "emulation_count": len(emulations),
            "comparison_count": len(comparisons),
            "saved_policy_count": len(policies),
            "max_coverage_transcript_residual": _fraction(max(coverage_residuals)),
            "positive_coverage_transcript_residual_count": sum(v > 0 for v in coverage_residuals),
        },
    }


# Everything below rebuilds scientific probabilities/observations independently.
@dataclass(frozen=True, slots=True)
class _RawSource:
    t: int
    x: int
    z: int
    y: int
    probability: Fraction
    sender_hit: bool


@dataclass(frozen=True, slots=True)
class _RawWorld:
    t: int
    x: int
    z: int
    y: int
    early: int
    weight: int
    sender_hit: bool
    initial: str
    final_prefix: tuple[int, ...]


def _independent_sources(
    m: int, p: Fraction, q: Fraction
) -> tuple[list[_RawSource], dict[str, Any], Fraction, bool]:
    def likelihood(observed: int, target: int, accuracy: Fraction) -> Fraction:
        return accuracy if observed == target else (1 - accuracy) / (m - 1)

    sender: dict[str, Any] = {}
    for x in range(m):
        for z in range(m):
            posterior = [likelihood(x, t, p) * likelihood(z, t, q) for t in range(m)]
            first = min(t for t in range(m) if posterior[t] == max(posterior))
            remaining = [t for t in range(m) if t != first]
            best_remaining = max(posterior[t] for t in remaining)
            second = min(t for t in remaining if posterior[t] == best_remaining)
            sender[f"{x}|{z}"] = {
                "first": first,
                "second_after_failure": second,
                "second_after_success": 0,
            }
    raw: list[_RawSource] = []
    probability_by_labels: dict[tuple[int, ...], Fraction] = {}
    agreement = Fraction(0)
    for t, x, z, y in product(range(m), repeat=4):
        probability = Fraction(1, m)
        for observed, accuracy in ((x, p), (z, q), (y, p)):
            probability *= likelihood(observed, t, accuracy)
        probability_by_labels[t, x, z, y] = probability
        if not probability:
            continue
        a = sender[f"{x}|{z}"]
        a_second = 0 if a["first"] == t else a["second_after_failure"]
        raw.append(_RawSource(t, x, z, y, probability, t in (a["first"], a_second)))
        if x == z:
            agreement += probability
    if sum((w.probability for w in raw), Fraction(0)) != 1:
        raise ValueError("Independent source mass is not one")
    symmetry = all(
        probability_by_labels[tuple((v + 1) % m for v in labels)] == probability
        for labels, probability in probability_by_labels.items()
    )
    return raw, sender, agreement, symmetry


def _independent_worlds(
    sources: list[_RawSource], protocol: str, agreement: Fraction
) -> tuple[list[_RawWorld], int]:
    expanded: list[tuple[_RawSource, int, Fraction]] = []
    for source in sources:
        choices: tuple[tuple[int, Fraction], ...]
        if protocol == "yoked_agreement":
            choices = ((0, 1 - agreement), (1, agreement))
        elif protocol == "yoked_disagreement":
            choices = ((0, agreement), (1, 1 - agreement))
        elif protocol == "agreement_trigger":
            choices = ((int(source.x == source.z), Fraction(1)),)
        elif protocol == "disagreement_trigger":
            choices = ((int(source.x != source.z), Fraction(1)),)
        elif protocol in ("early", "early_augmented"):
            choices = ((1, Fraction(1)),)
        else:
            choices = ((0, Fraction(1)),)
        for early, probability in choices:
            if probability:
                expanded.append((source, early, source.probability * probability))
    denominator = lcm(*(probability.denominator for _, _, probability in expanded))
    worlds: list[_RawWorld] = []
    for source, early, probability in expanded:
        # The event bit here is inferred from observed time, not read as a free payload.
        if protocol == "agreement_trigger":
            first_c = final_c = early
        elif protocol == "disagreement_trigger":
            first_c = final_c = 1 - early
        elif protocol in ("early_augmented", "late_augmented"):
            final_c = int(source.x == source.z)
            first_c = final_c if early else -1
        else:
            first_c = final_c = -1
        seen_x = source.x if early else -1
        initial = f"{source.y}|{early}|{seen_x}|{first_c}"
        prefix = (source.y, early, source.x, final_c)
        weight = probability.numerator * (denominator // probability.denominator)
        worlds.append(
            _RawWorld(
                source.t,
                source.x,
                source.z,
                source.y,
                early,
                weight,
                source.sender_hit,
                initial,
                prefix,
            )
        )
    return worlds, denominator


def _independent_channel(
    worlds: list[_RawWorld],
    denominator: int,
    protocol: str,
    m: int,
    source_count: int,
    agreement: Fraction,
) -> dict[str, Any]:
    target_counts: dict[str, list[int]] = defaultdict(lambda: [0] * m)
    packets: set[tuple[int, ...]] = set()
    transcripts: set[tuple[int, ...]] = set()
    arrival_weight = 0
    for world in worlds:
        target_counts[world.initial][world.t] += world.weight
        payload = (
            (world.x, int(world.x == world.z))
            if protocol in ("early_augmented", "late_augmented")
            else (world.x,)
        )
        packets.add(payload)
        transcripts.add((world.early, *payload))
        arrival_weight += world.early * world.weight
    first_information: dict[str, Any] = {}
    for key, counts in sorted(target_counts.items()):
        first_information[key] = {
            "mass": _fraction(Fraction(sum(counts), denominator)),
            "target_masses": [_fraction(Fraction(count, denominator)) for count in counts],
        }
    augmented = protocol in ("early_augmented", "late_augmented")
    return {
        "protocol": protocol,
        "trigger_early_on": {"agreement_trigger": 1, "disagreement_trigger": 0}.get(protocol),
        "arrival_probability": _fraction(Fraction(arrival_weight, denominator)),
        "agreement_probability": _fraction(agreement),
        "payload_fields": ["X", "C"] if augmented else ["X"],
        "payload_alphabet_max": m * (2 if augmented else 1),
        "transcript_alphabet_max": m * (1 if protocol in ("early", "late") else 2),
        "reached_payload_symbols": len(packets),
        "reached_transcript_symbols": len(transcripts),
        "positive_source_worlds": source_count,
        "zero_mass_source_worlds": m**4 - source_count,
        "positive_timed_worlds": len(worlds),
        "probability_mass": "1/1",
        "clue_budget": 3,
        "action_budget": 4,
        "packet_budget": 1,
        "first_information": first_information,
    }


def _raw_second_key(world: _RawWorld, first: int) -> str:
    values = (*world.final_prefix, first, int(world.t == first))
    return "|".join(map(str, values))


def _audit_saved_policy(
    worlds: list[_RawWorld], m: int, policy: dict[str, Any], receiver: str | None
) -> tuple[int, int, bool]:
    first_table, second_table = policy["first"], policy["second"]
    initial: dict[str, list[_RawWorld]] = defaultdict(list)
    continuations: dict[str, list[_RawWorld]] = defaultdict(list)
    for world in worlds:
        initial[world.initial].append(world)
        for first in range(m):
            continuations[_raw_second_key(world, first)].append(world)
    if set(first_table) != set(initial) or set(second_table) != set(continuations):
        raise ValueError("Saved policy omits a positive-mass history or adds an alien history")
    if any(
        type(action) is not int or not 0 <= action < m
        for table in (first_table, second_table)
        for action in table.values()
    ):
        raise ValueError("Saved policy contains an invalid action")
    deviations = 0
    for key, branch in continuations.items():
        is_hit = key.endswith("|1")
        chosen = second_table[key]
        if is_hit:
            if chosen != 0:
                raise ValueError("Second action after success violates its declared default")
            continue
        if receiver is None:
            continue
        scores = [0] * m
        for world in branch:
            if receiver == "coverage_aware" and world.sender_hit:
                for action in range(m):
                    scores[action] += world.weight
            else:
                scores[world.t] += world.weight
        best = min(action for action in range(m) if scores[action] == max(scores))
        deviations += m
        if chosen != best:
            raise ValueError("Second-stage local deviation or tie-break violation")
    for key, branch in initial.items():
        if receiver is None:
            continue
        scores = [0] * m
        for first in range(m):
            for world in branch:
                if receiver == "individual_map":
                    success = world.t == first
                else:
                    second = second_table[_raw_second_key(world, first)]
                    success = world.sender_hit or world.t == first or world.t == second
                if success:
                    scores[first] += world.weight
        best = min(action for action in range(m) if scores[action] == max(scores))
        deviations += m
        if first_table[key] != best:
            raise ValueError("First-stage local deviation or tie-break violation")
    value = 0
    relabeled_value = 0
    for world in worlds:
        first = first_table[world.initial]
        second = second_table[_raw_second_key(world, first)]
        success = world.sender_hit or world.t == first or world.t == second
        value += world.weight * success
        shifted_target = (world.t + 1) % m
        relabeled_value += world.weight * (
            world.sender_hit or shifted_target in ((first + 1) % m, (second + 1) % m)
        )
    return value, deviations, value == relabeled_value


def _channel_matches(observed: dict[str, Any], expected: dict[str, Any]) -> bool:
    return observed == expected


def _corruption_checks(config: dict[str, Any], result: dict[str, Any]) -> dict[str, bool]:
    """Send damaged one-cell artifacts through the substantive verifier path."""
    first = result["rows"][0]
    cell = first["cell_id"]
    fixture_config = deepcopy(config)
    fixture_config.update(target_counts=[first["m"]], p_values=[first["p"]], q_values=[first["q"]])
    rows = [row for row in result["rows"] if row["cell_id"] == cell]
    emulations = [row for row in result["emulations"] if row["cell_id"] == cell]
    comparisons = [row for row in result["comparisons"] if row["cell_id"] == cell]
    policy_ids = {row["policy_id"] for row in rows + emulations}
    residuals = [
        Fraction(row["transcript_matched_residual"])
        for row in comparisons
        if row["receiver"] == "coverage_aware"
    ]
    fixture = deepcopy(
        {
            "schema_version": result["schema_version"],
            "study_id": result["study_id"],
            "track_id": result["track_id"],
            "rows": rows,
            "emulations": emulations,
            "comparisons": comparisons,
            "channels": {
                key: value
                for key, value in result["channels"].items()
                if key.startswith(f"{cell}/")
            },
            "saved_policies": {key: result["saved_policies"][key] for key in policy_ids},
            "sender_policies": {cell: result["sender_policies"][cell]},
            "policy_restriction_gaps": [
                row for row in result["policy_restriction_gaps"] if row["cell_id"] == cell
            ],
            "summary": {
                "cell_count": 1,
                "base_row_count": 16,
                "emulation_count": 4,
                "comparison_count": 4,
                "saved_policy_count": 20,
                "max_coverage_transcript_residual": _fraction(max(residuals)),
                "positive_coverage_transcript_residual_count": sum(
                    value > 0 for value in residuals
                ),
            },
        }
    )
    # A valid control prevents missing fixture data from masquerading as rejection.
    baseline = _verify(fixture_config, fixture, exercise_corruptions=False)
    if not baseline["passed"]:
        raise ValueError(f"Uncorrupted one-cell verification fixture failed: {baseline['errors']}")
    rejected: dict[str, bool] = {}
    for name in ("trigger", "arrival", "silence_likelihood", "payload_alphabet", "value"):
        damaged = deepcopy(fixture)
        channel = damaged["channels"][f"{cell}/agreement_trigger"]
        if name == "trigger":
            channel["trigger_early_on"] = 1 - channel["trigger_early_on"]
        elif name == "arrival":
            channel["arrival_probability"] = _fraction(
                Fraction(channel["arrival_probability"]) + Fraction(1, 101)
            )
        elif name == "silence_likelihood":
            silent = [key for key in channel["first_information"] if key.split("|")[1] == "0"]
            if silent:
                entry = channel["first_information"][silent[0]]["target_masses"]
                entry[0] = _fraction(Fraction(entry[0]) + Fraction(1, 101))
            else:
                # A deterministic all-early cell must reject invented silence.
                channel["first_information"]["0|0|-1|0"] = {"mass": "1/101", "target_masses": []}
        elif name == "payload_alphabet":
            channel["payload_alphabet_max"] += 1
        else:
            value = Fraction(damaged["rows"][0]["value"]) + Fraction(1, 101)
            damaged["rows"][0]["value"] = _fraction(value)
        audit = _verify(fixture_config, damaged, exercise_corruptions=False)
        reason = (
            "saved value or row metadata"
            if name == "value"
            else "timing, silence, payload, or probability mismatch"
        )
        rejected[name] = not audit["passed"] and any(reason in error for error in audit["errors"])
    return rejected


def _verify(
    config: dict[str, Any], result: dict[str, Any], *, exercise_corruptions: bool
) -> dict[str, Any]:
    """Actual audit path; fixture calls disable only recursive negative controls."""
    errors: list[str] = []
    checks: dict[str, Any] = {
        "raw_rows": 0,
        "local_deviations": 0,
        "emulations": 0,
        "source_label_symmetry": True,
        "policy_label_conjugation": True,
    }
    corruptions: dict[str, bool] = {}
    try:
        cells = _cells(config)
        if (result.get("schema_version"), result.get("study_id"), result.get("track_id")) != (
            "dd024-timing-result-v1",
            "DD-024",
            "track-04",
        ):
            raise ValueError("Result identity/schema mismatch")
        row_map = {row["id"]: row for row in result["rows"]}
        emulation_map = {row["id"]: row for row in result["emulations"]}
        comparison_map = {row["id"]: row for row in result["comparisons"]}
        if (
            len(row_map) != len(cells) * 16
            or len(result["rows"]) != len(row_map)
            or len(emulation_map) != len(cells) * 4
            or len(result["emulations"]) != len(emulation_map)
            or len(comparison_map) != len(cells) * 4
            or len(result["comparisons"]) != len(comparison_map)
            or len(result["channels"]) != len(cells) * 8
            or len(result["saved_policies"]) != len(cells) * 20
            or len(result["sender_policies"]) != len(cells)
        ):
            raise ValueError("Incomplete, duplicated, or expanded result grid")
        residuals: list[Fraction] = []
        expected_restrictions: list[dict[str, Any]] = []
        for m, p, q in cells:
            cell = _cell_id(m, p, q)
            sources, sender, agreement, symmetry = _independent_sources(m, p, q)
            if result["sender_policies"][cell] != sender:
                raise ValueError(f"{cell}: sender policy differs from fixed Bayesian rule")
            checks["source_label_symmetry"] &= symmetry
            raw: dict[str, tuple[list[_RawWorld], int]] = {}
            values: dict[tuple[str, str], Fraction] = {}
            for protocol in PROTOCOLS:
                worlds, denominator = _independent_worlds(sources, protocol, agreement)
                raw[protocol] = (worlds, denominator)
                if sum(world.weight for world in worlds) != denominator:
                    raise ValueError("Independent timed-world mass is not one")
                expected_channel = _independent_channel(
                    worlds, denominator, protocol, m, len(sources), agreement
                )
                channel_id = f"{cell}/{protocol}"
                if not _channel_matches(result["channels"][channel_id], expected_channel):
                    raise ValueError(
                        f"{channel_id}: timing, silence, payload, or probability mismatch"
                    )
                for receiver in RECEIVERS:
                    row_id = f"{channel_id}/{receiver}"
                    policy = result["saved_policies"][row_id]
                    total, deviations, conjugation = _audit_saved_policy(
                        worlds, m, policy, receiver
                    )
                    value = Fraction(total, denominator)
                    expected_row = {
                        "id": row_id,
                        "cell_id": cell,
                        "m": m,
                        "p": _fraction(p),
                        "q": _fraction(q),
                        "protocol": protocol,
                        "receiver": receiver,
                        "value": _fraction(value),
                        "policy_id": row_id,
                        "channel_id": channel_id,
                    }
                    if row_map[row_id] != expected_row or not 0 <= value <= 1:
                        raise ValueError(
                            f"{row_id}: saved value or row metadata disagrees with raw worlds"
                        )
                    checks["raw_rows"] += 1
                    checks["local_deviations"] += deviations
                    checks["policy_label_conjugation"] &= conjugation
                    values[protocol, receiver] = value
            for event in EVENTS:
                yoked = "yoked_agreement" if event == "agreement_trigger" else "yoked_disagreement"
                contrasts: dict[str, tuple[Fraction, Fraction]] = {}
                for receiver in RECEIVERS:
                    event_id = f"{cell}/{event}/{receiver}"
                    emulation_id = f"{event_id}/emulated_early_augmented"
                    policy = result["saved_policies"][emulation_id]
                    event_policy = result["saved_policies"][event_id]
                    # Check the emulation mapping itself, not only coincidentally equal payoffs.
                    for key, action in policy["first"].items():
                        y, _early, x, c = [int(item) for item in key.split("|")]
                        arrival = int(c == (1 if event == "agreement_trigger" else 0))
                        history = f"{y}|{arrival}|{x if arrival else -1}|{c}"
                        if action != event_policy["first"][history]:
                            raise ValueError("First-stage event emulation mapping mismatch")
                    for key, action in policy["second"].items():
                        y, _early, x, c, first, hit = [int(item) for item in key.split("|")]
                        arrival = int(c == (1 if event == "agreement_trigger" else 0))
                        history = f"{y}|{arrival}|{x}|{c}|{first}|{hit}"
                        if action != event_policy["second"][history]:
                            raise ValueError("Second-stage event emulation mapping mismatch")
                    worlds, denominator = raw["early_augmented"]
                    total, _deviations, conjugation = _audit_saved_policy(worlds, m, policy, None)
                    emulated = Fraction(total, denominator)
                    if emulated != values[event, receiver]:
                        raise ValueError("Independent event emulation value mismatch")
                    expected_emulation = {
                        "id": emulation_id,
                        "cell_id": cell,
                        "event_protocol": event,
                        "receiver": receiver,
                        "value": _fraction(emulated),
                        "policy_id": emulation_id,
                        "base_row_id": event_id,
                        "channel_id": f"{cell}/early_augmented",
                    }
                    if emulation_map[emulation_id] != expected_emulation:
                        raise ValueError("Emulation record mismatch")
                    checks["emulations"] += 1
                    checks["policy_label_conjugation"] &= conjugation
                    best_fixed = max(values["early", receiver], values["late", receiver])
                    event_value, augmented = (
                        values[event, receiver],
                        values["early_augmented", receiver],
                    )
                    apparent, timing = (
                        event_value - best_fixed,
                        event_value - values[yoked, receiver],
                    )
                    residual = event_value - augmented
                    contrasts[receiver] = (apparent, timing)
                    expected_comparison = {
                        "id": event_id,
                        "cell_id": cell,
                        "event_protocol": event,
                        "receiver": receiver,
                        "event_value": _fraction(event_value),
                        "best_fixed_value": _fraction(best_fixed),
                        "yoked_value": _fraction(values[yoked, receiver]),
                        "early_augmented_value": _fraction(augmented),
                        "apparent_timing_gain": _fraction(apparent),
                        "timing_matched_contrast": _fraction(timing),
                        "transcript_matched_residual": _fraction(residual),
                        "emulation_difference": "0/1",
                    }
                    if comparison_map[event_id] != expected_comparison:
                        raise ValueError(
                            "Reported comparison differs from independently verified values"
                        )
                    if receiver == "coverage_aware":
                        residuals.append(residual)
                        if residual > 0:
                            raise ValueError("Early augmented coverage weak-dominance failure")
                expected_restrictions.append(
                    {
                        "cell_id": cell,
                        "event_protocol": event,
                        "map_minus_coverage_apparent_gain": _fraction(
                            contrasts["individual_map"][0] - contrasts["coverage_aware"][0]
                        ),
                        "map_minus_coverage_timing_matched": _fraction(
                            contrasts["individual_map"][1] - contrasts["coverage_aware"][1]
                        ),
                    }
                )
        if result["policy_restriction_gaps"] != expected_restrictions:
            raise ValueError("Policy restriction contrast mismatch")
        expected_summary = {
            "cell_count": len(cells),
            "base_row_count": len(cells) * 16,
            "emulation_count": len(cells) * 4,
            "comparison_count": len(cells) * 4,
            "saved_policy_count": len(cells) * 20,
            "max_coverage_transcript_residual": _fraction(max(residuals)),
            "positive_coverage_transcript_residual_count": sum(v > 0 for v in residuals),
        }
        if result["summary"] != expected_summary:
            raise ValueError("Summary does not match raw-world verification")
        if exercise_corruptions:
            corruptions = _corruption_checks(config, result)
            if not all(corruptions.values()):
                raise ValueError("A required validation corruption was not rejected")
        if not checks["source_label_symmetry"] or not checks["policy_label_conjugation"]:
            raise ValueError("Label conjugation check failed")
    except (KeyError, TypeError, ValueError, IndexError, ZeroDivisionError) as error:
        errors.append(str(error))
    return {"passed": not errors, "checks": checks, "errors": errors, "corruptions": corruptions}


def verify(config: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    """Independently audit saved decisions and genuinely reject five corruptions."""
    return _verify(config, result, exercise_corruptions=True)
