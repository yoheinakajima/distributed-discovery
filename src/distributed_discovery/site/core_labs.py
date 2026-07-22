# ruff: noqa: E501
"""Presentation-only builders for the six pre-Program-V3 public Labs."""

from __future__ import annotations

import html
import itertools
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any

import yaml

REPOSITORY_URL = "https://github.com/yoheinakajima/distributed-discovery"
DD004_RUN = "20260721T050038Z_DD-004_8ab02e7f_71d84de7c4"
DD005_RUN = "20260721T050706Z_DD-005_be3b544c_98698dee2f"
DD006_RUN = "20260721T051457Z_DD-006_d49a50ea_068bce4af3"
DD006A_RUN = "20260721T140505Z_DD-006A_ea3a1ae3_0d8f84a4b7"
DD006B_RUN = "20260721T165512Z_DD-006B_f022a1a5_3be21d0b9b"
DD007_RUN = "20260721T052307Z_DD-007_af4ea130_72fb89c5fc"
DD008_RUN = "20260721T141527Z_DD-008_0d11dc77_7e0c8f1d66"
DD008A_RUN = "20260721T153110Z_DD-008A_637f2b94_06307caab4"
DD008B_RUN = "20260721T192412Z_DD-008B_649deb08_29dbeaf3a9"
DD009_RUN = "20260721T171249Z_DD-009_bc78d249_0c3851c41a"


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _exact(value: Fraction | str | int) -> str:
    parsed = value if isinstance(value, Fraction) else Fraction(str(value))
    return str(parsed.numerator) if parsed.denominator == 1 else str(parsed)


def _decimal(value: Fraction | str | int | float, digits: int = 3) -> str:
    number = float(value if isinstance(value, (int, float, Fraction)) else Fraction(str(value)))
    return f"{number:.{digits}f}".rstrip("0").rstrip(".")


def _percent(value: Fraction | str | int | float, digits: int = 1) -> str:
    number = float(value if isinstance(value, (int, float, Fraction)) else Fraction(str(value)))
    return f"{number * 100:.{digits}f}%"


def _attr(value: object) -> str:
    return html.escape(str(value), quote=True)


def _options(values: list[str], selected: str | None = None) -> str:
    return "".join(
        f'<option value="{_attr(value)}"{" selected" if value == selected else ""}>{html.escape(value.replace("-", " ").replace("_", " "))}</option>'
        for value in values
    )


def _declaration(
    *,
    lab_type: str,
    studies: str,
    source: str,
    controls: str,
    outputs: str,
    baseline: str,
    claims: tuple[str, ...],
    runs: tuple[str, ...],
    slug: str,
) -> str:
    claim_links = " · ".join(
        f'<a href="../claims.html#{html.escape(claim)}">{html.escape(claim)}</a>'
        for claim in claims
    )
    run_links = " · ".join(
        f'<a href="{REPOSITORY_URL}/blob/main/results/verified/{html.escape(run)}/manifest.json"><code>{html.escape(run)}</code></a>'
        for run in runs
    )
    return f"""<details class="technical-details lab-declaration"><summary>Lab declaration and technical details</summary><dl><div><dt>Lab type</dt><dd>{html.escape(lab_type)}</dd></div><div><dt>Supporting study</dt><dd>{html.escape(studies)}</dd></div><div><dt>Data source</dt><dd>{html.escape(source)}</dd></div><div><dt>Control fields</dt><dd>{html.escape(controls)}</dd></div><div><dt>Output fields</dt><dd>{html.escape(outputs)}</dd></div><div><dt>Baseline</dt><dd>{html.escape(baseline)}</dd></div><div><dt>No-JavaScript fallback</dt><dd>Complete registered rows in the table below.</dd></div><div><dt>Claims</dt><dd>{claim_links}</dd></div><div><dt>Runs</dt><dd>{run_links}</dd></div></dl><p><a href="../data/labs/{html.escape(slug)}.json">Download the Lab data</a></p></details>"""


def _metric(
    label: str, key: str, value: object, *, exact_key: str | None = None, exact: object = ""
) -> str:
    exact_line = (
        f'<small class="exact-value">Exact: <code data-output-key="{_attr(exact_key)}">{html.escape(str(exact))}</code></small>'
        if exact_key
        else ""
    )
    return f'<article class="metric-card"><span>{html.escape(label)}</span><strong data-output-key="{_attr(key)}">{html.escape(str(value))}</strong>{exact_line}</article>'


def _data_row(
    kind: str, filters: dict[str, object], outputs: dict[str, object], cells: list[object]
) -> str:
    attrs = " ".join(
        [f'data-output-row="{_attr(kind)}"']
        + [f'data-{_attr(key)}="{_attr(value)}"' for key, value in filters.items()]
        + [f'data-{_attr(key)}="{_attr(value)}"' for key, value in outputs.items()]
    )
    return f'<tr {attrs}><th scope="row">{html.escape(str(cells[0]))}</th>{"".join(f"<td>{html.escape(str(cell))}</td>" for cell in cells[1:])}</tr>'


def _generic_lab(
    *,
    slug: str,
    title: str,
    eyebrow: str,
    description: str,
    kind: str,
    controls: str,
    status: str,
    metrics: str,
    visual: str,
    takeaway: str,
    table_caption: str,
    table_headers: tuple[str, ...],
    table_rows: str,
    declaration: str,
    row_count: int,
) -> str:
    headers = "".join(f"<th>{html.escape(value)}</th>" for value in table_headers)
    return f"""<header class="page-hero"><p class="eyebrow">{html.escape(eyebrow)}</p><h1>{html.escape(title)}</h1><p class="lede">{html.escape(description)}</p></header><section class="lab explainer-lab" data-output-lab="{html.escape(kind)}"><fieldset class="lab-controls"><legend>Choose a registered comparison</legend>{controls}</fieldset><div class="lab-actions"><button type="button" class="filter-button" data-lab-reset>Reset</button><a href="../data/labs/{html.escape(slug)}.json">Download data</a></div><p class="callout" data-output-status aria-live="polite">{html.escape(status)}</p><div class="metric-grid compact">{metrics}</div>{visual}<p class="takeaway"><strong>Takeaway:</strong> <span data-output-key="takeaway">{html.escape(takeaway)}</span></p></section><noscript><p class="callout">JavaScript is off. All {row_count} registered rows remain visible in the complete table.</p></noscript>{declaration}<details class="technical-details complete-data"><summary>Complete registered table</summary><table class="matrix"><caption>{html.escape(table_caption)}</caption><thead><tr>{headers}</tr></thead><tbody>{table_rows}</tbody></table></details>"""


