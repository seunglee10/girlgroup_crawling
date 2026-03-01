from dotenv import load_dotenv

load_dotenv()

from crawlers.spotify_api import SpotifyConfig, get_access_token, SpotifyClient

# 각각 따로 존재하는 함수들을 묶어서 하나의 실제 작업 흐름으로 묶는걸 오케스트레이션이라고 함.
def main():
    cfg = SpotifyConfig.from_env()
    token = get_access_token(cfg.client_id, cfg.client_secret)
    client = SpotifyClient(access_token=token, market=cfg.market)

    artist_id = "6RHTUrRF63xao58xh9FXYJ"  # IVE
    albums = client.list_artist_albums(artist_id)

    print("artist_id:", artist_id)
    print("albums_count:", len(albums))

    for a in albums[:5]:
        print("-", a["name"], f"(id={a['id']})")


if __name__ == "__main__":
    main()
