# TreasureBench and classical treasure-hunt literature

Status: required future-paper related-work boundary
Recorded: 2026-07-23

The playable companion uses the familiar name Treasure Hunt. The formal suite
uses TreasureBench because `treasure hunt` is already a technical term across
distributed computing, mobile-agent theory, active perception, and
reinforcement-learning examples.

## Classical distributed and mobile-agent treasure hunt

Classical formulations generally give one or more agents a graph, grid,
geometric terrain, plane, or ordered search space containing an inert hidden
target. The agents navigate or open locations until the target is found.
Primary complexity questions concern edge traversals or path length, time,
advice bits, memory, pebbles, angular hints, failures, or direct/indirect
communication.

Primary examples:

- Pelc and Yadav define treasure hunt as finding an inert target by a mobile
  agent in an unknown geometric terrain and study the advice needed to obtain a
  path-length cost comparable to the shortest route:
  [arXiv:1811.06823](https://arxiv.org/abs/1811.06823).
- Bhattacharya, Gorain, and Mandal study a mobile agent locating a stationary
  object in an anonymous graph, with pebbles supplied by an oracle and time
  measured by traversed edges:
  [arXiv:2209.00857](https://arxiv.org/abs/2209.00857).
- Bouchard, Dieudonné, Pelc, and Petit study an agent finding an inert point
  target in the Euclidean plane using angular hints and worst-case trajectory
  length:
  [DOI 10.4230/LIPIcs.ISAAC.2018.48](https://doi.org/10.4230/LIPIcs.ISAAC.2018.48).
- Dobrev, Královič, and Pardubská study fault-tolerant parallel exhaustive
  search by agents over boxes with very weak communication:
  [DOI 10.4230/LIPIcs.OPODIS.2017.14](https://doi.org/10.4230/LIPIcs.OPODIS.2017.14).
- Couëtoux et al. use a continuous-control TreasureHunt benchmark in which an
  agent moves through an arena toward a treasure while avoiding a hole:
  [HAL-00642459](https://inria.hal.science/hal-00642459).

These lines are related through the language of search, navigation, and
coordination. They are not the same formal object as TreasureBench.

## TreasureBench

TreasureBench evaluates software-agent teams that:

1. receive a declared combination of shared and private evidence;
2. choose a portfolio of actions rather than a navigation trajectory;
3. are evaluated on target success, group discovery, coverage, duplication,
   regret, source diversity, recovery-budget attainment, and related registered
   observables;
4. are compared with exact private, planner, and equilibrium comparators under
   alternative information and action architectures;
5. expose how communication and aggregation change evidence access and action
   correlation;
6. study incentives and institutional architecture as well as information.

The hidden target in the sixteen-box fixture is not a roaming object, and agents
do not traverse a graph to reach it. “Map,” “crew,” “digging site,” and “X
marks the spot” are removable companion metaphors beside the unchanged formal
terms.

## Required future-paper paragraph

Every formal benchmark paper should include, and every AAMAS-adjacent
submission must include, an explicit primary-cited paragraph substantially
equivalent to:

> Classical distributed/mobile-agent treasure-hunt problems ask an agent or
> agents to navigate a graph, grid, plane, or terrain to locate an inert hidden
> target, commonly measuring travel, time, advice, memory, pebble, failure, or
> communication complexity. TreasureBench instead gives software-agent teams
> shared and private evidence, asks them to choose a portfolio of actions, and
> evaluates discovery and coverage against registered exact private, planner,
> and equilibrium comparators under alternative information and action
> architectures.

This record is a literature boundary and naming safeguard. It is not a novelty
claim, complete related-work review, legal conclusion, or paper authorization.
