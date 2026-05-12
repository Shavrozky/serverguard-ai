from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import Base, engine, SessionLocal
from models import Metric

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