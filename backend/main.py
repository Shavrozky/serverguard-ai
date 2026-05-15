from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import Base, engine, SessionLocal
from models import Metric, Anomaly
from anomaly import detect_anomalies
from datetime import datetime, timedelta

Base.metadata.create_all(bind=engine)

app = FastAPI(title="ServerGuard AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MetricCreate(BaseModel):
    cpu_percent: float
    ram_percent: float
    disk_percent: float


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def analyze_health(metric: Metric):
    if metric is None:
        return {
            "status": "unknown",
            "message": "No metrics available yet",
            "issues": [],
        }

    issues = []

    checks = [
        ("CPU", metric.cpu_percent),
        ("RAM", metric.ram_percent),
        ("Disk", metric.disk_percent),
    ]

    for name, value in checks:
        if value >= 90:
            issues.append({
                "level": "critical",
                "message": f"{name} usage is critical: {value}%"
            })
        elif value >= 80:
            issues.append({
                "level": "warning",
                "message": f"{name} usage is high: {value}%"
            })

    has_critical = any(issue["level"] == "critical" for issue in issues)
    has_warning = any(issue["level"] == "warning" for issue in issues)

    if has_critical:
        status = "critical"
        message = "Server resource usage is critical"
    elif has_warning:
        status = "warning"
        message = "Server resource usage needs attention"
    else:
        status = "healthy"
        message = "Server is healthy"

    return {
        "status": status,
        "message": message,
        "issues": issues,
    }


@app.get("/")
def root():
    return {
        "message": "ServerGuard AI API is running"
    }

@app.post("/metrics")
def create_metric(payload: MetricCreate, db: Session = Depends(get_db)):
    metric = Metric(
        cpu_percent=payload.cpu_percent,
        ram_percent=payload.ram_percent,
        disk_percent=payload.disk_percent,
    )

    db.add(metric)
    db.commit()
    db.refresh(metric)

    return {
        "message": "Metric saved",
        "data": {
            "id": metric.id,
            "cpu_percent": metric.cpu_percent,
            "ram_percent": metric.ram_percent,
            "disk_percent": metric.disk_percent,
            "created_at": metric.created_at,
        },
    }


@app.get("/metrics")
def get_metrics(limit: int = 50, db: Session = Depends(get_db)):
    metrics = (
        db.query(Metric)
        .order_by(Metric.created_at.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": metric.id,
            "cpu_percent": metric.cpu_percent,
            "ram_percent": metric.ram_percent,
            "disk_percent": metric.disk_percent,
            "created_at": metric.created_at,
        }
        for metric in reversed(metrics)
    ]


@app.get("/metrics/latest")
def get_latest_metric(db: Session = Depends(get_db)):
    metric = (
        db.query(Metric)
        .order_by(Metric.created_at.desc())
        .first()
    )

    if metric is None:
        return None

    return {
        "id": metric.id,
        "cpu_percent": metric.cpu_percent,
        "ram_percent": metric.ram_percent,
        "disk_percent": metric.disk_percent,
        "created_at": metric.created_at,
    }


@app.get("/health")
def get_health(db: Session = Depends(get_db)):
    metric = (
        db.query(Metric)
        .order_by(Metric.created_at.desc())
        .first()
    )

    health = analyze_health(metric)

    return {
        **health,
        "latest": None if metric is None else {
            "id": metric.id,
            "cpu_percent": metric.cpu_percent,
            "ram_percent": metric.ram_percent,
            "disk_percent": metric.disk_percent,
            "created_at": metric.created_at,
        }
    }

def save_anomalies(db: Session, anomalies: list[dict]):
    saved_anomalies = []
    cooldown_time = datetime.utcnow() - timedelta(seconds=60)

    for item in anomalies:
        existing_anomaly = (
            db.query(Anomaly)
            .filter(
                Anomaly.metric_name == item["metric"],
                Anomaly.created_at >= cooldown_time,
            )
            .order_by(Anomaly.created_at.desc())
            .first()
        )

        if existing_anomaly:
            continue

        anomaly = Anomaly(
            metric_name=item["metric"],
            metric_value=item["value"],
            z_score=item["z_score"],
            message=item["message"],
        )

        db.add(anomaly)
        saved_anomalies.append(anomaly)

    db.commit()

    for anomaly in saved_anomalies:
        db.refresh(anomaly)

    return saved_anomalies

@app.get("/anomalies")
def get_anomalies(limit: int = 50, db: Session = Depends(get_db)):
    metrics = (
        db.query(Metric)
        .order_by(Metric.created_at.desc())
        .limit(limit)
        .all()
    )

    metrics = list(reversed(metrics))

    result = detect_anomalies(metrics)

    latest = metrics[-1] if metrics else None

    saved = []

    if result["status"] == "anomaly_detected":
        saved_anomalies = save_anomalies(db, result["anomalies"])

        saved = [
            {
                "id": anomaly.id,
                "metric": anomaly.metric_name,
                "value": anomaly.metric_value,
                "z_score": anomaly.z_score,
                "message": anomaly.message,
                "created_at": anomaly.created_at,
            }
            for anomaly in saved_anomalies
        ]

    return {
        **result,
        "saved": saved,
        "latest": None if latest is None else {
            "id": latest.id,
            "cpu_percent": latest.cpu_percent,
            "ram_percent": latest.ram_percent,
            "disk_percent": latest.disk_percent,
            "created_at": latest.created_at,
        },
    }

@app.get("/anomalies/history")
def get_anomaly_history(limit: int = 20, db: Session = Depends(get_db)):
    anomalies = (
        db.query(Anomaly)
        .order_by(Anomaly.created_at.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": anomaly.id,
            "metric": anomaly.metric_name,
            "value": anomaly.metric_value,
            "z_score": anomaly.z_score,
            "message": anomaly.message,
            "created_at": anomaly.created_at,
        }
        for anomaly in anomalies
    ]