# tests/test_api/test_owners.py
from fastapi.testclient import TestClient
import pytest

def test_create_owner(client, db):
    # オーナーを作成
    owner_data = {
        "name": "Test Owner",
        "address": "東京都千代田区1-1-1",
        "postal_code": "100-0001",
        "phone_number": "03-1234-5678",
        "email": "owner@example.com"
    }
    
    response = client.post("/api/v1/owners/", json=owner_data)
    
    # レスポンスを検証
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == owner_data["name"]
    assert data["address"] == owner_data["address"]
    assert data["postal_code"] == owner_data["postal_code"]
    
    # データベースを検証
    owner_id = data["id"]
    from app.db.models import Owner
    owner = db.query(Owner).filter(Owner.id == owner_id).first()
    assert owner is not None
    assert owner.name == owner_data["name"]

def test_get_owners(client, db):
    # オーナーを作成
    owner_data = {
        "name": "Test Owner",
        "address": "東京都千代田区1-1-1",
        "postal_code": "100-0001",
        "phone_number": "03-1234-5678",
        "email": "owner@example.com"
    }
    
    client.post("/api/v1/owners/", json=owner_data)
    
    # オーナーを取得
    response = client.get("/api/v1/owners/")
    
    # レスポンスを検証
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["name"] == owner_data["name"]

def test_update_owner(client, db):
    # オーナーを作成
    owner_data = {
        "name": "Test Owner",
        "address": "東京都千代田区1-1-1",
        "postal_code": "100-0001",
        "phone_number": "03-1234-5678",
        "email": "owner@example.com"
    }
    
    response = client.post("/api/v1/owners/", json=owner_data)
    owner_id = response.json()["id"]
    
    # オーナーを更新
    update_data = {
        "name": "Updated Owner",
        "phone_number": "03-8765-4321"
    }
    
    response = client.put(f"/api/v1/owners/{owner_id}", json=update_data)
    
    # レスポンスを検証
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["phone_number"] == update_data["phone_number"]
    assert data["address"] == owner_data["address"]  # 変更されていないフィールド
    
    # データベースを検証
    from app.db.models import Owner
    owner = db.query(Owner).filter(Owner.id == owner_id).first()
    assert owner is not None
    assert owner.name == update_data["name"]