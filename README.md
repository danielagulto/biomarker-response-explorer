# Biomarker Response Explorer

**Live demo:** https://biomarker-response-explorer.onrender.com  
**Interactive API docs:** https://biomarker-response-explorer.onrender.com/docs  
**Health endpoint:** https://biomarker-response-explorer.onrender.com/api/health

An independent portfolio demo showing how a small machine-learning workflow can be exposed through a web API and browser interface. It is inspired by computational biology use cases but is not affiliated with Omniscope.

> **Important:** All records are synthetic, marker names are placeholders, and the model is not clinically validated. Do not use it for medical decisions.

## Features
- FastAPI REST API with interactive OpenAPI documentation
- SQLite database seeded automatically with 240 synthetic records
- scikit-learn logistic regression pipeline with standardized features
- Feature coefficient visualization and confusion matrix
- Interactive prediction sandbox via `POST /api/predict`
- Search and filter participant records; export CSV from the browser interface
- Input validation and a health-check endpoint

## Tech stack
Python, FastAPI, scikit-learn, SQLite, HTML, CSS, JavaScript, and Chart.js.

## API endpoints
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | Basic service health and data status |
| GET | `/api/summary` | Dataset summary and illustrative model metrics |
| GET | `/api/participants?q=BM-0001&group=Discovery` | Search/filter synthetic participant records |
| POST | `/api/predict` | Return an illustrative model score for supplied features |

Example request body for `POST /api/predict`:
```json
{
  "marker_alpha": 7.0,
  "marker_beta": 4.0,
  "marker_gamma": 5.5,
  "age_years": 50
}
```

## Run locally
Requires Python 3.10+.

```bash
python -m venv .venv
source .venv/bin/activate       # macOS/Linux
# Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Open http://127.0.0.1:8000. API docs: http://127.0.0.1:8000/docs.

## Engineering notes and limitations
The app creates and seeds its SQLite database during startup when the database is empty. The displayed model score is computed on synthetic data; the training-set metric is intentionally labeled as such and is not a reliable estimate of generalization. A real research model would require expert-defined features, approved data governance, appropriate train/validation/test splits, calibration, external validation, and domain review.

## Portfolio talking points
- Separating API, persistence, model training, and browser UI
- Training and serving a scikit-learn pipeline
- Designing predictable REST endpoints and validating request data
- Making model behavior inspectable through coefficients and a confusion matrix
- Communicating limitations clearly and avoiding medical claims

## Deployment
Hosted on Render. The free service may spin down after inactivity, so the first request after a quiet period can take longer to respond.
