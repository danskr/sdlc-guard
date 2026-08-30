from __future__ import annotations

from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String, Text, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

from .config import get_settings


class Base(DeclarativeBase):
    pass


class Artifact(Base):
    __tablename__ = "artifacts"

    artifact_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(128), index=True)
    artifact_type: Mapped[str] = mapped_column(String(64), index=True)
    title: Mapped[str] = mapped_column(String(512))
    content: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default="approved")
    feature_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    source_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    version: Mapped[str] = mapped_column(String(32), default="1")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    outgoing: Mapped[list["ArtifactRelationship"]] = relationship(
        foreign_keys="ArtifactRelationship.source_id", cascade="all, delete-orphan"
    )


class ArtifactRelationship(Base):
    __tablename__ = "artifact_relationships"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source_id: Mapped[str] = mapped_column(ForeignKey("artifacts.artifact_id", ondelete="CASCADE"), index=True)
    relation_type: Mapped[str] = mapped_column(String(64), index=True)
    target_id: Mapped[str] = mapped_column(ForeignKey("artifacts.artifact_id", ondelete="CASCADE"), index=True)


settings = get_settings()
engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_artifact(artifact_id: str) -> Artifact | None:
    with SessionLocal() as session:
        return session.get(Artifact, artifact_id)


def list_artifacts(project_id: str = "ecommerce-demo") -> list[Artifact]:
    with SessionLocal() as session:
        return list(session.scalars(select(Artifact).where(Artifact.project_id == project_id)).all())
