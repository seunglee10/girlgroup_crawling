from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import text
from db.session import SessionLocal


def fetch_artist_ids() -> list[str]:
    sql = text("""
        SELECT DISTINCT spotify_artist_id
        FROM girl_group
        WHERE spotify_artist_id IS NOT NULL
            AND spotify_artist_id <> ''
        ORDER BY spotify_artist_id
    """)

    with SessionLocal() as session:
        rows = session.execute(sql).fetchall()

    return [r[0] for r in rows]


def main():
    artist_ids = fetch_artist_ids()

    print("artist_ids_count:", len(artist_ids))
    print("artist_ids (one per line):")

    for idx, aid in enumerate(artist_ids, start=1):
        print(f"{idx:02d}. {aid}")


if __name__ == "__main__":
    main()