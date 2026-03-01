import csv
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from crawlers.spotify_api import SpotifyConfig, get_access_token, SpotifyClient


def export_artist_tracks_csv(artist_id: str, output_path: str) -> None:
    config = SpotifyConfig.from_env()
    token = get_access_token(config.client_id, config.client_secret)
    client = SpotifyClient(access_token=token, market=config.market)

    # artist_name 확보
    artist = client.get_artist(artist_id)
    artist_name = artist["name"]

    # 앨범/싱글 목록 수집
    albums = client.list_artist_albums(artist_id)

    # 앨범별 트랙 수집할 때 track_id 기준으로 중복 제거
    tracks_by_id: dict[str, dict] = {}

    for album in albums:
        album_id = album["id"]
        tracks = client.list_album_tracks(album_id)

        for t in tracks:
            track_id = t["id"]
            if not track_id:
                continue
            # track_id 기준으로 최초 1회만 저장
            tracks_by_id.setdefault(track_id, t)

    # CSV 저장
    rows = []
    for t in tracks_by_id.values():
        rows.append(
            {
                "artist_id": artist_id,
                "artist_name": artist_name,
                "track_id": t["id"],
                "track_name": t["name"],
            }
        )

    # csv를 저장할 폴더만들기
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "artist_id",
                "artist_name",
                "track_id",
                "track_name",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"saved: {output_path} (tracks={len(rows)})")


def main():
    artist_id = "6RHTUrRF63xao58xh9FXYJ"
    id = 2
    export_artist_tracks_csv(artist_id, output_path=f"exports/tracks/{id}.csv")


if __name__ == "__main__":
    main()
