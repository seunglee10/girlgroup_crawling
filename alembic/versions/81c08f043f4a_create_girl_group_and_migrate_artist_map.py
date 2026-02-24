"""create girl_group and migrate artist_map

Revision ID: 81c08f043f4a
Revises: d9c02b5b986d
Create Date: 2026-02-23 15:25:10.171777

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "81c08f043f4a"
down_revision: Union[str, Sequence[str], None] = "d9c02b5b986d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "girl_group",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("spotify_name_ko", sa.Text(), nullable=True),
        sa.Column("spotify_name_en", sa.Text(), nullable=True),
        sa.Column("spotify_artist_id", sa.Text(), nullable=True, unique=True),
        sa.Column("brikorea_name", sa.Text(), nullable=False, unique=True),
        sa.Column("lastfm_name", sa.Text(), nullable=False, unique=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.execute(
        """
        INSERT INTO girl_group (brikorea_name, lastfm_name, notes, updated_at)
        SELECT brikorea_name, lastfm_artist_name, notes, updated_at
        FROM artist_map;
    """
    )

    op.drop_table("artist_map")


def downgrade():
    op.create_table(
        "artist_map",
        sa.Column("brikorea_name", sa.Text(), primary_key=True),
        sa.Column("lastfm_artist_name", sa.Text(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.execute(
        """
        INSERT INTO artist_map (brikorea_name, lastfm_artist_name, notes, updated_at)
        SELECT brikorea_name, lastfm_name, notes, updated_at
        FROM girl_group;
    """
    )

    op.drop_table("girl_group")
