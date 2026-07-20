# Operationally incomplete baseline run

The pinned upstream verifier completed successfully and `validation.json` passed, but the wrapper then failed while collecting package metadata because the isolated `uv` environment intentionally contained no `pip` module. This run is preserved as an operational negative result and is not used as claim evidence. The wrapper was changed to query `uv pip freeze`; a clean subsequent run is required.
