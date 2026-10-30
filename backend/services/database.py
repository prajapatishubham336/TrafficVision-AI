
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    DateTime
)
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "trafficvision.db"

DATABASE_URL = f"sqlite:///{DB_PATH.as_posix()}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


class TrafficRecord(Base):
    __tablename__ = "traffic_records"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_type = Column(String, nullable=False)
    direction = Column(String, nullable=False)
    tracking_id = Column(Integer, nullable=True)
    timestamp = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


def init_db():
    Base.metadata.create_all(bind=engine)


def save_traffic_record(
    vehicle_type,
    direction,
    tracking_id=None
):
    db = SessionLocal()

    try:
        record = TrafficRecord(
            vehicle_type=vehicle_type,
            direction=direction,
            tracking_id=tracking_id
        )

        db.add(record)
        db.commit()
        db.refresh(record)

        return record.id

    finally:
        db.close()
