# 스포티파이 api 수집 담당
# 토큰 발급, 아티스트 조회, 아시트스 앨범 목록 조회, 앨범 트랙 목록 조회
from __future__ import annotations

import time 
import base64
import os
from pydantic import BaseModel
import requests
from config.constants import (
    DEFAULT_SPOTIFY_MARKET,
    SPOTIFY_TOKEN_URL,
    SPOTIFY_API_BASE_URL,
    SPOTIFY_ARTIST_ALBUMS_LIMIT,
    SPOTIFY_DEFAULT_INCLUDE_GROUPS,
    SPOTIFY_ALBUM_TRACKS_LIMIT,
    SPOTIFY_MAX_RETRIES,
    SPOTIFY_FALLBACK_RETRY_AFTER_SECONDS,
    SPOTIFY_HTTP_TIMEOUT_SECONDS,
)


class SpotifyAuthError(RuntimeError):
    pass


# spotify api를 호출하기 위한 토큰 발급 담당
def get_access_token(client_id: str, client_secret: str) -> str:
    raw = f"{client_id}:{client_secret}".encode("utf-8")
    b64 = base64.b64encode(raw).decode("utf-8")

    # 요청 헤더,바디 만들기
    headers = {
        "Authorization": f"Basic {b64}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    # 애플리케이션 자격증명client_id,secret만으로 API 토큰을 발급받는 방식
    # 나 이런 앱이고 토큰 하나 줘
    data = {
        "grant_type": "client_credentials",
    }

    # 토큰 발급 요청
    resp = requests.post(
        SPOTIFY_TOKEN_URL, headers=headers, data=data, timeout=SPOTIFY_HTTP_TIMEOUT_SECONDS
    )
    if resp.status_code != 200:
        raise SpotifyAuthError(
            f"Failed to get access token: {resp.status_code} {resp.text}"
        )
    payload = resp.json()
    return payload["access_token"]


# 환경변수에서 spotify api를 호출하기 위한 설정을 담당하는 클래스
class SpotifyConfig(BaseModel):
    client_id: str
    client_secret: str
    market: str = DEFAULT_SPOTIFY_MARKET

    @staticmethod
    def from_env() -> SpotifyConfig:
        client_id = os.environ.get("SPOTIFY_CLIENT_ID")
        client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
        market = os.environ.get("SPOTIFY_MARKET", DEFAULT_SPOTIFY_MARKET)
        if not client_id or not client_secret:
            raise SpotifyAuthError(
                "Missing env vars: SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET"
            )
        return SpotifyConfig(
            client_id=client_id, client_secret=client_secret, market=market
        )


# spotify api  호출을 담당하는 클래스
class SpotifyClient:
    def __init__(self, access_token: str, market: str = DEFAULT_SPOTIFY_MARKET):
        self.access_token = access_token
        self.market = market

    # access_token을 이용해 인가 헤더 만들기
    def __headers(self) -> dict:
        return {"Authorization": f"Bearer {self.access_token}"}

    def get(self, path: str, params: dict | None = None) -> dict:
        url = f"{SPOTIFY_API_BASE_URL}/{path}"

        for attempt in range(SPOTIFY_MAX_RETRIES + 1):
            try:
                resp = requests.get(
                    url,
                    headers=self.__headers(),
                    params=params,
                    timeout=SPOTIFY_HTTP_TIMEOUT_SECONDS,
                )
            except requests.exceptions.RequestException as e:
                # timeout, connection error, DNS error 등 (resp 자체가 없는 경우)
                # 마지막 시도면 실패, 아니면 sleep 후 재시도
                if attempt >= SPOTIFY_MAX_RETRIES:
                    raise SpotifyAuthError(f"Network error after retries: {e}") from e

                time.sleep(SPOTIFY_FALLBACK_RETRY_AFTER_SECONDS)
                continue

            # 토큰 문제(만료/오류) → 재시도해도 해결 안 되는 경우가 많아서 즉시 실패 처리
            if resp.status_code == 401:
                raise SpotifyAuthError(f"Unauthorized (401): {resp.text}")

            # 429는 스포티파이가 "너 지금 너무 많이 요청한다"는 것을 의미함
            # Spotify는 보통 언제 다시 요청해도 되는지를 Retry-After 헤더로 알려주니까 알려주면 그거에 맞춰서 재시도하거나 내가 정한 시간 지난 후 재시도하거나 함.
            if resp.status_code == 429:
                retry_after = resp.headers.get("Retry-After")
                if retry_after and retry_after.isdigit():
                    wait_s = int(retry_after)
                else:
                    wait_s = SPOTIFY_FALLBACK_RETRY_AFTER_SECONDS
            
                # 재시도 횟수 초과하면 실패처리하겠다.
                if attempt >= SPOTIFY_MAX_RETRIES:
                    raise SpotifyAuthError(
                        f"Rate limited (429) and max retries exceeded. Last: {resp.text}"
                    )

                time.sleep(wait_s)
                continue

            # 그 외 오류
            if resp.status_code != 200:
                raise SpotifyAuthError(
                    f"GET {path} failed: {resp.status_code} {resp.text}"
                )

            return resp.json()

        raise SpotifyAuthError("Unexpected retry loop exit.")

    # 아티스트 조회
    def get_artist(self, artist_id: str) -> dict:
        return self.get(f"/artists/{artist_id}")

    # 아티스트 앨범 조회
    def list_artist_albums(
        self,
        artist_id: str,
        include_groups: str = SPOTIFY_DEFAULT_INCLUDE_GROUPS,
    ) -> list[dict]:
        items_all: list[dict] = []
        offset = 0

        while True:
            params = {
                "include_groups": include_groups,
                "limit": SPOTIFY_ARTIST_ALBUMS_LIMIT,
                "offset": offset,
                "market": self.market,
            }
            data = self.get(f"/artists/{artist_id}/albums", params=params)
            items = data.get("items", [])

            if not items:
                break

            items_all.extend(items)
            offset += len(items)

        return items_all

    def list_album_tracks(self, album_id: str) -> list[dict]:
        items_all: list[dict] = []
        offset = 0

        while True:
            params = {
                "limit": SPOTIFY_ALBUM_TRACKS_LIMIT,
                "offset": offset,
                "market": self.market,
            }
            data = self.get(f"/albums/{album_id}/tracks", params=params)
            items = data.get("items", [])

            if not items:
                break

            items_all.extend(items)
            offset += len(items)

        return items_all
