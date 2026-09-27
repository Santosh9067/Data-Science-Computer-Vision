"""Start the churn API from a YAML configuration file."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any

import uvicorn
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def project_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path


def load_config(config_path: str | Path) -> dict[str, Any]:
    with Path(config_path).open("r", encoding="utf-8") as stream:
        config = yaml.safe_load(stream) or {}
    deployment = config.get("deployment")
    if not isinstance(deployment, dict):
        raise ValueError("YAML must contain a 'deployment' mapping.")
    if not deployment.get("model_path"):
        raise ValueError("Deployment YAML must define deployment.model_path.")
    return deployment


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="config/deploy.yaml")
    args = parser.parse_args()
    settings = load_config(project_path(args.config))
    model_path = project_path(str(settings["model_path"]))
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model not found at {model_path}. Run the training launcher first."
        )
    os.environ["CHURN_MODEL_PATH"] = str(model_path)
    uvicorn.run(
        "churn_ml.api:app",
        host=str(settings.get("host", "127.0.0.1")),
        port=int(settings.get("port", 8000)),
        workers=int(settings.get("workers", 1)),
        app_dir=str(PROJECT_ROOT),
    )


if __name__ == "__main__":
    main()