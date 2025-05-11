from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.db.database import get_db
from app.db import models
from app.core.security import get_current_active_user
from app.services.extract_info import get_cleaned_addresses, extract_registry_office
from app.services.auto_mode import run_auto_mode
from app.utils.helpers import ensure_dir, is_valid_pdf
import os

router = APIRouter()

@router.post("/extract-addresses", response_model=List[str])
async def extract_addresses(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    PDFファイルから住所リストを抽出します。
    """
    if not is_valid_pdf(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PDFファイルのみアップロード可能です"
        )
    
    # 一時ファイルとして保存
    output_dir = ensure_dir(os.getenv("OUTPUT_DIR", "./output"))
    temp_file_path = os.path.join(output_dir, file.filename)
    
    with open(temp_file_path, "wb") as buffer:
        buffer.write(await file.read())
    
    try:
        # 住所リストを抽出
        addresses = get_cleaned_addresses(temp_file_path)
        return addresses
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"住所の抽出に失敗しました: {str(e)}"
        )
    finally:
        # 一時ファイルを削除
        os.remove(temp_file_path)

@router.post("/download-registry-pdfs", response_model=Dict[str, Any])
async def download_registry_pdfs(
    background_tasks: BackgroundTasks,  # BackgroundTasksを先に配置
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    PDFファイルから住所を抽出し、登記情報PDFをダウンロードします。
    """
    if not is_valid_pdf(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PDFファイルのみアップロード可能です"
        )
    
    # ファイルを保存
    output_dir = ensure_dir(os.getenv("OUTPUT_DIR", "./output"))
    file_path = os.path.join(output_dir, file.filename)
    
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    
    # ドキュメントレコードを作成
    db_document = models.Document(
        file_name=file.filename,
        file_path=file_path,
        document_type="registry_ledger",
        uploaded_by=current_user.id
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    # バックグラウンドタスクでPDFダウンロードを実行
    background_tasks.add_task(
        download_registry_pdfs_task,
        file_path,
        db_document.id,
        db
    )
    
    return {
        "message": "登記情報PDFのダウンロードを開始しました",
        "document_id": db_document.id,
        "status": "processing"
    }

def download_registry_pdfs_task(file_path: str, document_id: int, db: Session):
    """
    バックグラウンドタスクとして登記情報PDFをダウンロードします。
    """
    document = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not document:
        return
    
    try:
        # 登記情報PDFをダウンロード
        pdf_paths = run_auto_mode(file_path)
        
        # ドキュメントステータスを更新
        document.processing_status = "completed"
        document.status = "processed"
        db.commit()
        
        # 各PDFに対応するプロパティレコードを作成
        for pdf_path in pdf_paths:
            # PDFからテキストを抽出して登記所名を取得
            with open(pdf_path, 'rb') as f:
                registry_office = extract_registry_office(pdf_path)
            
            # プロパティレコードを作成
            property_address = os.path.basename(pdf_path).replace('_', ' ').replace('-', '/').replace('.pdf', '')
            db_property = models.Property(
                property_address=property_address,
                registry_office=registry_office,
                property_type="land"  # デフォルト値
            )
            db.add(db_property)
            db.commit()
    
    except Exception as e:
        # エラー時の処理
        document.processing_status = "failed"
        document.error_message = str(e)
        db.commit()