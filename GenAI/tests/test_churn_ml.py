from pathlib import Path

import pandas as pd

from churn_ml.predict import predict_frame
from churn_ml.train import train


ROOT = Path(__file__).parents[1]
DATA_PATH = ROOT / "data" / "sample_churn.csv"


def test_train_and_predict(tmp_path: Path) -> None:
    result = train(DATA_PATH, tmp_path)
    model_path = Path(result["model_path"])
    assert model_path.exists()

    features = pd.read_csv(DATA_PATH).drop(columns=["customer_id", "churn"])
    predictions = predict_frame(model_path, features.head(3))
    assert list(predictions.columns) == ["churn_prediction", "churn_probability"]
    assert len(predictions) == 3
    assert predictions["churn_probability"].between(0, 1).all()
