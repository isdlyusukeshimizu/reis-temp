# app/utils/helpers.py
import os
import uuid
from pathlib import Path
from typing import Optional

def ensure_dir(directory: str) -> str:
    """
    ディレクトリが存在することを確認し、存在しない場合は作成します。
    """
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return str(path)

def generate_unique_filename(original_filename: str, prefix: Optional[str] = None) -> str:
    """
    一意のファイル名を生成します。
    """
    _, ext = os.path.splitext(original_filename)
    unique_id = str(uuid.uuid4())
    
    if prefix:
        return f"{prefix}_{unique_id}{ext}"
    
    return f"{unique_id}{ext}"

def format_error_message(exception: Exception) -> str:
    """
    例外からエラーメッセージを整形します。
    """
    return f"{type(exception).__name__}: {str(exception)}"

def get_file_size(file_path: str) -> int:
    """
    ファイルサイズをバイト単位で取得します。
    """
    return os.path.getsize(file_path)

def get_file_extension(filename: str) -> str:
    """
    ファイル名から拡張子を取得します。
    """
    return os.path.splitext(filename)[1].lower()

def is_valid_pdf(filename: str) -> bool:
    """
    ファイルがPDFかどうかを確認します。
    """
    return get_file_extension(filename) == '.pdf'