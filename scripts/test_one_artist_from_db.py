from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import text
from db.session import SessionLocal
from crawlers.spotify_api import SpotifyConfig, get_access_token, SpotifyClient


# DB에서 아티스트 ID 목록 가져와서 리스트로 만들기
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
    # DB에서 목록 가져오기
    artist_ids = fetch_artist_ids()
    print("total artists:", len(artist_ids))

    if not artist_ids:
        print("No artist ids found.")
        return

    # 첫 번째 아티스트 선택(테스트용)
    artist_id = artist_ids[0]
    print("testing artist_id:", artist_id)

    # Spotify 클라이언트 준비
    config = SpotifyConfig.from_env()
    token = get_access_token(config.client_id, config.client_secret)
    client = SpotifyClient(access_token=token, market=config.market)

    # 아티스트 이름 조회
    artist = client.get_artist(artist_id)
    artist_name = artist["name"]
    print("artist_name:", artist_name)

    # 앨범 목록 조회
    albums = client.list_artist_albums(artist_id)
    print("album_count:", len(albums))

    # 전곡 수집해서 딕셔너리로 만들기 (track_id 기준으로 중복제거하기) 
    tracks_by_id: dict[str, dict] = {}

    for album in albums:
        album_id = album["id"]
        tracks = client.list_album_tracks(album_id)

        for t in tracks:
            tid = t.get("id")
            if not tid:
                continue
            tracks_by_id.setdefault(tid, t)

    print("unique_track_count:", len(tracks_by_id))

    # 샘플 출력
    print("sample tracks:")
    for i, t in enumerate(tracks_by_id.values()):
        print("-", t["name"])


if __name__ == "__main__":
    main()