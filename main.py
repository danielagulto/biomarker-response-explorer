from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import sqlite3, random
from datetime import date, timedelta
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix

BASE = Path(__file__).resolve().parent
DB_PATH = BASE / "biomarker_explorer.db"
app = FastAPI(title="Biomarker Response Explorer API", version="1.0.0")
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")

FEATURES = ["marker_alpha", "marker_beta", "marker_gamma", "age_years"]
def connect():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = connect()
    con.execute("""CREATE TABLE IF NOT EXISTS participants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        participant_code TEXT UNIQUE NOT NULL,
        study_group TEXT NOT NULL,
        collection_date TEXT NOT NULL,
        marker_alpha REAL NOT NULL,
        marker_beta REAL NOT NULL,
        marker_gamma REAL NOT NULL,
        age_years INTEGER NOT NULL,
        response_label INTEGER NOT NULL
    )""")
    if con.execute("SELECT COUNT(*) FROM participants").fetchone()[0] == 0:
        rng = random.Random(415)
        rows = []
        today = date.today()
        for i in range(1, 241):
            alpha = rng.gauss(6.5, 1.7)
            beta = rng.gauss(4.8, 1.5)
            gamma = rng.gauss(5.1, 1.8)
            age = int(max(18, min(85, rng.gauss(51, 13))))
            # Synthetic rule with noise; not based on real patients or biology.
            logit = 0.9 * (alpha - 6.0) - 0.65 * (beta - 5.0) + 0.28 * (gamma - 5.0) - 0.012 * (age - 50)
            p = 1 / (1 + pow(2.71828, -logit))
            response = 1 if rng.random() < p else 0
            rows.append((f"BM-{i:04d}", rng.choice(["Discovery", "Validation"]), (today-timedelta(days=rng.randint(0,365))).isoformat(),
                         round(max(0,alpha),2),round(max(0,beta),2),round(max(0,gamma),2),age,response))
        con.executemany("""INSERT INTO participants
            (participant_code, study_group, collection_date, marker_alpha, marker_beta, marker_gamma, age_years, response_label)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", rows)
    con.commit()
    con.close()

def get_data():
    con=connect()
    rows=[dict(r) for r in con.execute("SELECT * FROM participants ORDER BY collection_date DESC").fetchall()]
    con.close()
    return rows

def train_model():
    rows=get_data()
    X=[[r[k] for k in FEATURES] for r in rows]
    y=[r["response_label"] for r in rows]
    model=make_pipeline(StandardScaler(),LogisticRegression(max_iter=1000,random_state=42))
    model.fit(X,y)
    preds=model.predict(X)
    return model, rows, accuracy_score(y,preds), confusion_matrix(y,preds,labels=[0,1]).tolist()

@app.on_event("startup")
def startup():
    init_db()

@app.get("/", response_class=HTMLResponse)
def home():
    return (BASE/"static"/"index.html").read_text(encoding="utf-8")

@app.get("/api/summary")
def summary():
    rows=get_data()
    n=len(rows)
    positive=sum(r["response_label"] for r in rows)
    model,_,accuracy,cm=train_model()
    return {
        "participants":n,
        "positive_rate":round(100*positive/n,1) if n else 0,
        "model_accuracy_training":round(100*accuracy,1),
        "features":[{"name":name,"coefficient":round(float(coef),3)} for name,coef in zip(FEATURES,model[-1].coef_[0])],
        "confusion_matrix":cm,
        "note":"Synthetic dataset. Training-set score is for demonstration only and is not a valid estimate of real-world performance."
    }

@app.get("/api/participants")
def participants(q: str = Query(default="", max_length=80), group: str = ""):
    sql="SELECT * FROM participants WHERE 1=1"; params=[]
    if q:
        sql+=" AND participant_code LIKE ?"; params.append(f"%{q}%")
    if group:
        sql+=" AND study_group = ?"; params.append(group)
    sql+=" ORDER BY collection_date DESC LIMIT 250"
    con=connect(); rows=con.execute(sql,params).fetchall(); con.close()
    return {"items":[dict(r) for r in rows],"count":len(rows)}

@app.post("/api/predict")
def predict(payload: dict):
    required=FEATURES
    missing=[k for k in required if k not in payload]
    if missing:
        from fastapi import HTTPException
        raise HTTPException(status_code=422,detail=f"Missing fields: {', '.join(missing)}")
    try:
        values=[float(payload[k]) for k in required]
    except (TypeError,ValueError):
        from fastapi import HTTPException
        raise HTTPException(status_code=422,detail="All feature values must be numeric.")
    if not all(v == v and abs(v) < 1e6 for v in values):
        from fastapi import HTTPException
        raise HTTPException(status_code=422,detail="Please enter finite, reasonable numeric values.")
    model,_,_,_=train_model()
    probability=float(model.predict_proba([values])[0][1])
    return {"illustrative_response_probability":round(probability,4),
            "label":"Higher model score" if probability>=0.5 else "Lower model score",
            "warning":"Synthetic demonstration only. Not clinically validated; do not use for diagnosis or treatment."}

@app.get("/api/health")
def health():
    return {"status":"ok","database":"sqlite","model":"logistic regression","data":"synthetic"}
