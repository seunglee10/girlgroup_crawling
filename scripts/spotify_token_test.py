# 스포티파이 토큰 발급 테스트
from dotenv import load_dotenv
load_dotenv()

from crawlers.spotify_api import SpotifyConfig, get_access_token


def main():
    config = SpotifyConfig.from_env()
    token = get_access_token(config.client_id, config.client_secret)
    print(f"Access token: {token}")

if __name__ == "__main__":
    main()