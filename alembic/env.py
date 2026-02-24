# alembic/env.py : Alembic이 models.py를 읽어서 마이그레이션 생성하고 실행할 수 있게 연결
# Alembic이란? Python으로 SQLAlchemy를 사용하고 있을 때 DB의 관리해주는 툴
# 마이그레이션이란? db 테이블 구조 바꿔야할 때 변경 내용을 코드로 기록하고 순서대로 적용하고 필요하면 되돌릴 수 있는 시스템(실무에서 많이 씀)

from __future__ import annotations

import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from dotenv import load_dotenv

# 환경변수에서 DATABASE_URL 읽기
load_dotenv()

# Alembic Config 객체
config = context.config

# alembic.ini의 로깅 설정 적용
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# SQLAlchemy 모델의 Base.metadata를 Alembic에 전달
from db.models import Base  # db/models.py를 import

target_metadata = Base.metadata


# DB URL을 가져오는 함수
def get_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set. Check your .env file.")
    return url


# offline 모드: db에 연결하지 않고 sql을 출력만 함 (Alembic 기본 구조라 굳이 삭제할 필요는 없다고 함)
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# 온라인 모드 : 실제 db를 변경하는 모드 (기본 모드)
def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
