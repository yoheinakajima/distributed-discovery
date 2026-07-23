"""Write the deterministic public Agents v1 base-campaign allocation."""

from pathlib import Path

import yaml

from distributed_discovery.benchmark.agents_v1.campaign import build_base_allocation


def main() -> None:
    destination = Path("docs/benchmark/agents-v1/base-campaign-allocation.yml")
    destination.write_text(
        yaml.safe_dump(build_base_allocation(), sort_keys=False, width=100),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
