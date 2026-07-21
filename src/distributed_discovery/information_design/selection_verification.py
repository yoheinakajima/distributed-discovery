"""Independent exact verifier for DD-002 selection-robustness certificates."""

from __future__ import annotations

from fractions import Fraction
from typing import Any

Profile = tuple[int, int]
Partition = tuple[tuple[int, ...], ...]


def _partitions(size: int) -> tuple[Partition, ...]:
    result: list[Partition] = []

    def extend(item: int, blocks: list[list[int]]) -> None:
        if item == size:
            result.append(tuple(tuple(block) for block in blocks))
            return
        for index in range(len(blocks)):
            blocks[index].append(item)
            extend(item + 1, blocks)
            blocks[index].pop()
        blocks.append([item])
        extend(item + 1, blocks)
        blocks.pop()

    extend(0, [])
    return tuple(result)


def _profile(value: object) -> Profile:
    if (
        not isinstance(value, list)
        or len(value) != 2
        or any(not isinstance(action, int) or isinstance(action, bool) for action in value)
    ):
        raise ValueError("invalid profile")
    return value[0], value[1]


def _fraction(value: object) -> Fraction:
    if not isinstance(value, str):
        raise ValueError("exact value must be a fraction string")
    return Fraction(value)


def _posterior(
    likelihood: tuple[tuple[Fraction, ...], ...], block: tuple[int, ...]
) -> tuple[Fraction, tuple[Fraction, ...]]:
    targets = len(likelihood)
    joint = tuple(
        sum((likelihood[target][state] for state in block), start=Fraction(0)) / targets
        for target in range(targets)
    )
    weight = sum(joint, start=Fraction(0))
    return weight, tuple(value / weight for value in joint)


def _payoff(posterior: tuple[Fraction, ...], profile: Profile, player: int) -> Fraction:
    action = profile[player]
    return posterior[action] / (2 if action == profile[1 - player] else 1)


def _discovery(posterior: tuple[Fraction, ...], profile: Profile) -> Fraction:
    first, second = profile
    return posterior[first] if first == second else posterior[first] + posterior[second]


def _potential(posterior: tuple[Fraction, ...], profile: Profile) -> Fraction:
    first, second = profile
    return (
        Fraction(3, 2) * posterior[first]
        if first == second
        else posterior[first] + posterior[second]
    )


def _pure_equilibria(posterior: tuple[Fraction, ...]) -> tuple[Profile, ...]:
    profiles: tuple[Profile, ...] = tuple(
        (first, second) for first in range(len(posterior)) for second in range(len(posterior))
    )
    result = []
    for profile in profiles:
        if all(
            _payoff(posterior, profile, player)
            >= max(
                _payoff(
                    posterior,
                    (
                        action if player == 0 else profile[0],
                        action if player == 1 else profile[1],
                    ),
                    player,
                )
                for action in range(len(posterior))
            )
            for player in (0, 1)
        ):
            result.append(profile)
    return tuple(result)


def _moves(posterior: tuple[Fraction, ...], profile: Profile) -> tuple[Profile, ...]:
    result: list[Profile] = []
    for player in (0, 1):
        alternatives = []
        for action in range(len(posterior)):
            updated: Profile = (
                action if player == 0 else profile[0],
                action if player == 1 else profile[1],
            )
            alternatives.append((updated, _payoff(posterior, updated, player)))
        maximum = max(payoff for _, payoff in alternatives)
        current = _payoff(posterior, profile, player)
        if maximum > current:
            result.extend(updated for updated, payoff in alternatives if payoff == maximum)
    return tuple(result)


def _distribution(value: object) -> dict[Profile, Fraction]:
    if not isinstance(value, list):
        raise ValueError("absorption distribution must be a list")
    result: dict[Profile, Fraction] = {}
    for record in value:
        if not isinstance(record, dict):
            raise ValueError("absorption record must be an object")
        terminal = _profile(record["terminal"])
        if terminal in result:
            raise ValueError("duplicate absorption terminal")
        result[terminal] = _fraction(record["probability"])
    return result


