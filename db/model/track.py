from sqlalchemy import (
    BigInteger,
    Date,
    DateTime,
    ForeignKey,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from .base import Base


class tracks(Base):
    __tablename__ = "tracks"

    track_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    girl_group_id: Mapped[int] = mapped_column(
        ForeignKey("girl_group.id"), nullable=False
    )
    track_name: Mapped[str] = mapped_column(Text, nullable=False)

    track_mbid: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("girl_group_id", "track_name", name="uq_artist_track"),
    )

    girl_group = relationship("GirlGroup", back_populates="track_list")


class TrackListeningSnapshot(Base):
    __tablename__ = "track_listening_snapshot"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    snapshot_date: Mapped[str] = mapped_column(Date, nullable=False)
    track_id: Mapped[int] = mapped_column(ForeignKey("tracks.track_id"), nullable=False)

    listeners_total: Mapped[int] = mapped_column(BigInteger, nullable=False)
    playcount_total: Mapped[int] = mapped_column(BigInteger, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("snapshot_date", "track_id", name="uq_snapshot_track"),
    )

    track = relationship("tracks")