def _sequential(root: Path) -> dict[str, Any]:
    source = root / "results/verified" / DD004_RUN / "outputs/schedule-frontier.json"
    rows = _load_json(source)
    by_case: dict[str, list[dict[str, Any]]] = {str(row["case"]): [] for row in rows}
    for row in rows:
        by_case[str(row["case"])].append(row)
    output_rows: list[dict[str, Any]] = []
    html_rows: list[str] = []
    for row in rows:
        case = str(row["case"])
        peers = by_case[case]
        parallel = next(item for item in peers if item["schedule"] == "4")
        sequential = next(item for item in peers if item["schedule"] == "1+1+1+1")
        actions = Fraction(str(row["expected_actions"]))
        rounds = Fraction(str(row["expected_rounds"]))
        action_savings = Fraction(str(parallel["expected_actions"])) - actions
        round_cost = rounds - Fraction(str(parallel["expected_rounds"]))
        derived = {
            **row,
            "total_action_budget": 4,
            "batches": len(str(row["schedule"]).split("+")),
            "action_savings": _exact(action_savings),
            "round_cost": _exact(round_cost),
            "parallel_expected_actions": parallel["expected_actions"],
            "sequential_expected_actions": sequential["expected_actions"],
            "parallel_expected_rounds": parallel["expected_rounds"],
            "sequential_expected_rounds": sequential["expected_rounds"],
        }
        output_rows.append(derived)
        outputs = {
            "terminal-display": _percent(row["terminal_discovery"]),
            "terminal-exact": row["terminal_discovery"],
            "actions-display": _decimal(actions),
            "actions-exact": _exact(actions),
            "rounds-display": _decimal(rounds),
            "rounds-exact": _exact(rounds),
            "batches": derived["batches"],
            "savings-display": _decimal(action_savings),
            "savings-exact": _exact(action_savings),
            "round-cost-display": _decimal(round_cost),
            "round-cost-exact": _exact(round_cost),
            "timeline": " → ".join(str(row["schedule"]).split("+")),
            "parallel-actions": _decimal(parallel["expected_actions"]),
            "selected-actions": _decimal(actions),
            "sequential-actions": _decimal(sequential["expected_actions"]),
            "parallel-actions-width": _decimal(
                Fraction(str(parallel["expected_actions"])) / 4 * 100
            ),
            "selected-actions-width": _decimal(actions / 4 * 100),
            "sequential-actions-width": _decimal(
                Fraction(str(sequential["expected_actions"])) / 4 * 100
            ),
            "takeaway": "Perfect failure feedback preserves terminal discovery here while trading fewer expected actions for more expected rounds.",
        }
        html_rows.append(
            _data_row(
                "sequential",
                {"fixture": case, "schedule": row["schedule"]},
                outputs,
                [
                    case,
                    row["schedule"],
                    row["terminal_discovery"],
                    row["expected_actions"],
                    row["expected_rounds"],
                    derived["batches"],
                    derived["action_savings"],
                    derived["round_cost"],
                ],
            )
        )
    default = next(
        item
        for item in output_rows
        if item["case"] == "asymmetric-eight" and item["schedule"] == "2+2"
    )
    metrics = "".join(
        [
            _metric(
                "Terminal discovery",
                "terminal-display",
                _percent(default["terminal_discovery"]),
                exact_key="terminal-exact",
                exact=default["terminal_discovery"],
            ),
            _metric(
                "Expected actions",
                "actions-display",
                _decimal(default["expected_actions"]),
                exact_key="actions-exact",
                exact=default["expected_actions"],
            ),
            _metric(
                "Expected rounds",
                "rounds-display",
                _decimal(default["expected_rounds"]),
                exact_key="rounds-exact",
                exact=default["expected_rounds"],
            ),
            _metric("Batches", "batches", default["batches"]),
            _metric(
                "Actions saved vs parallel",
                "savings-display",
                _decimal(default["action_savings"]),
                exact_key="savings-exact",
                exact=default["action_savings"],
            ),
            _metric(
                "Round cost vs parallel",
                "round-cost-display",
                _decimal(default["round_cost"]),
                exact_key="round-cost-exact",
                exact=default["round_cost"],
            ),
        ]
    )
    controls = f'<div><label for="sequential-fixture">Fixture or prior</label><select id="sequential-fixture" data-filter-key="fixture">{_options(sorted(by_case), "asymmetric-eight")}</select></div><div><label for="sequential-schedule">Batch schedule</label><select id="sequential-schedule" data-filter-key="schedule">{_options(["4", "3+1", "2+2", "2+1+1", "1+3", "1+2+1", "1+1+2", "1+1+1+1"], "2+2")}</select></div><div class="registered-context"><span>Registered total action budget</span><strong>4 actions</strong></div>'
    visual = """<section class="lab-visual" aria-labelledby="sequential-visual-title"><h2 id="sequential-visual-title">Batch timeline and expected-action comparison</h2><p class="visual-summary">Batch sizes appear in order. Bars compare the expected actions used by fully parallel, selected, and fully sequential schedules.</p><p class="timeline" data-output-key="timeline">2 → 2</p><div class="comparison-bars"><div><span>Fully parallel</span><i data-output-bar-key="parallel-actions-width"></i><strong data-output-key="parallel-actions">4</strong></div><div><span>Selected schedule</span><i data-output-bar-key="selected-actions-width"></i><strong data-output-key="selected-actions">3.1</strong></div><div><span>Fully sequential</span><i data-output-bar-key="sequential-actions-width"></i><strong data-output-key="sequential-actions">2.725</strong></div></div></section>"""
    body = _generic_lab(
        slug="sequential",
        title="Sequential Discovery",
        eyebrow="Data explorer · DD-004",
        description="Compare every registered perfect-elimination batch schedule while keeping terminal discovery, expected actions, and rounds separate.",
        kind="sequential",
        controls=controls,
        status="Showing the asymmetric prior with a 2+2 batch schedule.",
        metrics=metrics,
        visual=visual,
        takeaway="Perfect failure feedback preserves terminal discovery here while trading fewer expected actions for more expected rounds.",
        table_caption="Complete exact DD-004 schedule frontier",
        table_headers=(
            "Fixture",
            "Schedule",
            "Terminal discovery",
            "Expected actions",
            "Expected rounds",
            "Batches",
            "Action savings",
            "Round cost",
        ),
        table_rows="".join(html_rows),
        declaration=_declaration(
            lab_type="Data explorer",
            studies="DD-004",
            source=str(source.relative_to(root)),
            controls="fixture or prior; batch schedule; registered budget shown read-only",
            outputs="terminal discovery; expected actions; expected rounds; batches; savings; round cost",
            baseline="Fully parallel schedule 4",
            claims=("DD-C-0045",),
            runs=(DD004_RUN,),
            slug="sequential",
        ),
        row_count=len(rows),
    )
    return {
        "title": "Sequential Discovery",
        "description": "Exact DD-004 schedule-frontier explorer.",
        "body": body,
        "data": {
            "schema_version": 1,
            "lab_type": "data-explorer",
            "study_ids": ["DD-004"],
            "run_ids": [DD004_RUN],
            "claim_ids": ["DD-C-0045"],
            "rows": output_rows,
        },
    }