def _refines(finer: Partition, coarser: Partition) -> bool:
    membership = {state: index for index, block in enumerate(coarser) for state in block}
    return all(len({membership[state] for state in block}) == 1 for block in finer)


def verify_selection_certificate(certificate: dict[str, Any]) -> list[str]:
    """Check games, potential identities, Bellman witnesses, and all aggregates."""

    errors: list[str] = []
    try:
        if certificate.get("schema_version") != 1:
            errors.append("unsupported schema version")
        raw_likelihood = certificate["likelihood"]
        if not isinstance(raw_likelihood, list):
            raise ValueError("likelihood must be a list")
        likelihood = tuple(
            tuple(_fraction(value) for value in row)
            for row in raw_likelihood
            if isinstance(row, list)
        )
        if len(likelihood) != 3 or any(len(row) != 4 for row in likelihood):
            errors.append("likelihood dimensions must be three by four")
            return errors
        if any(sum(row, start=Fraction(0)) != 1 for row in likelihood):
            errors.append("likelihood rows do not normalize")
        expected_partitions = _partitions(4)
        raw_partitions = certificate["partitions"]
        if not isinstance(raw_partitions, list) or len(raw_partitions) != 15:
            errors.append("certificate must contain all 15 partitions")
            return errors

        profiles: tuple[Profile, ...] = tuple(
            (first, second) for first in range(3) for second in range(3)
        )
        computed_partitions: dict[str, tuple[Partition, dict[str, Fraction]]] = {}
        for index, (raw_partition, expected_partition) in enumerate(
            zip(raw_partitions, expected_partitions, strict=True)
        ):
            if not isinstance(raw_partition, dict):
                raise ValueError("partition record must be an object")
            partition_id = raw_partition["partition_id"]
            if partition_id != f"P{index:02d}":
                errors.append(f"partition id mismatch at {index}")
            partition = tuple(tuple(block) for block in raw_partition["partition"])
            if partition != expected_partition:
                errors.append(f"canonical partition mismatch at {partition_id}")
            raw_messages = raw_partition["messages"]
            if not isinstance(raw_messages, list) or len(raw_messages) != len(partition):
                errors.append(f"message count mismatch at {partition_id}")
                continue
            values = {
                "anonymous_symmetric": Fraction(0),
                "best_pure": Fraction(0),
                "worst_pure": Fraction(0),
                "uniform_potential_maximum": Fraction(0),
                "uniform_strict_best_response_basin": Fraction(0),
                "planner": Fraction(0),
            }
            tied_count = 0
            potential_multiple = False
            partition_branch = False
            for message_index, (block, raw_message) in enumerate(
                zip(partition, raw_messages, strict=True)
            ):
                if not isinstance(raw_message, dict):
                    raise ValueError("message record must be an object")
                label = f"{partition_id}:{message_index}"
                if tuple(raw_message["block"]) != block:
                    errors.append(f"message block mismatch at {label}")
                weight, posterior = _posterior(likelihood, block)
                stored_posterior = tuple(_fraction(value) for value in raw_message["posterior"])
                if weight != _fraction(raw_message["weight"]) or posterior != stored_posterior:
                    errors.append(f"posterior mismatch at {label}")

                pure = _pure_equilibria(posterior)
                stored_pure = tuple(
                    _profile(value) for value in raw_message["pure_equilibrium_profiles"]
                )
                if pure != stored_pure:
                    errors.append(f"pure correspondence mismatch at {label}")
                pure_discovery = tuple(_discovery(posterior, profile) for profile in pure)
                best_pure = max(pure_discovery)
                worst_pure = min(pure_discovery)
                if best_pure != _fraction(raw_message["best_pure_discovery"]):
                    errors.append(f"best-pure mismatch at {label}")
                if worst_pure != _fraction(raw_message["worst_pure_discovery"]):
                    errors.append(f"worst-pure mismatch at {label}")

                for profile in profiles:
                    for player in (0, 1):
                        for action in range(3):
                            updated: Profile = (
                                action if player == 0 else profile[0],
                                action if player == 1 else profile[1],
                            )
                            if _payoff(posterior, updated, player) - _payoff(
                                posterior, profile, player
                            ) != _potential(posterior, updated) - _potential(posterior, profile):
                                errors.append(f"exact-potential identity fails at {label}")
                maximum = max(_potential(posterior, profile) for profile in profiles)
                maximizers = tuple(
                    profile for profile in profiles if _potential(posterior, profile) == maximum
                )
                stored_maximizers = tuple(
                    _profile(value) for value in raw_message["potential_maximizers"]
                )
                if maximum != _fraction(raw_message["potential_maximum"]):
                    errors.append(f"potential maximum mismatch at {label}")
                if maximizers != stored_maximizers or any(
                    profile not in pure for profile in maximizers
                ):
                    errors.append(f"potential maximizer mismatch at {label}")
                potential_discovery = sum(
                    (_discovery(posterior, profile) for profile in maximizers), start=Fraction(0)
                ) / len(maximizers)
                if potential_discovery != _fraction(raw_message["potential_discovery"]):
                    errors.append(f"potential discovery mismatch at {label}")
                tied_count += len(maximizers)
                potential_multiple |= (
                    len({_discovery(posterior, profile) for profile in maximizers}) > 1
                )

                anonymous = raw_message["anonymous_symmetric"]
                strategy = tuple(_fraction(value) for value in anonymous["strategy"])
                if len(strategy) != 3 or any(value < 0 for value in strategy) or sum(strategy) != 1:
                    errors.append(f"invalid anonymous strategy at {label}")
                action_payoffs = tuple(
                    posterior[action] * (1 - strategy[action] / 2) for action in range(3)
                )
                payoff_maximum = max(action_payoffs)
                if not all(
                    action_payoffs[action] == payoff_maximum
                    if strategy[action] > 0
                    else action_payoffs[action] <= payoff_maximum
                    for action in range(3)
                ):
                    errors.append(f"anonymous best-response condition fails at {label}")
                anonymous_discovery = sum(
                    (
                        posterior[action]
                        * (2 * strategy[action] - strategy[action] * strategy[action])
                        for action in range(3)
                    ),
                    start=Fraction(0),
                )
                if anonymous_discovery != _fraction(anonymous["discovery"]):
                    errors.append(f"anonymous discovery mismatch at {label}")

                raw_moves = raw_message["best_response_moves"]
                move_map = {
                    _profile(record["profile"]): tuple(_profile(move) for move in record["moves"])
                    for record in raw_moves
                }
                expected_moves = {profile: _moves(posterior, profile) for profile in profiles}
                if move_map != expected_moves:
                    errors.append(f"strict best-response transitions mismatch at {label}")
                if any(
                    _potential(posterior, move) <= _potential(posterior, profile)
                    for profile, moves in expected_moves.items()
                    for move in moves
                ):
                    errors.append(f"best-response potential does not increase at {label}")

                absorption_map = {
                    _profile(record["initial"]): _distribution(record["absorption"])
                    for record in raw_message["absorption_by_initial"]
                }
                if set(absorption_map) != set(profiles):
                    errors.append(f"absorption initial states mismatch at {label}")
                    continue
                for profile in profiles:
                    stored = absorption_map[profile]
                    if (
                        any(probability < 0 for probability in stored.values())
                        or sum(stored.values(), start=Fraction(0)) != 1
                    ):
                        errors.append(f"absorption distribution invalid at {label}:{profile}")
                    moves = expected_moves[profile]
                    expected_distribution: dict[Profile, Fraction]
                    if not moves:
                        expected_distribution = {profile: Fraction(1)}
                    else:
                        expected_distribution = {}
                        for move in moves:
                            for terminal, probability in absorption_map[move].items():
                                expected_distribution[terminal] = expected_distribution.get(
                                    terminal, Fraction(0)
                                ) + probability / len(moves)
                    if stored != expected_distribution:
                        errors.append(f"absorption Bellman equation fails at {label}:{profile}")
                terminal_distribution: dict[Profile, Fraction] = {}
                for distribution in absorption_map.values():
                    for terminal, probability in distribution.items():
                        terminal_distribution[terminal] = terminal_distribution.get(
                            terminal, Fraction(0)
                        ) + probability / len(profiles)
                stored_terminal = _distribution(raw_message["basin_terminal_distribution"])
                if terminal_distribution != stored_terminal:
                    errors.append(f"basin terminal distribution mismatch at {label}")
                if any(terminal not in pure for terminal in terminal_distribution):
                    errors.append(f"basin terminates outside pure equilibria at {label}")
                basin_discovery = sum(
                    (
                        probability * _discovery(posterior, terminal)
                        for terminal, probability in terminal_distribution.items()
                    ),
                    start=Fraction(0),
                )
                if basin_discovery != _fraction(raw_message["basin_discovery"]):
                    errors.append(f"basin discovery mismatch at {label}")
                branch = any(
                    len({_discovery(posterior, terminal) for terminal in distribution}) > 1
                    for distribution in absorption_map.values()
                )
                if branch is not raw_message["basin_branch_dependent"]:
                    errors.append(f"basin branch flag mismatch at {label}")
                partition_branch |= branch

                planner = sum(sorted(posterior, reverse=True)[:2], start=Fraction(0))
                if planner != _fraction(raw_message["planner_discovery"]):
                    errors.append(f"planner discovery mismatch at {label}")
                selected = {
                    "anonymous_symmetric": anonymous_discovery,
                    "best_pure": best_pure,
                    "worst_pure": worst_pure,
                    "uniform_potential_maximum": potential_discovery,
                    "uniform_strict_best_response_basin": basin_discovery,
                    "planner": planner,
                }
                for rule, value in selected.items():
                    values[rule] += weight * value

            stored_values = {
                rule: _fraction(value) for rule, value in raw_partition["values"].items()
            }
            if values != stored_values:
                errors.append(f"partition values mismatch at {partition_id}")
            if tied_count != raw_partition["potential_tied_profile_count"]:
                errors.append(f"potential tie count mismatch at {partition_id}")
            if potential_multiple is not raw_partition["potential_multiple_discovery_values"]:
                errors.append(f"potential multiplicity flag mismatch at {partition_id}")
            if partition_branch is not raw_partition["basin_branch_dependent"]:
                errors.append(f"partition branch flag mismatch at {partition_id}")
            computed_partitions[str(partition_id)] = (partition, values)

        computed_comparisons: dict[tuple[str, str], dict[str, Fraction]] = {}
        for finer_id, (finer, finer_values) in computed_partitions.items():
            for coarser_id, (coarser, coarser_values) in computed_partitions.items():
                if finer_id != coarser_id and _refines(finer, coarser):
                    computed_comparisons[(finer_id, coarser_id)] = {
                        rule: finer_values[rule] - coarser_values[rule] for rule in finer_values
                    }
        stored_comparisons = {
            (record["more_informative"], record["less_informative"]): {
                rule: _fraction(value) for rule, value in record["differences"].items()
            }
            for record in certificate["refinement_comparisons"]
        }
        if computed_comparisons != stored_comparisons or len(computed_comparisons) != 45:
            errors.append("refinement comparison registry mismatch")
        computed_counts = {
            rule: {
                "harmful": sum(values[rule] < 0 for values in computed_comparisons.values()),
                "improving": sum(values[rule] > 0 for values in computed_comparisons.values()),
                "tied": sum(values[rule] == 0 for values in computed_comparisons.values()),
            }
            for rule in next(iter(computed_comparisons.values()))
        }
        if computed_counts != certificate["refinement_counts"]:
            errors.append("refinement count summary mismatch")
    except (KeyError, TypeError, ValueError, ZeroDivisionError) as error:
        errors.append(f"malformed certificate: {error}")
    return errors
