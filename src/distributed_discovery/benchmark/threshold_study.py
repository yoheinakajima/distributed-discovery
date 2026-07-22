"""Run the versioned DiscoveryBench Program V4 extension."""

from pathlib import Path

from distributed_discovery.benchmark.study import run_registered


def main() -> None:
    run_registered(
        Path("studies/DD-010-discoverybench/configs/threshold-v3.yml"),
        "v3",
        "make dd010-threshold",
    )


if __name__ == "__main__":
    main()