def _coverage(root: Path) -> dict[str, Any]:
    source_dir = root / "results/verified" / DD005_RUN / "outputs"
    frontier = _load_json(source_dir / "coverage-frontiers.json")
    config = yaml.safe_load(
        (root / "studies/DD-005-overlapping-coverage/configs/frontiers.yml").read_text(
            encoding="utf-8"
        )
    )
    fixtures = {str(item["name"]): item for item in config["fixtures"]}
    rows: list[dict[str, Any]] = []
    html_rows: list[str] = []
    for summary in frontier:
        fixture_name = str(summary["fixture"])
        fixture = fixtures[fixture_name]
        weights = list(fixture["weights"])
        actions = [set(action) for action in fixture["actions"]]
        exact_value = Fraction(str(summary["exact_value"]))
        named = {
            "exact-optimum": summary["exact_portfolio"],
            "top-individual-values": summary["top_individual_portfolio"],
            "marginal-greedy": summary["greedy_portfolio"],
        }
        selections = [(rule, "registered", portfolio) for rule, portfolio in named.items()]
        selections.extend(
            ("manual-selection", "+".join(str(value) for value in selection), list(selection))
            for selection in itertools.combinations(range(len(actions)), int(fixture["budget"]))
        )
        for rule, selection_id, portfolio in selections:
            hit_counts = {outcome: 0 for outcome in range(len(weights))}
            for action_id in portfolio:
                for outcome in actions[action_id]:
                    hit_counts[outcome] += 1
            covered = [outcome for outcome, count in hit_counts.items() if count]
            union_value = sum(Fraction(str(weights[outcome])) for outcome in covered)
            overlap = sum(len(actions[action_id]) for action_id in portfolio) - len(covered)
            redundancy = sum(max(0, count - 1) for count in hit_counts.values())
            gap = exact_value - union_value
            row = {
                "fixture": fixture_name,
                "rule": rule,
                "selection": selection_id,
                "portfolio": portfolio,
                "weighted_union_coverage": _exact(union_value),
                "covered_outcomes": covered,
                "overlap": overlap,
                "redundancy": redundancy,
                "gap_from_optimum": _exact(gap),
                "recovery_budget": f"{fixture['budget']} actions (exact)"
                if gap == 0
                else f"not recovered at {fixture['budget']} actions",
                "actions": [sorted(value) for value in actions],
                "weights": weights,
            }
            rows.append(row)
            outputs = {
                "coverage-display": _decimal(union_value),
                "coverage-exact": _exact(union_value),
                "covered": ", ".join(str(value) for value in covered),
                "portfolio": ", ".join(f"A{value}" for value in portfolio),
                "overlap": overlap,
                "redundancy": redundancy,
                "gap-display": _decimal(gap),
                "gap-exact": _exact(gap),
                "recovery": row["recovery_budget"],
                "coverage-width": _decimal((union_value / exact_value) * 100 if exact_value else 0),
                "action-sets": " · ".join(
                    f"A{index}={{{', '.join(str(value) for value in sorted(action))}}}"
                    for index, action in enumerate(actions)
                ),
                "takeaway": "Different action labels do not guarantee different covered outcomes; inspect the union and the gap, not the labels alone.",
            }
            html_rows.append(
                _data_row(
                    "coverage",
                    {"fixture": fixture_name, "rule": rule, "selection": selection_id},
                    outputs,
                    [
                        fixture_name,
                        rule,
                        selection_id,
                        row["portfolio"],
                        row["covered_outcomes"],
                        row["weighted_union_coverage"],
                        overlap,
                        redundancy,
                        row["gap_from_optimum"],
                    ],
                )
            )
    default = next(
        row
        for row in rows
        if row["fixture"] == "duplicated-ranking-witness" and row["rule"] == "top-individual-values"
    )
    controls = f'<div><label for="coverage-fixture">Fixture</label><select id="coverage-fixture" data-filter-key="fixture">{_options(sorted(fixtures), "duplicated-ranking-witness")}</select></div><div><label for="coverage-rule">Portfolio rule</label><select id="coverage-rule" data-filter-key="rule">{_options(["exact-optimum", "top-individual-values", "marginal-greedy", "manual-selection"], "top-individual-values")}</select></div><div data-manual-control hidden><label for="coverage-selection">Manual action selection</label><select id="coverage-selection" data-filter-key="selection" disabled>{_options(sorted({str(row["selection"]) for row in rows if row["rule"] == "manual-selection"}))}</select></div>'
    metrics = "".join(
        [
            _metric(
                "Weighted union coverage",
                "coverage-display",
                _decimal(default["weighted_union_coverage"]),
                exact_key="coverage-exact",
                exact=default["weighted_union_coverage"],
            ),
            _metric(
                "Covered outcomes",
                "covered",
                ", ".join(str(value) for value in default["covered_outcomes"]),
            ),
            _metric(
                "Selected portfolio",
                "portfolio",
                ", ".join(f"A{value}" for value in default["portfolio"]),
            ),
            _metric("Overlap", "overlap", default["overlap"]),
            _metric("Redundancy", "redundancy", default["redundancy"]),
            _metric(
                "Gap from optimum",
                "gap-display",
                _decimal(default["gap_from_optimum"]),
                exact_key="gap-exact",
                exact=default["gap_from_optimum"],
            ),
            _metric("Recovery budget", "recovery", default["recovery_budget"]),
        ]
    )
    visual = f"""<section class="lab-visual" aria-labelledby="coverage-visual-title"><h2 id="coverage-visual-title">Outcome coverage</h2><p class="visual-summary" data-output-key="action-sets">A0={{0, 1, 2}} · A1={{0, 1, 2}} · A2={{3}}</p><div class="coverage-track"><i data-output-bar-key="coverage-width"></i></div><p><span data-output-key="coverage-display">{_decimal(default["weighted_union_coverage"])}</span> of exact optimum {html.escape(str(next(item["exact_value"] for item in frontier if item["fixture"] == default["fixture"])))}</p></section>"""
    body = _generic_lab(
        slug="coverage",
        title="Coverage and Redundancy",
        eyebrow="Guided exhibit · DD-005",
        description="Compare exact, ranking, greedy, and manual portfolios on the three registered weighted-union fixtures.",
        kind="coverage",
        controls=controls,
        status="Showing top individual values on the duplicated-ranking witness.",
        metrics=metrics,
        visual=visual,
        takeaway="Different action labels do not guarantee different covered outcomes; inspect the union and the gap, not the labels alone.",
        table_caption="Complete DD-005 registered portfolio comparisons",
        table_headers=(
            "Fixture",
            "Rule",
            "Selection",
            "Portfolio",
            "Covered outcomes",
            "Union value",
            "Overlap",
            "Redundancy",
            "Gap",
        ),
        table_rows="".join(html_rows),
        declaration=_declaration(
            lab_type="Guided exhibit",
            studies="DD-005",
            source=str((source_dir / "coverage-frontiers.json").relative_to(root)),
            controls="fixture; portfolio rule; manual selection for small fixtures",
            outputs="weighted union; outcomes; overlap; redundancy; optimum gap; recovery budget",
            baseline="Exact optimum for the selected fixture",
            claims=("DD-C-0046",),
            runs=(DD005_RUN,),
            slug="coverage",
        ),
        row_count=len(rows),
    )
    return {
        "title": "Coverage and Redundancy",
        "description": "Exact DD-005 weighted-union coverage explorer.",
        "body": body,
        "data": {
            "schema_version": 1,
            "lab_type": "guided-exhibit",
            "study_ids": ["DD-005"],
            "run_ids": [DD005_RUN],
            "claim_ids": ["DD-C-0046"],
            "rows": rows,
        },
    }


