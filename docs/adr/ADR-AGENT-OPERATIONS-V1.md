# ADR: Agent Operations v1

- Status: accepted
- Date: 2026-07-25
- Decision owner: project owner
- Scope: workflow infrastructure only

## Context

Long prompts repeatedly serialized stable repository policy, mixed durable
authority with transient observations, and made checkpoint handoffs difficult
to validate mechanically. The repository already treats Git, claims, runs,
plans, ADRs, issues, pull requests, and release records as durable authority.

## Decision

Adopt “thin prompt, fat repository” prospectively:

- stable rules live in root/scoped instructions and policy;
- one fixed typed task contract defines bounded authority;
- one living ExecPlan records execution state;
- dynamic context is generated from live local and optional GitHub
  observations;
- task-type and acceptance profiles reuse gates without granting permission;
- one generic manifest-driven owner-gate engine creates exact, expiring local
  authorization but performs no consequential action;
- typed handoffs classify completion, checkpoints, stops, and inconsistencies;
- chat carries intake and the task-specific delta only.

The existing scientific authority hierarchy is unchanged. Historical artifacts
are not migrated or rewritten.

## Consequences

New substantive work pays a small registration cost but gains bounded prompts,
machine-checkable permissions, reproducible resumes, reusable validation, and
fail-closed owner gates. A contract authority change requires supersession and
a new owner decision. Generated context and handoffs remain non-authoritative.

The repository must maintain instruction-size, schema, semantic corruption,
private-path, and authority-confusion audits.
