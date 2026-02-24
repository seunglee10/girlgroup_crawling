# 스포티파이 api 수집 담당
# 토큰 발급, 아티스트 조회, 아시트스 앨범 목록 조회, 앨범 트랙 목록 조회

from __future__ import annotations

import base64
import os
from dataclasses import dataclass
import requests
from config.constants import DEFAULT_SPOTIFY_MARKET, SPOTIFY_TOKEN_URL



class SpotifyAuthError(RuntimeError):
    pass


# spotify api를 호출하기 위한 토큰 발급 받기
def get_access_token(client_id:str, client_secret: str) -> str:
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
    resp = requests.post(SPOTIFY_TOKEN_URL, headers=headers, data=data, timeout=10)
    if resp.status_code != 200:
        raise SpotifyAuthError(f"Failed to get access token: {resp.status_code} {resp.text}")
    payload = resp.json()
    return payload["access_token"]


@dataclass(frozen=True)
class SpotifyConfig:
    client_id: str
    client_secret: str
    market: str = DEFAULT_SPOTIFY_MARKET

    @staticmethod
    def from_env() -> SpotifyConfig:
        client_id = os.environ.get("SPOTIFY_CLIENT_ID")
        client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
        market = os.environ.get("SPOTIFY_MARKET", DEFAULT_SPOTIFY_MARKET)
        if not client_id or not client_secret:
            raise SpotifyAuthError("Missing env vars: SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET")
        return SpotifyConfig(client_id=client_id, client_secret=client_secret, market=market)
