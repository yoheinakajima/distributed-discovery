"""Run the versioned DiscoveryBench attention extension."""

from pathlib import Path

from distributed_discovery.benchmark.study import run_registered


def main() -> None:
    run_registered(
        Path("studies/DD-010-discoverybench/configs/attention-v2.yml"),
        "v2",
        "make dd010-attention",
    )


if __name__ == "__main__":
    main()
