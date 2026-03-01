from dotenv import load_dotenv
load_dotenv()

from crawlers.spotify_api import SpotifyConfig, SpotifyClient, get_access_token


def main():
    artist_id = "6RHTUrRF63xao58xh9FXYJ"
    config = SpotifyConfig.from_env()
    access_token = get_access_token(config.client_id, config.client_secret)
    client = SpotifyClient(access_token, market = config.market)
    artist = client.get_artist(artist_id)
    print("artist_id: ", artist["id"])
    print("artist_name: ", artist["name"])


if __name__ == "__main__":
    main()