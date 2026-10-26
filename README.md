# Biomarker Response Explorer

An independent portfolio demo showing how a small machine-learning workflow can be exposed through a web API and browser interface. It is inspired by computational biology use cases but is not affiliated with Omniscope.

**Important:** all records are synthetic, marker names are placeholders, and the model is not clinically validated. Do not use it for medical decisions.

## Features
- FastAPI REST API
- SQLite database seeded with 240 synthetic records
- Logistic regression pipeline using scikit-learn
- Feature coefficient visualization and confusion matrix
- Interactive prediction sandbox via `POST /api/predict`
- Search/filter participant records and export CSV
- API input validation and health endpoint

## Tech stack
Python, FastAPI, scikit-learn, SQLite, HTML, CSS, JavaScript, Chart.js.

## Run locally
Requires Python 3.10+.

```bash
python -m venv .venv
source .venv/bin/activate       # macOS/Linux
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Open http://127.0.0.1:8000. API docs: http://127.0.0.1:8000/docs

## API endpoints
- `GET /api/health`
- `GET /api/summary`
- `GET /api/participants?q=BM-0001&group=Discovery`
- `POST /api/predict`

Example request body:
```json
{
  "marker_alpha": 7.0,
  "marker_beta": 4.0,
  "marker_gamma": 5.5,
  "age_years": 50
}
```

## Known limitation
The displayed score is computed on synthetic data and the training-set metric is intentionally labeled as such. A real research model would require expert-defined features, approved data governance, appropriate train/validation/test splits, calibration, external validation, and domain review.

## Portfolio talking points
- Separating API, data persistence, and browser UI
- Training and serving a scikit-learn pipeline
- Designing predictable REST endpoints
- Handling input validation and documenting limitations
- Visualizing model behavior without presenting it as a medical diagnosis
