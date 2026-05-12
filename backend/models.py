from sqlalchemy import Column, Integer, Float, DateTime
from datetime import datetime

from database import Base


class Metric(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True)
    cpu_percent = Column(Float, nullable=False)
    ram_percent = Column(Float, nullable=False)
    disk_percent = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)