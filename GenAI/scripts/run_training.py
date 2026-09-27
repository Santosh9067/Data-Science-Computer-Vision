"""Run churn training from a YAML configuration file."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml

from churn_ml.train import train


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def project_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path


def load_config(config_path: str | Path) -> dict[str, Any]:
    with Path(config_path).open("r", encoding="utf-8") as stream:
        config = yaml.safe_load(stream) or {}
    training = config.get("training")
    if not isinstance(training, dict):
        raise ValueError("YAML must contain a 'training' mapping.")
    if not training.get("data"):
        raise ValueError("Training YAML must define training.data.")
    return training


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="config/train.yaml")
    args = parser.parse_args()
    settings = load_config(project_path(args.config))
    result = train(
        data_path=project_path(str(settings["data"])),
        output_dir=project_path(str(settings.get("output_dir", "models"))),
    )
    print(f"Training complete. Model: {result['model_path']}")


if __name__ == "__main__":
    main()