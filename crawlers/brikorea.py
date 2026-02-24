# crawlers/brikorea.py : brikorea 사이트에서 걸그룹 순위 데이터를 가져와 DB에 저장

import os
import re
from datetime import date
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

BRIKOREA_URL = "https://brikorea.com/rk/girl2601"

# 2026년 1월 같은 문자열에서 원하는 데이터 추출하는 정규식
# (\d{4}) → 연도(4자리)
# (\d{1,2}) → 월(1~2자리)
# \s*는 공백이 있어도/없어도 매칭되도록 함.
TITLE_RE = re.compile(r"(\d{4})\s*년\s*(\d{1,2})\s*월")


# title(문자열)에서 연/월을 뽑아 date로 반환
# 월 단위 데이터를 Date 타입으로 저장하기 위해 해당 월의 첫 날을 대표값으로 사용한다
# 2026년1월 데이터 가져다 써서 일에 대한 정보가 없기 때문에 임의로 1일을 만듦
def parse_snapshot_month(title: str) -> date:
    m = TITLE_RE.search(title)
    if not m:
        raise ValueError(f"snapshot_month parse fail (title): {title}")
    year = int(m.group(1))
    month = int(m.group(2))
    return date(year, month, 1)


# 숫자 문자열을 int로 변환
def parse_int(s: str) -> int:
    return int(s.replace(",", "").strip())


# html을 문자열로 반환
def fetch_html(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    }
    r = requests.get(url, headers=headers, timeout=15)
    r.raise_for_status()  # HTTP 상태 코드가 200대가 아니면 예외 발생
    return r.text


# 페이지에서 제목 추출
def extract_title(soup: BeautifulSoup) -> str:
    # 1) 먼저 문서에서 "YYYY년 M월"이 포함된 텍스트를 우선 탐색
    text_candidates = []
    for tag in soup.find_all(["h1", "h2", "h3", "div", "p"]):
        t = tag.get_text(strip=True)
        # 텍스트가 비어있지 않고 “YYYY년 M월” 패턴이 있으면 후보로 저장
        if t and TITLE_RE.search(t):
            text_candidates.append(t)

    if text_candidates:
        # 가장 처음 잡힌 후보를 사용
        return text_candidates[0]

    # 2) 그래도 못 찾으면 전체 텍스트에서 탐색(최후수단)
    all_text = soup.get_text(" ", strip=True)
    m = TITLE_RE.search(all_text)
    if not m:
        raise ValueError("Cannot find title containing 'YYYY년 M월' in page.")
    # 매칭된 연/월로 “YYYY년 M월” 형태로 만든 문자열 반환
    return f"{m.group(1)}년 {m.group(2)}월"


# Top50 추출
def extract_top_rows(soup: BeautifulSoup, top_n: int = 50):
    """
    표의 각 row에서 다음을 추출:
    rank, girl_group_name, brand_score, activity_score, media_score, communication_score, community_score
    """

    # 페이지의 모든 <table> 태그를 가져옴
    tables = soup.find_all("table")
    if not tables:
        raise ValueError("No <table> found on page. HTML structure may have changed.")
    target_table = None
    # 여러 테이블이 있을 수 있으니 “순위”와 “브랜드평판지수”라는 키워드가 함께 포함된 테이블을 우선 선택.
    for tbl in tables:
        header_text = tbl.get_text(" ", strip=True)
        if "순위" in header_text and "브랜드평판지수" in header_text:
            target_table = tbl
            break
    if target_table is None:
        # fallback: 첫 테이블
        target_table = tables[0]

    # 행
    rows = target_table.find_all("tr")
    results = []

    # 열
    for tr in rows:
        tds = tr.find_all("td")
        if not tds:
            continue

        rank_text = tds[0].get_text(strip=True)
        if not rank_text.isdigit():
            continue

        rank = int(rank_text)

        # 0 순위
        # 1 브랜드(그룹명)
        # 2 Link
        # 3 브랜드평판지수
        # 4 참여지수
        # 5 미디어지수
        # 6 소통지수
        # 7 커뮤니티지수
        if len(tds) < 8:
            # 구조가 예상과 다르면 일단 스킵 (안전)
            continue

        girl_group_name = tds[1].get_text(strip=True)
        brand_score = parse_int(tds[3].get_text(strip=True))
        activity_score = parse_int(tds[4].get_text(strip=True))
        media_score = parse_int(tds[5].get_text(strip=True))
        communication_score = parse_int(tds[6].get_text(strip=True))
        community_score = parse_int(tds[7].get_text(strip=True))

        results.append(
            {
                "rank": rank,
                "girl_group_name": girl_group_name,
                "brand_score": brand_score,
                "activity_score": activity_score,
                "media_score": media_score,
                "communication_score": communication_score,
                "community_score": community_score,
            }
        )

        if len(results) >= top_n:
            break

    if len(results) == 0:
        raise ValueError("결과가 0이면 파싱 로직이 깨졌거나 HTML 구조가 변한 것")

    return results


# DB URL, 스냅샷 월, 파싱된 rows를 받아 DB에 저장하는 함수
def upsert_rows(database_url: str, snapshot_month: date, rows: list[dict]):
    engine = create_engine(database_url, future=True)

    upsert_sql = text(
        """
        INSERT INTO girl_group_rank (
            snapshot_month, rank, girl_group_name,
            brand_score, activity_score, media_score, communication_score, community_score
        )
        VALUES (
            :snapshot_month, :rank, :girl_group_name,
            :brand_score, :activity_score, :media_score, :communication_score, :community_score
        )
        ON CONFLICT (snapshot_month, girl_group_name)
        DO UPDATE SET
            rank = EXCLUDED.rank,
            brand_score = EXCLUDED.brand_score,
            activity_score = EXCLUDED.activity_score,
            media_score = EXCLUDED.media_score,
            communication_score = EXCLUDED.communication_score,
            community_score = EXCLUDED.community_score;
    """
    )

    payload = []
    for r in rows:
        payload.append(
            {
                "snapshot_month": snapshot_month,
                **r,
            }
        )

    with engine.begin() as conn:
        conn.execute(upsert_sql, payload)


# 프로그램 실행 main 함수
def main():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DB 연결 불가")

    html = fetch_html(BRIKOREA_URL)
    soup = BeautifulSoup(html, "lxml")

    title = extract_title(soup)
    snapshot_month = parse_snapshot_month(title)

    rows = extract_top_rows(soup, top_n=50)
    upsert_rows(db_url, snapshot_month, rows)

    print(
        f"[OK] snapshot_month={snapshot_month} rows={len(rows)} saved into girl_group_rank"
    )


if __name__ == "__main__":
    main()
