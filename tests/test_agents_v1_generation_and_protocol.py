from __future__ import annotations

import json

import pytest

from distributed_discovery.benchmark.agents_v1.actions import parse_action
from distributed_discovery.benchmark.agents_v1.adapters import (
    AdapterRequest,
    DisabledProviderAdapter,
    LocalOpenProcessContract,
    MockAdapter,
    ModelManifest,
)
from distributed_discovery.benchmark.agents_v1.generation import (
    canonical_cells,
    generate_instance,
    generate_prompt_space,
    instance_commitment,
)
from distributed_discovery.benchmark.agents_v1.models import task_from_records
from distributed_discovery.benchmark.agents_v1.orchestration import (
    ARCHITECTURES,
    information_rights,
    run_architecture,
)
from distributed_discovery.benchmark.agents_v1.prompts import (
    ClosedCapabilityView,
    compile_prompt,
    leakage_findings,
)


def test_registered_generator_counts_and_determinism() -> None:
    cells = canonical_cells()
    assert len(cells) == 138
    assert sum(cell.primitive_labeled_states for cell in cells) == 58_945
    prompts = generate_prompt_space()
    assert len(prompts) == 552
    assert prompts == generate_prompt_space()


def test_round_trip_and_hidden_labels() -> None:
    task = generate_instance(
        canonical_cells()[0],
        variant=3,
        public_fixture=True,
        material="explicit-public-material",
        hidden_labels=True,
    )
    restored = task_from_records(task.visible_record(), task.evaluator_record())
    assert restored.visible_record() == task.visible_record()
    assert restored.commitment == instance_commitment(restored)
    assert all(
        capability.private_observation.startswith("HIDDEN-LABEL-")
        for capability in task.capabilities.values()
    )


def test_private_generation_fails_closed() -> None:
    with pytest.raises(PermissionError, match="future authorization"):
        generate_instance(canonical_cells()[0], variant=0, public_fixture=False)


def test_prompt_compiler_and_capability_sandbox() -> None:
    task = generate_instance(canonical_cells()[0], variant=0, public_fixture=True)
    agent_id = sorted(task.capabilities)[0]
    prompt = compile_prompt(task, agent_id)
    assert task.task_id not in prompt.user
    assert '"target":' not in prompt.user
    assert leakage_findings(json.loads(prompt.user)) == ()
    view = ClosedCapabilityView(task.capabilities[agent_id])
    assert view["agent_id"] == agent_id
    with pytest.raises(PermissionError, match="undeclared capability"):
        view["primitive_state"]
    with pytest.raises(PermissionError, match="undeclared capability"):
        view["network"]


def test_all_architecture_information_rights() -> None:
    agents = ("AGENT-01", "AGENT-02", "AGENT-03")
    messages = (("AGENT-01", "one"), ("AGENT-02", "two"), ("AGENT-03", "three"))
    for architecture in ARCHITECTURES:
        rights = information_rights(architecture, agents, messages)
        assert set(rights) == set(agents)
    assert information_rights("isolated-private", agents, messages)["AGENT-01"] == ()
    assert len(information_rights("full-broadcast", agents, messages)["AGENT-01"]) == 3
    assert information_rights("designated-reader", agents, messages)["AGENT-03"] == ("one",)


def test_orchestrators_use_two_rounds_and_one_schema_retry() -> None:
    task = generate_instance(canonical_cells()[0], variant=0, public_fixture=True)
    for architecture in ARCHITECTURES:
        run = run_architecture(task, architecture, MockAdapter())
        assert {turn.round_number for turn in run.turns} == {0, 1}
        assert len(run.final_actions) == len(task.capabilities)
    malformed = run_architecture(task, "isolated-private", MockAdapter("malformed"))
    assert all(turn.retry_count == 1 for turn in malformed.turns)


def test_mock_modes_and_live_adapters_fail_closed() -> None:
    task = generate_instance(canonical_cells()[0], variant=0, public_fixture=True)
    prompt = compile_prompt(task, sorted(task.capabilities)[0])
    request = AdapterRequest(
        prompt,
        MockAdapter().manifest,
        0,
        task.action_vocabulary,
        task.source_vocabulary,
    )
    assert MockAdapter("timeout").respond(request).error_class == "timeout"
    assert MockAdapter("error").respond(request).error_class == "adapter-error"
    moving = ModelManifest("example", "latest", "latest", "v1", True, True)
    with pytest.raises(PermissionError, match="disabled"):
        DisabledProviderAdapter(moving).respond(request)
    with pytest.raises(PermissionError, match="outside"):
        LocalOpenProcessContract(("model",), "0" * 64).execute()


def test_structured_action_rejects_duplicates_hidden_fields_and_domain_errors() -> None:
    task = generate_instance(canonical_cells()[0], variant=0, public_fixture=True)
    agent_id = sorted(task.capabilities)[0]
    prompt = compile_prompt(task, agent_id)
    response = MockAdapter().respond(
        AdapterRequest(
            prompt,
            MockAdapter().manifest,
            0,
            task.action_vocabulary,
            task.source_vocabulary,
        )
    )
    action = parse_action(
        response.raw_output,
        task_commitment=task.commitment,
        agent_id=agent_id,
        round_number=0,
        action_vocabulary=task.action_vocabulary,
        source_vocabulary=task.source_vocabulary,
    )
    assert action.agent_id == agent_id
    with pytest.raises(ValueError, match="duplicate field"):
        parse_action(
            '{"schema_version":"x","schema_version":"y"}',
            task_commitment=task.commitment,
            agent_id=agent_id,
            round_number=0,
            action_vocabulary=task.action_vocabulary,
            source_vocabulary=task.source_vocabulary,
        )
    payload = json.loads(response.raw_output)
    payload["answer_key"] = "TARGET-A"
    with pytest.raises(ValueError, match="prohibited"):
        parse_action(
            json.dumps(payload),
            task_commitment=task.commitment,
            agent_id=agent_id,
            round_number=0,
            action_vocabulary=task.action_vocabulary,
            source_vocabulary=task.source_vocabulary,
        )
