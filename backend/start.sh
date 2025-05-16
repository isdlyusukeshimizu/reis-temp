#!/bin/bash

# データベースの準備を待機
echo "Waiting for database to be ready..."
python - << 'PYCODE'
import time
import os
import sqlalchemy
from sqlalchemy import create_engine

db_url = os.getenv('DATABASE_URL')
max_retries = 30
retries = 0

while retries < max_retries:
    try:
        engine = create_engine(db_url)
        conn = engine.connect()
        conn.close()
        break
    except sqlalchemy.exc.OperationalError:
        retries += 1
        print(f'Database connection attempt {retries}/{max_retries} failed, retrying in 1 second...')
        time.sleep(1)

if retries == max_retries:
    print('Could not connect to database, exiting...')
    exit(1)
PYCODE

# マイグレーションを実行
# alembic.ini は /app/alembic/alembic.ini に存在するため、-c オプションでパスを指定
echo "Running database migrations..."
alembic -c alembic/alembic.ini upgrade head

# 管理者ユーザーを作成（存在しない場合）
echo "Creating admin user if not exists..."
python - << 'PYCODE'
from app.db.database import SessionLocal
from app.db.models import User
from app.core.security import get_password_hash
import os

db = SessionLocal()
admin_email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
admin_exists = db.query(User).filter(User.email == admin_email).first()

if not admin_exists:
    admin_password = os.getenv('ADMIN_PASSWORD', 'admin')
    admin_user = User(
        email=admin_email,
        password_hash=get_password_hash(admin_password),
        name='Admin User',
        role='admin',
        status='active'
    )
    db.add(admin_user)
    db.commit()
    print(f'Admin user {admin_email} created successfully')
else:
    print(f'Admin user {admin_email} already exists')

db.close()
PYCODE

# アプリケーションを起動
echo "Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
