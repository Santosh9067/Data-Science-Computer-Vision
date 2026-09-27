"""Train and persist a churn classification pipeline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

TARGET_COLUMN = "churn"
ID_COLUMNS = {"customer_id", "customerid", "id"}


def parse_target(values: pd.Series) -> pd.Series:
    """Normalize common binary churn labels to integer values."""
    if pd.api.types.is_numeric_dtype(values):
        numeric = pd.to_numeric(values, errors="raise")
        if not set(numeric.dropna().unique()).issubset({0, 1}):
            raise ValueError("Numeric churn labels must contain only 0 and 1.")
        return numeric.astype(int)

    normalized = values.astype(str).str.strip().str.lower()
    mapping = {
        "0": 0,
        "1": 1,
        "no": 0,
        "yes": 1,
        "false": 0,
        "true": 1,
        "stay": 0,
        "churn": 1,
    }
    unknown = sorted(set(normalized.dropna()) - mapping.keys())
    if unknown:
        raise ValueError(f"Unsupported churn labels: {unknown}")
    return normalized.map(mapping).astype(int)


def build_pipeline(features: pd.DataFrame) -> Pipeline:
    numeric_columns = features.select_dtypes(include="number").columns.tolist()
    categorical_columns = [
        column for column in features.columns if column not in numeric_columns
    ]

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, numeric_columns),
            ("categorical", categorical_pipeline, categorical_columns),
        ],
        remainder="drop",
    )
    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", LogisticRegression(max_iter=1000, class_weight="balanced")),
        ]
    )


def train(data_path: str | Path, output_dir: str | Path) -> dict[str, Any]:
    data_path = Path(data_path)
    output_dir = Path(output_dir)
    frame = pd.read_csv(data_path)
    if TARGET_COLUMN not in frame.columns:
        raise ValueError(f"Dataset must contain a '{TARGET_COLUMN}' column.")

    target = parse_target(frame.pop(TARGET_COLUMN))
    drop_columns = [column for column in frame.columns if column.lower() in ID_COLUMNS]
    features = frame.drop(columns=drop_columns)
    if features.empty:
        raise ValueError("Dataset must contain at least one feature column.")
    if target.nunique() != 2:
        raise ValueError("Churn target must contain both classes 0 and 1.")

    train_features, test_features, train_target, test_target = train_test_split(
        features,
        target,
        test_size=0.2,
        random_state=42,
        stratify=target,
    )
    pipeline = build_pipeline(train_features)
    pipeline.fit(train_features, train_target)
    predictions = pipeline.predict(test_features)
    probabilities = pipeline.predict_proba(test_features)[:, 1]

    metrics: dict[str, Any] = {
        "accuracy": float(accuracy_score(test_target, predictions)),
        "roc_auc": float(roc_auc_score(test_target, probabilities)),
        "classification_report": classification_report(
            test_target, predictions, output_dict=True
        ),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    model_path = output_dir / "churn_model.joblib"
    metrics_path = output_dir / "metrics.json"
    metadata_path = output_dir / "metadata.json"
    joblib.dump(pipeline, model_path)
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    metadata_path.write_text(
        json.dumps(
            {
                "target_column": TARGET_COLUMN,
                "feature_columns": features.columns.tolist(),
                "dropped_columns": drop_columns,
                "model_path": model_path.name,
                "random_state": 42,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return {"model_path": str(model_path), "metrics": metrics}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", required=True, help="Training CSV path")
    parser.add_argument("--output-dir", default="models", help="Artifact directory")
    args = parser.parse_args()
    result = train(args.data, args.output_dir)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