def _mechanisms(root: Path) -> dict[str, Any]:
    dd006_path = root / "results/verified" / DD006_RUN / "outputs/mechanism-catalogue.json"
    dd006a_path = root / "results/verified" / DD006A_RUN / "outputs/general-transfer-frontier.json"
    dd006b_path = root / "results/verified" / DD006B_RUN / "outputs/joint-mechanism-frontier.json"
    rows: list[dict[str, Any]] = []

    for item in _load_json(dd006_path):
        maximum_gain = max(Fraction(str(deviation["gain"])) for deviation in item["deviations"])
        margin = -maximum_gain
        rows.append(
            {
                "family": "DD-006 score difference",
                "regime": str(item["regime"]),
                "mechanism": f"coefficient {item['coefficient']}",
                "tie_role": "not applicable",
                "truthful_reporting": "yes" if item["truthful_direct_pure_bne"] else "no",
                "action_obedience": "yes" if item["truthful_direct_pure_bne"] else "no",
                "weak_implementation": "yes" if margin >= 0 else "no",
                "strict_implementation": "yes" if item["strict_against_joint_deviations"] else "no",
                "report_margin": _exact(margin),
                "action_margin": _exact(margin),
                "joint_margin": _exact(margin),
                "strict_margin": _exact(margin),
                "discovery": str(item["direct_discovery_probability"]),
                "external_subsidy": "not reported",
                "worst_transfer": "not reported",
                "budget_status": "transfer accounting not registered",
                "takeaway": "The original score-difference fixture separates truthful direct behavior from strict joint implementation.",
            }
        )
    for item in _load_json(dd006a_path):
        for role_index, margin in enumerate(item["fixed_role_margins"], start=1):
            rows.append(
                {
                    "family": "DD-006A transfer frontier",
                    "regime": str(item["regime"]),
                    "mechanism": "coefficients "
                    + ",".join(str(value) for value in item["coefficients"]),
                    "tie_role": f"fixed role {role_index}",
                    "truthful_reporting": "not tested",
                    "action_obedience": "yes" if Fraction(str(margin)) >= 0 else "no",
                    "weak_implementation": "yes" if item["weak_implements_all_ties"] else "no",
                    "strict_implementation": "yes"
                    if item["strictly_implements_all_ties"]
                    else "no",
                    "report_margin": "not applicable",
                    "action_margin": str(margin),
                    "joint_margin": str(margin),
                    "strict_margin": str(margin),
                    "discovery": "not reported",
                    "external_subsidy": "not reported",
                    "worst_transfer": "not reported",
                    "budget_status": "normalized transfer class; subsidy not reported",
                    "takeaway": "The DD-006A normalized transfer class reaches weak but not strict all-tie implementation.",
                }
            )
    for item in _load_json(dd006b_path):
        for role_index, (certificate, accounting, discovery) in enumerate(
            zip(
                item["deviation_certificates_by_tie_role"],
                item["accounting_by_tie_role"],
                item["truthful_discovery_by_tie_role"],
                strict=True,
            ),
            start=1,
        ):
            rows.append(
                {
                    "family": "DD-006B joint score",
                    "regime": str(item["regime"]),
                    "mechanism": "coefficients "
                    + ",".join(str(value) for value in item["coefficients"]),
                    "tie_role": f"fixed role {role_index}",
                    "truthful_reporting": "yes"
                    if Fraction(str(certificate["report_only_margin"])) >= 0
                    else "no",
                    "action_obedience": "yes"
                    if Fraction(str(certificate["action_only_margin"])) >= 0
                    else "no",
                    "weak_implementation": "yes" if item["weak"] else "no",
                    "strict_implementation": "yes" if item["strict"] else "no",
                    "report_margin": str(certificate["report_only_margin"]),
                    "action_margin": str(certificate["action_only_margin"]),
                    "joint_margin": str(certificate["joint_margin"]),
                    "strict_margin": str(item["tie_role_margins"][role_index - 1]),
                    "discovery": str(discovery),
                    "external_subsidy": str(accounting["expected_total_transfer"]),
                    "worst_transfer": str(accounting["worst_case_abs_transfer"]),
                    "budget_status": "externally subsidized"
                    if item["externally_subsidized"]
                    else "no external subsidy",
                    "selected_role_utility": str(
                        accounting["expected_agent_utilities"][role_index - 1]
                    ),
                    "takeaway": "Observable action incentives can support strict joint implementation here; hidden actions fail in the registered class.",
                }
            )

    def outputs(row: dict[str, Any]) -> dict[str, object]:
        numeric_margins = [
            Fraction(str(row[key]))
            for key in ("report_margin", "action_margin", "joint_margin")
            if row[key] not in {"not applicable", "not reported"}
        ]
        scale = max([Fraction(1, 2), *[abs(value) for value in numeric_margins]])
        return {
            "truthful": row["truthful_reporting"],
            "obedience": row["action_obedience"],
            "weak": row["weak_implementation"],
            "strict": row["strict_implementation"],
            "strict-margin": row["strict_margin"],
            "discovery-display": _percent(row["discovery"])
            if row["discovery"] != "not reported"
            else "not reported",
            "discovery-exact": row["discovery"],
            "subsidy": row["external_subsidy"],
            "worst-transfer": row["worst_transfer"],
            "budget": row["budget_status"],
            "role-utility": row.get("selected_role_utility", "not reported"),
            "report-margin": row["report_margin"],
            "action-margin": row["action_margin"],
            "joint-margin": row["joint_margin"],
            "report-margin-width": _decimal(abs(Fraction(str(row["report_margin"]))) / scale * 100)
            if row["report_margin"] not in {"not applicable", "not reported"}
            else 0,
            "action-margin-width": _decimal(abs(Fraction(str(row["action_margin"]))) / scale * 100)
            if row["action_margin"] not in {"not applicable", "not reported"}
            else 0,
            "joint-margin-width": _decimal(abs(Fraction(str(row["joint_margin"]))) / scale * 100)
            if row["joint_margin"] not in {"not applicable", "not reported"}
            else 0,
            "takeaway": row["takeaway"],
        }

    html_rows = "".join(
        _data_row(
            "mechanisms",
            {
                "family": row["family"],
                "regime": row["regime"],
                "mechanism": row["mechanism"],
                "tie-role": row["tie_role"],
            },
            outputs(row),
            [
                row["family"],
                row["regime"],
                row["mechanism"],
                row["tie_role"],
                row["truthful_reporting"],
                row["action_obedience"],
                row["weak_implementation"],
                row["strict_implementation"],
                row["strict_margin"],
                row["discovery"],
                row["external_subsidy"],
                row["worst_transfer"],
                row["budget_status"],
            ],
        )
        for row in rows
    )
    default = next(
        row
        for row in rows
        if row["family"] == "DD-006B joint score"
        and row["regime"] == "target-actions"
        and row["mechanism"] == "coefficients 0,0,1"
        and row["tie_role"] == "fixed role 1"
    )
    default_outputs = outputs(default)
    controls = f'<div><label for="mechanisms-family">Mechanism family</label><select id="mechanisms-family" data-filter-key="family">{_options(sorted({str(row["family"]) for row in rows}), str(default["family"]))}</select></div><div><label for="mechanisms-regime">Observability regime</label><select id="mechanisms-regime" data-filter-key="regime">{_options(sorted({str(row["regime"]) for row in rows}), str(default["regime"]))}</select></div><div><label for="mechanisms-row">Named coefficient row</label><select id="mechanisms-row" data-filter-key="mechanism">{_options(sorted({str(row["mechanism"]) for row in rows}), str(default["mechanism"]))}</select></div><div><label for="mechanisms-tie">Tie role</label><select id="mechanisms-tie" data-filter-key="tie-role">{_options(sorted({str(row["tie_role"]) for row in rows}), str(default["tie_role"]))}</select></div>'
    metrics = "".join(
        [
            _metric("Truthful reporting", "truthful", default["truthful_reporting"]),
            _metric("Action obedience", "obedience", default["action_obedience"]),
            _metric("Weak implementation", "weak", default["weak_implementation"]),
            _metric("Strict implementation", "strict", default["strict_implementation"]),
            _metric("Strict margin", "strict-margin", default["strict_margin"]),
            _metric(
                "Discovery",
                "discovery-display",
                _percent(default["discovery"]),
                exact_key="discovery-exact",
                exact=default["discovery"],
            ),
            _metric("External subsidy", "subsidy", default["external_subsidy"]),
            _metric("Worst-case transfer", "worst-transfer", default["worst_transfer"]),
            _metric("Budget status", "budget", default["budget_status"]),
            _metric("Selected-role utility", "role-utility", default["selected_role_utility"]),
        ]
    )
    visual = f"""<section class="lab-visual" aria-labelledby="mechanism-visual-title"><h2 id="mechanism-visual-title">Deviation margins</h2><p class="visual-summary">The text gives each signed exact margin; bar length gives magnitude only, so sign is never communicated by color.</p><div class="comparison-bars"><div><span>Report-only: <b data-output-key="report-margin">{html.escape(str(default["report_margin"]))}</b></span><i data-output-bar-key="report-margin-width" style="--bar-value:{default_outputs["report-margin-width"]}%"></i><strong>exact</strong></div><div><span>Action-only: <b data-output-key="action-margin">{html.escape(str(default["action_margin"]))}</b></span><i data-output-bar-key="action-margin-width" style="--bar-value:{default_outputs["action-margin-width"]}%"></i><strong>exact</strong></div><div><span>Joint: <b data-output-key="joint-margin">{html.escape(str(default["joint_margin"]))}</b></span><i data-output-bar-key="joint-margin-width" style="--bar-value:{default_outputs["joint-margin-width"]}%"></i><strong>exact</strong></div></div></section>"""
    body = _generic_lab(
        slug="mechanisms",
        title="Mechanisms and Incentives",
        eyebrow="Data explorer · DD-006 / DD-006A / DD-006B",
        description="Compare the registered score-difference, normalized-transfer, and joint truthful-and-obedient mechanism families without crossing their observability boundaries.",
        kind="mechanisms",
        controls=controls,
        status="Showing DD-006B target-actions coefficients 0,0,1 for fixed role 1.",
        metrics=metrics,
        visual=visual,
        takeaway=str(default["takeaway"]),
        table_caption="Complete public mechanism comparison rows",
        table_headers=(
            "Family",
            "Regime",
            "Mechanism",
            "Tie role",
            "Truthful",
            "Obedient",
            "Weak",
            "Strict",
            "Margin",
            "Discovery",
            "Subsidy",
            "Worst transfer",
            "Budget",
        ),
        table_rows=html_rows,
        declaration=_declaration(
            lab_type="Data explorer",
            studies="DD-006, DD-006A, and DD-006B",
            source="three immutable public mechanism frontiers",
            controls="mechanism family; observability regime; coefficient row; tie role",
            outputs="truth; obedience; weak/strict implementation; margins; discovery; subsidy; transfer; budget",
            baseline="DD-006B target-actions coefficients 0,0,1",
            claims=("DD-C-0048", "DD-C-0050", "DD-C-0053"),
            runs=(DD006_RUN, DD006A_RUN, DD006B_RUN),
            slug="mechanisms",
        ),
        row_count=len(rows),
    )
    return {
        "title": "Mechanisms and Incentives",
        "description": "Exact registered mechanism-family explorer.",
        "body": body,
        "data": {
            "schema_version": 1,
            "lab_type": "data-explorer",
            "study_ids": ["DD-006", "DD-006B"],
            "run_ids": [DD006_RUN, DD006A_RUN, DD006B_RUN],
            "claim_ids": ["DD-C-0048", "DD-C-0050", "DD-C-0053"],
            "rows": rows,
        },
    }


