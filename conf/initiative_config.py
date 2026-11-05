"""Initiative registry and CI selection, without environment secrets."""
import argparse
import json
from pathlib import Path

INITIATIVE_CONFIGS = json.loads(
    Path(__file__).with_name("initiatives.json").read_text(encoding="utf-8")
)


def initiative_matrix(selected):
    if selected == "all":
        return list(INITIATIVE_CONFIGS)
    if selected not in INITIATIVE_CONFIGS:
        raise ValueError(f"Unknown initiative: {selected}")
    return [selected]


def initiative_filter(selected):
    initiative_matrix(selected)
    if selected == "all":
        raise ValueError("Select a concrete initiative for scenario filtering")
    others = [name for name in INITIATIVE_CONFIGS if name != selected]
    return (
        f"({selected} or not ({' or '.join(others)}))"
        if others
        else f"({selected} or not {selected})"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", choices=("matrix", "filter"))
    parser.add_argument("initiative")
    args = parser.parse_args()
    try:
        value = (
            json.dumps(initiative_matrix(args.initiative))
            if args.operation == "matrix"
            else initiative_filter(args.initiative)
        )
    except ValueError as error:
        parser.error(str(error))
    print(value)


if __name__ == "__main__":
    main()
