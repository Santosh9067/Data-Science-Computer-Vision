"""Load a trained churn model and generate predictions."""

from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import pandas as pd


def predict_frame(model_path: str | Path, features: pd.DataFrame) -> pd.DataFrame:
    """Return predictions and churn probabilities for a feature frame."""
    pipeline = joblib.load(model_path)
    predictions = pipeline.predict(features).astype(int)
    probabilities = pipeline.predict_proba(features)[:, 1]
    return pd.DataFrame(
        {
            "churn_prediction": predictions,
            "churn_probability": probabilities,
        },
        index=features.index,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, help="Path to churn_model.joblib")
    parser.add_argument("--input", required=True, help="Feature CSV path")
    parser.add_argument("--output", default="predictions.csv", help="Output CSV path")
    args = parser.parse_args()

    frame = pd.read_csv(args.input)
    if "churn" in frame.columns:
        frame = frame.drop(columns=["churn"])
    if "customer_id" in frame.columns:
        frame = frame.drop(columns=["customer_id"])
    predictions = predict_frame(args.model, frame)
    output = pd.concat([frame.reset_index(drop=True), predictions.reset_index(drop=True)], axis=1)
    output.to_csv(args.output, index=False)
    print(f"Wrote {len(output)} predictions to {args.output}")


if __name__ == "__main__":
    main()
