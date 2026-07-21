"""Run the DD-011 selective-attention synthetic extension."""

from pathlib import Path

from distributed_discovery.experimental_design.study import run_registered


def main() -> None:
    run_registered(
        Path("studies/DD-011-experimental-design/configs/attention-v2.yml"),
        "v2",
        "make dd011-attention",
    )


if __name__ == "__main__":
    main()
