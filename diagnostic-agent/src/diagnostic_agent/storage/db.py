"""Persistencia local del edge (SQLite + SQLAlchemy): sesiones, lecturas y anomalías."""

from datetime import datetime
from pathlib import Path

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from mecanico_contracts import DetectedAnomaly, OBDReading


class Base(DeclarativeBase):
    """Base declarativa del esquema local."""


class CaptureSession(Base):
    __tablename__ = "capture_sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    vehicle_id: Mapped[str] = mapped_column(String, index=True)
    device_id: Mapped[str] = mapped_column(String)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    sample_rate_hz: Mapped[float] = mapped_column(Float)


class ReadingRow(Base):
    __tablename__ = "readings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("capture_sessions.id"), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    pid: Mapped[str] = mapped_column(String, index=True)
    value: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String)


class AnomalyRow(Base):
    __tablename__ = "anomalies"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("capture_sessions.id"), index=True)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    detector: Mapped[str] = mapped_column(String)
    model_name: Mapped[str | None] = mapped_column(String, nullable=True)
    model_version: Mapped[str | None] = mapped_column(String, nullable=True)
    score: Mapped[float] = mapped_column(Float)
    threshold: Mapped[float] = mapped_column(Float)
    involved_pids: Mapped[str] = mapped_column(String)  # CSV simple


class EdgeStore:
    """Repositorio mínimo del edge sobre SQLite."""

    def __init__(self, db_path: str | Path) -> None:
        path = Path(db_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(f"sqlite:///{path}")
        Base.metadata.create_all(self.engine)

    def start_session(
        self, session_id: str, vehicle_id: str, device_id: str, started_at: datetime, rate: float
    ) -> None:
        with Session(self.engine) as s:
            s.add(
                CaptureSession(
                    id=session_id,
                    vehicle_id=vehicle_id,
                    device_id=device_id,
                    started_at=started_at,
                    sample_rate_hz=rate,
                )
            )
            s.commit()

    def add_readings(self, session_id: str, readings: list[OBDReading]) -> None:
        with Session(self.engine) as s:
            s.add_all(
                ReadingRow(
                    session_id=session_id,
                    timestamp=r.timestamp,
                    pid=r.pid,
                    value=r.value,
                    unit=r.unit,
                )
                for r in readings
            )
            s.commit()

    def add_anomaly(self, session_id: str, anomaly: DetectedAnomaly) -> None:
        with Session(self.engine) as s:
            s.add(
                AnomalyRow(
                    id=anomaly.anomaly_id,
                    session_id=session_id,
                    detected_at=anomaly.detected_at,
                    detector=anomaly.detector.value,
                    model_name=anomaly.model_name,
                    model_version=anomaly.model_version,
                    score=anomaly.score,
                    threshold=anomaly.threshold,
                    involved_pids=",".join(anomaly.involved_pids),
                )
            )
            s.commit()

    def count(self, table: type[Base]) -> int:
        from sqlalchemy import func, select

        with Session(self.engine) as s:
            return s.execute(select(func.count()).select_from(table)).scalar_one()
