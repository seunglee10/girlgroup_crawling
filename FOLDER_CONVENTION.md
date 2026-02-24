# 폴더 구조 컨벤션

## 목적

- 역할별 디렉터리 분리
- 의존성 방향 고정(상위 오케스트레이션 -> 하위 구현)
- 모델/크롤러/실행 로직의 책임 분리

## 표준 구조

```text
idol-crawler/
├─ crawlers/           # 외부 수집 로직 (HTML/API)
├─ db/                 # DB 연결/모델
│  ├─ model/           # 도메인별 SQLAlchemy 모델
│  │  ├─ base.py
│  │  ├─ girl_group.py
│  │  └─ track.py
│  ├─ models.py        # 호환용 re-export 진입점
│  └─ session.py
├─ jobs/               # 수집 + 저장 오케스트레이션
├─ alembic/            # 마이그레이션
├─ scripts/            # 일회성/운영 보조 스크립트
└─ logs/               # 실행 로그 (git 제외)
```

## 의존성 규칙

- `crawlers/`는 DB 세션/모델을 직접 다루지 않는다.
- `jobs/`만 `crawlers/`와 `db/`를 조합한다.
- `db/model/` 파일끼리는 필요한 최소 참조만 허용한다.
- 외부 모듈에서는 기본적으로 `db.models`를 import 진입점으로 사용한다.

# 환경변수

- `.env` — 로컬 전용, git 제외
- `.env.sample` — 팀 공유용 템플릿 (실제 값 없이 키만)

## 네이밍 규칙

- crawler: `crawlers/{source_name}.py`
- job: `jobs/job_{source}_{purpose}.py`
- model 파일: `db/model/{domain}.py`
- 마이그레이션 메시지: 변경 의도가 드러나게 작성

## Alembic 마이그레이션

모델 변경 시 반드시 마이그레이션 생성 후 적용.

```bash
alembic revision --autogenerate -m "변경 내용"
alembic upgrade head
```
