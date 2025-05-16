# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base, get_db
from app.main import app
from app.core.security import get_current_active_user
from app.db import models

# テスト用のデータベースURL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# テスト用のエンジンとセッション
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# テスト用のユーザー
test_user = models.User(
    id=1,
    email="test@example.com",
    password_hash="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
    name="Test User",
    role="admin",
    status="active"
)

@pytest.fixture(scope="function")
def db():
    # テスト用のデータベースを作成
    Base.metadata.create_all(bind=engine)
    
    # テストセッションを提供
    db = TestingSessionLocal()
    
    # テスト用のユーザーを追加
    db.add(test_user)
    db.commit()
    
    try:
        yield db
    finally:
        db.close()
        # テスト後にデータベースをクリア
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    # テスト用のクライアントを作成
    
    # 依存関係をオーバーライド
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    def override_get_current_active_user():
        return test_user
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user
    
    with TestClient(app) as client:
        yield client
    
    # オーバーライドをリセット
    app.dependency_overrides = {}