def _audit(root: Path) -> dict[str, Any]:
    source_dir = root / "results/verified" / DD007_RUN / "outputs"
    raw = _load_json(source_dir / "synthetic-recovery-grid.json")
    calibration = {
        str(item["condition"]): item
        for item in _load_json(source_dir / "uncertainty-calibration.json")
    }
    grouped: dict[tuple[float, float, float], list[dict[str, Any]]] = {}
    for row in raw:
        key = (
            float(row["copying_truth"]),
            float(row["provenance_missing_truth"]),
            float(row["matching_error_truth"]),
        )
        grouped.setdefault(key, []).append(row)
    rows: list[dict[str, Any]] = []
    for (copying, missing, error), items in sorted(grouped.items()):
        estimates = [float(item["copying_estimate"]) for item in items]
        mean = sum(estimates) / len(estimates)
        bias = mean - copying
        rmse = math.sqrt(sum((estimate - copying) ** 2 for estimate in estimates) / len(estimates))
        condition = f"copy={copying};missing={missing};error={error}"
        rows.append(
            {
                "copying_truth": copying,
                "provenance_missing_truth": missing,
                "matching_error_truth": error,
                "sample_size": 240,
                "replicates": len(items),
                "estimator_mean": mean,
                "bias": bias,
                "rmse": rmse,
                "interval_coverage": float(calibration[condition]["coverage"]),
                "duplication": sum(float(item["agreement"]) for item in items) / len(items),
                "provenance_completeness": 1
                - sum(float(item["source_missing_rate"]) for item in items) / len(items),
            }
        )

    def outputs(row: dict[str, Any]) -> dict[str, object]:
        return {
            "mean": _decimal(row["estimator_mean"]),
            "bias": _decimal(row["bias"]),
            "rmse": _decimal(row["rmse"]),
            "coverage": _percent(row["interval_coverage"]),
            "duplication": _percent(row["duplication"]),
            "provenance": _percent(row["provenance_completeness"]),
            "truth": _percent(row["copying_truth"]),
            "estimate": _percent(row["estimator_mean"]),
            "truth-width": _decimal(row["copying_truth"] * 100),
            "estimate-width": _decimal(max(0, min(1, row["estimator_mean"])) * 100),
            "coverage-width": _decimal(row["interval_coverage"] * 100),
            "takeaway": "Matching error attenuates the copying estimator and can destroy interval coverage; provenance missingness separately limits source interpretation.",
        }

    html_rows = "".join(
        _data_row(
            "audit",
            {
                "copying": row["copying_truth"],
                "missing": row["provenance_missing_truth"],
                "error": row["matching_error_truth"],
                "sample": row["sample_size"],
            },
            outputs(row),
            [
                row["copying_truth"],
                row["provenance_missing_truth"],
                row["matching_error_truth"],
                row["sample_size"],
                _decimal(row["estimator_mean"]),
                _decimal(row["bias"]),
                _decimal(row["rmse"]),
                _percent(row["interval_coverage"]),
                _percent(row["duplication"]),
                _percent(row["provenance_completeness"]),
            ],
        )
        for row in rows
    )
    default = next(
        row
        for row in rows
        if row["copying_truth"] == 0.5
        and row["provenance_missing_truth"] == 0.5
        and row["matching_error_truth"] == 0.1
    )
    default_outputs = outputs(default)
    controls = f'<div><label for="audit-copying">True copying rate</label><select id="audit-copying" data-filter-key="copying">{_options(["0.0", "0.5", "1.0"], "0.5")}</select></div><div><label for="audit-missing">Provenance missingness</label><select id="audit-missing" data-filter-key="missing">{_options(["0.0", "0.5"], "0.5")}</select></div><div><label for="audit-error">Action-matching error</label><select id="audit-error" data-filter-key="error">{_options(["0.0", "0.1"], "0.1")}</select></div><div><label for="audit-sample">Registered sample size</label><select id="audit-sample" data-filter-key="sample"><option value="240" selected>240 sessions per replicate</option></select></div>'
    metrics = "".join(
        [
            _metric("Estimator mean", "mean", _decimal(default["estimator_mean"])),
            _metric("Bias", "bias", _decimal(default["bias"])),
            _metric("RMSE", "rmse", _decimal(default["rmse"])),
            _metric("Interval coverage", "coverage", _percent(default["interval_coverage"])),
            _metric("Observed duplication", "duplication", _percent(default["duplication"])),
            _metric(
                "Provenance completeness",
                "provenance",
                _percent(default["provenance_completeness"]),
            ),
        ]
    )
    visual = f"""<section class="lab-visual" aria-labelledby="audit-visual-title"><h2 id="audit-visual-title">Truth, estimate, and calibration</h2><p class="visual-summary">Bars compare the true copying rate, mean recovered estimate, and interval coverage across eight seeded synthetic replicates.</p><div class="comparison-bars"><div><span>Truth</span><i data-output-bar-key="truth-width" style="--bar-value:{default_outputs["truth-width"]}%"></i><strong data-output-key="truth">{default_outputs["truth"]}</strong></div><div><span>Mean estimate</span><i data-output-bar-key="estimate-width" style="--bar-value:{default_outputs["estimate-width"]}%"></i><strong data-output-key="estimate">{default_outputs["estimate"]}</strong></div><div><span>Interval coverage</span><i data-output-bar-key="coverage-width" style="--bar-value:{default_outputs["coverage-width"]}%"></i><strong data-output-key="coverage">{default_outputs["coverage"]}</strong></div></div></section>"""
    body = _generic_lab(
        slug="audit",
        title="Audit and Calibration",
        eyebrow="Data explorer · synthetic only · DD-007",
        description="Inspect the registered seeded synthetic estimator-recovery grid. No real data or behavioral validation is present.",
        kind="audit",
        controls=controls,
        status="Showing copy=0.5, missingness=0.5, matching error=0.1 at 240 sessions per replicate.",
        metrics=metrics,
        visual=visual,
        takeaway=str(default_outputs["takeaway"]),
        table_caption="Twelve registered DD-007 synthetic calibration conditions",
        table_headers=(
            "True copying",
            "Missingness",
            "Matching error",
            "Sample",
            "Mean",
            "Bias",
            "RMSE",
            "Coverage",
            "Duplication",
            "Provenance",
        ),
        table_rows=html_rows,
        declaration=_declaration(
            lab_type="Data explorer",
            studies="DD-007",
            source=str((source_dir / "synthetic-recovery-grid.json").relative_to(root)),
            controls="true copying; provenance missingness; matching error; registered sample",
            outputs="mean; bias; RMSE; interval coverage; duplication; provenance completeness",
            baseline="Eight seeded replicates per condition; 240 sessions each",
            claims=("DD-C-0049",),
            runs=(DD007_RUN,),
            slug="audit",
        ),
        row_count=len(rows),
    )
    return {
        "title": "Audit and Calibration",
        "description": "Synthetic-only DD-007 calibration explorer.",
        "body": body,
        "data": {
            "schema_version": 1,
            "lab_type": "data-explorer",
            "study_ids": ["DD-007"],
            "run_ids": [DD007_RUN],
            "claim_ids": ["DD-C-0049"],
            "synthetic_only": True,
            "rows": rows,
        },
    }


