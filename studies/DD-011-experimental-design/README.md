# DD-011 — Experimental Design and Power

This study builds a bounded, preregistration-ready **synthetic** package for
acquisition, disclosure, allocation, and reward interventions. It does not
recruit participants, collect human data, deploy an experiment, or establish
real-world statistical power.

Primary run: `20260721T185647Z_DD-011_fa0271d9_fcaa647c55`. Verify it with
`distributed-discovery experiment verify
20260721T185647Z_DD-011_fa0271d9_fcaa647c55`.

The selective-attention extension is explicit v2 and preserves the v1 CLI
default. It appends nine treatment cells, six hypotheses, four outcomes, and
three response scenarios. Inspect it with `distributed-discovery experiment
--version v2 design`; execute `make dd011-attention` only from a clean commit.

The Program V4 extension is explicit v3 and preserves the v1 default and
complete v2 registries. It appends eight threshold/dynamic cells, six
hypotheses, four outcomes, and three response scenarios. Its immutable run is
`20260722T061958Z_DD-011_5743ccba_19b6517655`; verify it with
`distributed-discovery experiment --version v3 verify
20260722T061958Z_DD-011_5743ccba_19b6517655`. No human experiment exists.
