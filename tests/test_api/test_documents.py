# tests/test_api/test_documents.py
from fastapi.testclient import TestClient
import pytest
import os
from unittest.mock import patch

def test_upload_document(client, db):
    # モックファイルを作成
    test_file_path = "test_file.pdf"
    with open(test_file_path, "wb") as f:
        f.write(b"test content")
    
    try:
        # ファイルをアップロード
        with open(test_file_path, "rb") as f:
            response = client.post(
                "/api/v1/documents/upload?document_type=registry_ledger",
                files={"file": ("test_file.pdf", f, "application/pdf")}
            )
        
        # レスポンスを検証
        assert response.status_code == 200
        data = response.json()
        assert data["file_name"] == "test_file.pdf"
        assert data["document_type"] == "registry_ledger"
        assert data["status"] == "pending"
        assert data["processing_status"] == "pending"
        
        # データベースを検証
        document_id = data["id"]
        from app.db.models import Document
        document = db.query(Document).filter(Document.id == document_id).first()
        assert document is not None
        assert document.file_name == "test_file.pdf"
        
    finally:
        # テストファイルを削除
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

def test_get_documents(client, db):
    # ドキュメントを取得
    response = client.get("/api/v1/documents/")
    
    # レスポンスを検証
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

@patch("app.api.routes.documents.process_document_task")
def test_process_document(mock_process, client, db):
    # モックファイルを作成
    test_file_path = "test_file.pdf"
    with open(test_file_path, "wb") as f:
        f.write(b"test content")
    
    try:
        # ファイルをアップロード
        with open(test_file_path, "rb") as f:
            response = client.post(
                "/api/v1/documents/upload?document_type=registry_ledger",
                files={"file": ("test_file.pdf", f, "application/pdf")}
            )
        
        document_id = response.json()["id"]
        
        # ドキュメントを処理
        response = client.post(f"/api/v1/documents/{document_id}/process")
        
        # レスポンスを検証
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "queued"
        assert "task_id" in data
        
        # モックが呼び出されたことを検証
        mock_process.assert_called_once()
        
    finally:
        # テストファイルを削除
        if os.path.exists(test_file_path):
            os.remove(test_file_path)