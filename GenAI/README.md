# Churn Classification

Reusable baseline for training and serving a binary customer-churn model.

## Layout

- `data/sample_churn.csv`: small synthetic smoke-test dataset. Replace it with an approved real dataset using the same target contract.
- `churn_ml/train.py`: trains and saves a preprocessing-plus-model artifact.
- `churn_ml/predict.py`: shared prediction functions and CLI.
- `churn_ml/api.py`: optional FastAPI deployment service.
- `config/train.yaml`: training configuration.
- `config/deploy.yaml`: deployment configuration.
- `scripts/run_training.py`: YAML-driven training launcher.
- `scripts/run_deployment.py`: YAML-driven FastAPI launcher.
- `models/`: generated artifacts; not committed by the scripts.
- `tests/`: fast unit tests for inference behavior.

## Install

```powershell
cd C:\Users\Santosh\MY_GITHUB_REPO\Data-Science-Computer-Vision\GenAI
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Train

```powershell
python -m churn_ml.train --data data/sample_churn.csv --output-dir models
```

Or run training from YAML configuration:

```powershell
.\.venv\Scripts\python.exe -m scripts.run_training --config config/train.yaml
```

Edit `config/train.yaml` to select another dataset or artifact directory.

The input must contain a `churn` column. Churn accepts `0/1`, `true/false`, or common yes/no labels. `customer_id` is excluded automatically when present.

## Predict from CSV

```powershell
python -m churn_ml.predict --model models/churn_model.joblib --input data/sample_churn.csv --output predictions.csv
```

The input for prediction must contain feature columns used during training. The output includes `churn_prediction` and `churn_probability`.

## Serve

```powershell
uvicorn churn_ml.api:app --host 0.0.0.0 --port 8000
```

Or start the API from YAML configuration:

```powershell
.\.venv\Scripts\python.exe -m scripts.run_deployment --config config/deploy.yaml
```

Edit `config/deploy.yaml` to change the model path, host, or port. The deployment launcher sets `CHURN_MODEL_PATH` before starting Uvicorn.

Example request:

```powershell
Invoke-RestMethod -Method Post http://localhost:8000/predict -ContentType 'application/json' -Body (@{
  tenure_months = 6
  monthly_charges = 95.1
  total_charges = 570.6
  contract_type = 'Month-to-month'
  payment_method = 'Electronic check'
  internet_service = 'Fiber optic'
  support_tickets = 3
  senior_citizen = 1
} | ConvertTo-Json)
```

This is a baseline reference implementation, not a production risk or retention decision system. Before deployment, add data validation, authentication, monitoring, drift checks, model versioning, and an approved evaluation protocol.