def _evidence_acquisition(root: Path) -> dict[str, Any]:
    source = root / "results/verified" / DD008A_RUN / "outputs/n-agent-census.json"
    census = _load_json(source)
    rows: list[dict[str, Any]] = []
    for item in census:
        weak = [int(cell["k"]) for cell in item["cells"] if cell["weak_equilibrium"]]
        planner = [int(value) for value in item["planner_k"]]
        trap = 0 in weak and all(value > 0 for value in planner)
        modes = {
            "equilibrium": min(weak),
            "planner": min(planner),
            "assigned-intervention": min(planner),
        }
        cells = {int(cell["k"]): cell for cell in item["cells"]}
        for mode, selected_k in modes.items():
            cell = cells[selected_k]
            rows.append(
                {
                    "agents": int(item["agents"]),
                    "accuracy": str(item["accuracy"]),
                    "cost": str(item["cost"]),
                    "mode": mode,
                    "equilibrium_k": weak,
                    "planner_k": planner,
                    "independence_gap": int(item["independence_gap"]),
                    "selected_k": selected_k,
                    "discovery": str(cell["gross_discovery"]),
                    "social_net_value": str(cell["net_value"]),
                    "common_source_trap": trap,
                }
            )

    def outputs(row: dict[str, Any]) -> dict[str, object]:
        return {
            "equilibrium-k": ", ".join(str(value) for value in row["equilibrium_k"]),
            "planner-k": ", ".join(str(value) for value in row["planner_k"]),
            "gap": row["independence_gap"],
            "selected-k": row["selected_k"],
            "discovery-display": _percent(row["discovery"]),
            "discovery-exact": row["discovery"],
            "net-display": _decimal(row["social_net_value"]),
            "net-exact": row["social_net_value"],
            "trap": "yes" if row["common_source_trap"] else "no",
            "equilibrium-width": _decimal(max(row["equilibrium_k"]) / row["agents"] * 100),
            "planner-width": _decimal(max(row["planner_k"]) / row["agents"] * 100),
            "takeaway": "Private incentives and the planner can choose different numbers of independent sources; the direction and size depend on team size, accuracy, and cost.",
        }

    html_rows = "".join(
        _data_row(
            "evidence-acquisition",
            {
                "agents": row["agents"],
                "accuracy": row["accuracy"],
                "cost": row["cost"],
                "mode": row["mode"],
            },
            outputs(row),
            [
                row["agents"],
                row["accuracy"],
                row["cost"],
                row["mode"],
                row["equilibrium_k"],
                row["planner_k"],
                row["independence_gap"],
                row["selected_k"],
                row["discovery"],
                row["social_net_value"],
                "yes" if row["common_source_trap"] else "no",
            ],
        )
        for row in rows
    )
    default = next(
        row
        for row in rows
        if row["agents"] == 2
        and row["accuracy"] == "1/2"
        and row["cost"] == "1/6"
        and row["mode"] == "equilibrium"
    )
    default_outputs = outputs(default)
    agents = [str(value) for value in sorted({int(row["agents"]) for row in rows})]
    accuracies = sorted({str(row["accuracy"]) for row in rows}, key=Fraction)
    costs = sorted({str(row["cost"]) for row in rows}, key=Fraction)
    controls = f'<div><label for="acquisition-agents">Team size</label><select id="acquisition-agents" data-filter-key="agents">{_options(agents, "2")}</select></div><div><label for="acquisition-accuracy">Signal accuracy</label><select id="acquisition-accuracy" data-filter-key="accuracy">{_options(accuracies, "1/2")}</select></div><div><label for="acquisition-cost">Independent-source cost</label><select id="acquisition-cost" data-filter-key="cost">{_options(costs, "1/6")}</select></div><div><label for="acquisition-mode">View</label><select id="acquisition-mode" data-filter-key="mode">{_options(["equilibrium", "planner", "assigned-intervention"], "equilibrium")}</select></div>'
    metrics = "".join(
        [
            _metric(
                "Equilibrium independent sources",
                "equilibrium-k",
                ", ".join(str(value) for value in default["equilibrium_k"]),
            ),
            _metric(
                "Planner independent sources",
                "planner-k",
                ", ".join(str(value) for value in default["planner_k"]),
            ),
            _metric("Independence gap", "gap", default["independence_gap"]),
            _metric("Selected-mode sources", "selected-k", default["selected_k"]),
            _metric(
                "Discovery",
                "discovery-display",
                _percent(default["discovery"]),
                exact_key="discovery-exact",
                exact=default["discovery"],
            ),
            _metric(
                "Social net value",
                "net-display",
                _decimal(default["social_net_value"]),
                exact_key="net-exact",
                exact=default["social_net_value"],
            ),
            _metric("Common-Source Trap", "trap", "yes"),
        ]
    )
    visual = f"""<section class="lab-visual" aria-labelledby="acquisition-visual-title"><h2 id="acquisition-visual-title">Equilibrium versus planner source counts</h2><p class="visual-summary">Bar length shows the largest registered source count in each correspondence relative to team size.</p><div class="comparison-bars"><div><span>Equilibrium</span><i data-output-bar-key="equilibrium-width" style="--bar-value:{default_outputs["equilibrium-width"]}%"></i><strong data-output-key="equilibrium-k">0</strong></div><div><span>Planner</span><i data-output-bar-key="planner-width" style="--bar-value:{default_outputs["planner-width"]}%"></i><strong data-output-key="planner-k">1</strong></div></div><p class="callout">Exact preserved over-acquisition counterexample: at N=3, p=4/5, and cost 13/375, equilibrium chooses k=2 while the planner chooses k=1 (DD-008B).</p></section>"""
    body = _generic_lab(
        slug="evidence-acquisition",
        title="Evidence Acquisition",
        eyebrow="Interactive model · DD-008 / DD-008A / DD-008B",
        description="Compare exact equilibrium and planner independent-source counts across the registered finite census, with the Common-Source Trap and over-acquisition boundary kept visible.",
        kind="evidence-acquisition",
        controls=controls,
        status="Showing the two-agent p=1/2, cost=1/6 equilibrium boundary cell.",
        metrics=metrics,
        visual=visual,
        takeaway=str(default_outputs["takeaway"]),
        table_caption="Complete DD-008A exact source-count census by view",
        table_headers=(
            "N",
            "Accuracy",
            "Cost",
            "View",
            "Equilibrium k",
            "Planner k",
            "Gap",
            "Selected k",
            "Discovery",
            "Net value",
            "Trap",
        ),
        table_rows=html_rows,
        declaration=_declaration(
            lab_type="Interactive model",
            studies="DD-008, DD-008A, and DD-008B",
            source=str(source.relative_to(root)),
            controls="team size; accuracy; source cost; equilibrium/planner/intervention view",
            outputs="source counts; gap; discovery; net value; trap status",
            baseline="Equilibrium source count in the selected exact cell",
            claims=("DD-C-0051", "DD-C-0055", "DD-C-0058"),
            runs=(DD008_RUN, DD008A_RUN, DD008B_RUN),
            slug="evidence-acquisition",
        ),
        row_count=len(rows),
    )
    return {
        "title": "Evidence Acquisition",
        "description": "Exact source-acquisition equilibrium and planner explorer.",
        "body": body,
        "data": {
            "schema_version": 1,
            "lab_type": "interactive-model",
            "study_ids": ["DD-008", "DD-008A", "DD-008B"],
            "run_ids": [DD008_RUN, DD008A_RUN, DD008B_RUN],
            "claim_ids": ["DD-C-0051", "DD-C-0055", "DD-C-0058"],
            "rows": rows,
            "over_acquisition_counterexample": _load_json(
                root / "results/verified" / DD008B_RUN / "outputs/counterexamples.json"
            )[0],
        },
    }


