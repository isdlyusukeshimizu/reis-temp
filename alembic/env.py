# alembic/env.py
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

import os
import sys
from dotenv import load_dotenv

# .envファイルを読み込む
load_dotenv()

# このスクリプトのディレクトリの親ディレクトリをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# モデルのメタデータをインポート
from app.db.database import Base
from app.db.models import *

# Alembic Configオブジェクト
config = context.config

# 環境変数からデータベースURLを取得
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))

# ログ設定
fileConfig(config.config_file_name)

# メタデータターゲット
target_metadata = Base.metadata

def run_migrations_offline():
    """
    SQLマイグレーションスクリプトを生成するオフラインモードで実行します。
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """
    エンジンに接続してマイグレーションを実行するオンラインモードで実行します。
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()