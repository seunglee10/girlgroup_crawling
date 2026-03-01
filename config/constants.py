# 상수 정의

# =========================
# Spotify API URLs
# =========================
SPOTIFY_API_BASE_URL = "https://api.spotify.com/v1"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"

# =========================
# Spotify 기본 설정
# =========================
DEFAULT_SPOTIFY_MARKET = "KR"
SPOTIFY_DEFAULT_INCLUDE_GROUPS = "album,single"


# =========================
# Spotify pagination 기본 설정
# =========================
SPOTIFY_ARTIST_ALBUMS_LIMIT = 10
SPOTIFY_ALBUM_TRACKS_LIMIT = 50


# =========================
# HTTP / Retry 정책(50그룹 대비 최소 안전장치)
# =========================
SPOTIFY_HTTP_TIMEOUT_SECONDS = 10
SPOTIFY_MAX_RETRIES = 3
SPOTIFY_FALLBACK_RETRY_AFTER_SECONDS = 2


# =========================
# Export 기본 설정
# =========================
DEFAULT_EXPORT_DIR = "exports"