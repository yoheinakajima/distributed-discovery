# DiscoveryBench Agents v1 local hardware audit

The audited host is an arm64 Apple M1 system with eight CPU cores, an
eight-core integrated Metal GPU, 16 GB unified memory, and roughly 1.07 TB free
disk. No supported local inference engine or container engine is installed.
No model was invoked or downloaded.

The pinned Mistral Small 3.1 repository is about 96.1 GB and its official
release note says a Mac with 32 GB RAM or one RTX 4090 is a suitable local
route. This 16-GB host therefore fails the registered local feasibility gate.
Quantization is not silently accepted: it changes engine and numerical
identity and requires a separate audit.

Decision: a two-cloud sealed engineering pilot may be registered, but the
claim-grade base campaign remains blocked until an exact local/open model has a
separately accepted execution environment.
