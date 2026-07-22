"""Run the DD-011 threshold and dynamic synthetic extension."""

from pathlib import Path

from distributed_discovery.experimental_design.study import run_registered


def main() -> None:
    run_registered(
        Path("studies/DD-011-experimental-design/configs/threshold-dynamic-v3.yml"),
        "v3",
        "make dd011-threshold-dynamic",
    )


if __name__ == "__main__":
    main()
