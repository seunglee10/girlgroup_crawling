from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .track import tracks


class GirlGroup(Base):
    __tablename__ = "girl_group"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    spotify_name_ko: Mapped[str | None] = mapped_column(Text, nullable=True)
    spotify_name_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    spotify_artist_id: Mapped[str | None] = mapped_column(
        Text, nullable=True, unique=True
    )

    brikorea_name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    lastfm_name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    ranks: Mapped[list[GirlGroupRank]] = relationship(back_populates="girl_group")
    track_list: Mapped[list[tracks]] = relationship(back_populates="girl_group")


class GirlGroupRank(Base):
    __tablename__ = "girl_group_rank"

    snapshot_month: Mapped[str] = mapped_column(Date, primary_key=True, nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    girl_group_id: Mapped[int] = mapped_column(
        ForeignKey("girl_group.id"), primary_key=True, nullable=False
    )

    brand_score: Mapped[int] = mapped_column(BigInteger, nullable=False)
    activity_score: Mapped[int] = mapped_column(BigInteger, nullable=False)
    media_score: Mapped[int] = mapped_column(BigInteger, nullable=False)
    communication_score: Mapped[int] = mapped_column(BigInteger, nullable=False)
    community_score: Mapped[int] = mapped_column(BigInteger, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    girl_group: Mapped[GirlGroup] = relationship(back_populates="ranks")
