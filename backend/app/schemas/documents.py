# app/schemas/documents.py
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

class DocumentBase(BaseModel):
    file_name: str
    document_type: str

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(BaseModel):
    file_name: Optional[str] = None
    document_type: Optional[str] = None
    status: Optional[str] = None
    processing_status: Optional[str] = None
    error_message: Optional[str] = None

class DocumentInDB(DocumentBase):
    id: int
    file_path: str
    status: str
    upload_date: datetime
    uploaded_by: int
    processed_at: Optional[datetime] = None
    processing_status: str
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class Document(DocumentInDB):
    pass

class ExtractedDataBase(BaseModel):
    document_id: int
    customer_name: str
    prefecture: str
    current_address: str
    inheritance_address: str
    postal_code: Optional[str] = None
    phone_number: Optional[str] = None
    status: str = "pending"

class ExtractedDataCreate(ExtractedDataBase):
    pass

class ExtractedDataUpdate(BaseModel):
    customer_name: Optional[str] = None
    prefecture: Optional[str] = None
    current_address: Optional[str] = None
    inheritance_address: Optional[str] = None
    postal_code: Optional[str] = None
    phone_number: Optional[str] = None
    status: Optional[str] = None

class ExtractedDataInDB(ExtractedDataBase):
    id: int
    extracted_at: datetime
    extracted_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ExtractedData(ExtractedDataInDB):
    pass

class ProcessingResult(BaseModel):
    task_id: str
    pdf_count: int
    owner_count: int
    output_files: Dict[str, str]