def _atlas(root: Path) -> dict[str, Any]:
    source_dir = root / "results/verified" / DD009_RUN / "outputs"
    architectures = _load_json(source_dir / "architectures.json")
    validity = _load_json(source_dir / "validity-registry.json")
    dominance = _load_json(source_dir / "dominance.json")
    pareto_ids = {
        str(architectures[index]["architecture_id"]) for index in dominance["pareto_indices"]
    }
    for row in architectures:
        row["pareto_status"] = (
            "nondominated" if str(row["architecture_id"]) in pareto_ids else "dominated"
        )
    dimensions = {
        "evidence": sorted({str(row["evidence"]) for row in validity}),
        "disclosure": sorted({str(row["disclosure"]) for row in validity}),
        "allocation": sorted({str(row["allocation"]) for row in validity}),
        "timing": sorted({str(row["timing"]) for row in validity}),
        "reward": sorted({str(row["reward"]) for row in validity}),
    }
    default = architectures[0]
    controls = "".join(
        f'<div><label for="atlas-{key}">{html.escape("Acquisition" if key == "evidence" else key.title())}</label><select id="atlas-{key}" data-atlas-filter="{key}">{_options(values, str(default[key]))}</select></div>'
        for key, values in dimensions.items()
    )
    architecture_options = "".join(
        '<option value="{}"{}>{}</option>'.format(
            _attr(row["architecture_id"]),
            " selected" if row["architecture_id"] == default["architecture_id"] else "",
            html.escape(str(row["architecture_id"])),
        )
        for row in architectures
    )
    controls += f'<div><label for="atlas-architecture">Named coherent architecture</label><select id="atlas-architecture"><option value="custom">Custom components</option>{architecture_options}</select></div>'
    metrics = "".join(
        [
            _metric(
                "Discovery",
                "discovery-display",
                _percent(default["discovery"]),
                exact_key="discovery-exact",
                exact=default["discovery"],
            ),
            _metric(
                "Action quality",
                "quality-display",
                _percent(default["action_quality"]),
                exact_key="quality-exact",
                exact=default["action_quality"],
            ),
            _metric(
                "Social net value",
                "net-display",
                _decimal(default["social_net_value"]),
                exact_key="net-exact",
                exact=default["social_net_value"],
            ),
            _metric("Information cost", "cost", default["information_cost"]),
            _metric("Transfer budget", "budget", default["transfer_budget"]),
            _metric("Rounds", "rounds", default["rounds"]),
            _metric("Pareto status", "pareto", default["pareto_status"]),
        ]
    )
    points = "".join(
        f'<button type="button" class="atlas-point{" selected" if row["architecture_id"] == default["architecture_id"] else ""}" data-atlas-point="{_attr(row["architecture_id"])}" style="--atlas-x:{_decimal(Fraction(str(row["information_cost"])) * 100)}%;--atlas-y:{_decimal(Fraction(str(row["discovery"])) * 100)}%" aria-label="{_attr(row["architecture_id"])}: discovery {row["discovery"]}, information cost {row["information_cost"]}, {row["pareto_status"]}"></button>'
        for row in architectures
    )
    architecture_rows = "".join(
        f'<tr data-atlas-architecture="{_attr(row["architecture_id"])}" data-evidence="{_attr(row["evidence"])}" data-disclosure="{_attr(row["disclosure"])}" data-allocation="{_attr(row["allocation"])}" data-timing="{_attr(row["timing"])}" data-reward="{_attr(row["reward"])}" data-discovery-display="{_attr(_percent(row["discovery"]))}" data-discovery-exact="{_attr(row["discovery"])}" data-quality-display="{_attr(_percent(row["action_quality"]))}" data-quality-exact="{_attr(row["action_quality"])}" data-net-display="{_attr(_decimal(row["social_net_value"]))}" data-net-exact="{_attr(row["social_net_value"])}" data-cost="{_attr(row["information_cost"])}" data-budget="{_attr(row["transfer_budget"])}" data-rounds="{_attr(row["rounds"])}" data-pareto="{_attr(row["pareto_status"])}"><th scope="row">{html.escape(str(row["architecture_id"]))}</th><td>{html.escape(str(row["evidence"]))}</td><td>{html.escape(str(row["disclosure"]))}</td><td>{html.escape(str(row["allocation"]))}</td><td>{html.escape(str(row["timing"]))}</td><td>{html.escape(str(row["reward"]))}</td><td>{html.escape(str(row["discovery"]))}</td><td>{html.escape(str(row["action_quality"]))}</td><td>{html.escape(str(row["social_net_value"]))}</td><td>{html.escape(str(row["information_cost"]))}</td><td>{html.escape(str(row["transfer_budget"]))}</td><td>{html.escape(str(row["rounds"]))}</td><td>{html.escape(str(row["pareto_status"]))}</td></tr>'
        for row in architectures
    )
    validity_rows = "".join(
        f'<tr data-atlas-validity data-evidence="{_attr(row["evidence"])}" data-disclosure="{_attr(row["disclosure"])}" data-allocation="{_attr(row["allocation"])}" data-timing="{_attr(row["timing"])}" data-reward="{_attr(row["reward"])}" data-valid="{str(bool(row["valid"])).lower()}" data-reason="{_attr(row["reason"])}" hidden><td>{html.escape(str(row["cell_id"]))}</td><td>{html.escape(str(row["reason"]))}</td></tr>'
        for row in validity
    )
    body = f"""<header class="page-hero"><p class="eyebrow">Data explorer · DD-009</p><h1>Architecture Atlas</h1><p class="lede">Explore the 20 coherent registered architectures and the explicit rejection reason for every other component combination.</p></header><section class="lab explainer-lab" data-atlas-lab><fieldset class="lab-controls"><legend>Choose architecture components or a named coherent row</legend>{controls}</fieldset><div class="lab-actions"><button type="button" class="filter-button" data-lab-reset>Reset</button><a href="../data/labs/atlas.json">Download data</a></div><p class="callout" data-atlas-status aria-live="polite">Showing coherent architecture A001.</p><div class="metric-grid compact">{metrics}</div><section class="lab-visual" aria-labelledby="atlas-visual-title"><h2 id="atlas-visual-title">Pareto map</h2><p class="visual-summary">Points position information cost horizontally and discovery vertically. Each point has a full text label; selected and Pareto status are also written in the metrics.</p><div class="atlas-scatter" role="img" aria-label="Twenty registered architectures plotted by information cost and discovery">{points}</div></section><p class="takeaway"><strong>Takeaway:</strong> <span data-atlas-takeaway>Coherent architectures expose tradeoffs; no single registered row dominates every declared objective.</span></p></section><noscript><p class="callout">JavaScript is off. All 20 coherent rows remain visible below; the download also contains all 288 validity decisions and rejection reasons.</p></noscript>{_declaration(lab_type="Data explorer", studies="DD-009", source=str((source_dir / "architectures.json").relative_to(root)), controls="acquisition; disclosure; allocation; timing; reward; named coherent architecture", outputs="discovery; quality; net value; information cost; transfer budget; rounds; Pareto status", baseline="A001", claims=("DD-C-0054",), runs=(DD009_RUN,), slug="atlas")}<details class="technical-details complete-data"><summary>Complete coherent architecture table</summary><table class="matrix"><caption>Twenty coherent DD-009 architecture rows</caption><thead><tr><th>ID</th><th>Acquisition</th><th>Disclosure</th><th>Allocation</th><th>Timing</th><th>Reward</th><th>Discovery</th><th>Quality</th><th>Net value</th><th>Info cost</th><th>Transfer</th><th>Rounds</th><th>Pareto</th></tr></thead><tbody>{architecture_rows}</tbody></table></details><table hidden><caption>Registered validity lookup</caption><tbody>{validity_rows}</tbody></table>"""
    return {
        "title": "Architecture Atlas",
        "description": "Exact DD-009 coherent architecture and validity explorer.",
        "body": body,
        "data": {
            "schema_version": 1,
            "lab_type": "data-explorer",
            "study_ids": ["DD-009"],
            "run_ids": [DD009_RUN],
            "claim_ids": ["DD-C-0054"],
            "architectures": architectures,
            "validity": validity,
            "dominance": dominance,
        },
    }


def build_core_labs(root: Path) -> dict[str, dict[str, Any]]:
    """Return presentation pages and public data for the six repaired Labs."""
    return {
        "sequential": _sequential(root),
        "coverage": _coverage(root),
        "mechanisms": _mechanisms(root),
        "audit": _audit(root),
        "evidence-acquisition": _evidence_acquisition(root),
        "atlas": _atlas(root),
    }
