# TreasureBench version transition

Status: compatibility policy
Effective date: 2026-07-23

TreasureBench is the current formal display name. Rebranding does not create a
scientific, task-content, schema, protocol, metric, or package version.

## Frozen identifiers

The following remain exact:

- `discoverybench-task-v1`, `discoverybench-task-v2`, and
  `discoverybench-task-v3`;
- `discoverybench-suite-v1`, `discoverybench-suite-v2`, and
  `discoverybench-suite-v3`;
- every `DB-G*` task ID;
- every current protocol and metric ID;
- Agents v1 protocol, generator, trace, custody, and campaign identifiers;
- every historical result key, immutable run ID, result path, and checksum.

Compatibility readers continue to accept these identifiers. Public display
metadata may say TreasureBench without mutating the encoded ID.

## Future transition

The next substantive nonfrozen benchmark content or schema version may adopt a
TreasureBench identifier only when:

1. content or schema semantics actually change;
2. the new version has an explicit compatibility record;
3. readers accept the frozen DiscoveryBench identifiers;
4. old public routes, JSON endpoints, and commands remain supported or have a
   documented stable alias;
5. the version passes the scientific evidence and release gates applicable to
   that content.

No new benchmark-content version is created solely to rename the display name.
A future standalone package is a separate owner decision and is not authorized
by this policy.
