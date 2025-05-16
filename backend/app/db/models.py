# app/db/models.py
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Date, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False, default="staff")
    status = Column(String(20), nullable=False, default="active")
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # リレーションシップ
    documents = relationship("Document", back_populates="uploader")
    extracted_data = relationship("ExtractedData", back_populates="extractor")
    reported_errors = relationship("ErrorReport", foreign_keys="ErrorReport.reported_by", back_populates="reporter")
    resolved_errors = relationship("ErrorReport", foreign_keys="ErrorReport.resolved_by", back_populates="resolver")
    assigned_customers = relationship("Customer", back_populates="assigned_user")
    customer_activities = relationship("CustomerActivity", back_populates="creator")
    registry_requests = relationship("RegistryRequest", back_populates="requester")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(255), nullable=False)
    document_type = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    upload_date = Column(DateTime, default=func.now(), nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    processed_at = Column(DateTime, nullable=True)
    processing_status = Column(String(20), default="pending")
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # リレーションシップ
    uploader = relationship("User", back_populates="documents")
    extracted_data = relationship("ExtractedData", back_populates="document")
    error_reports = relationship("ErrorReport", back_populates="document")


class ExtractedData(Base):
    __tablename__ = "extracted_data"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    customer_name = Column(String(100), nullable=False)
    postal_code = Column(String(8), nullable=True)
    prefecture = Column(String(20), nullable=False)
    current_address = Column(String(255), nullable=False)
    inheritance_address = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=True)
    status = Column(String(20), nullable=False, default="pending")
    extracted_at = Column(DateTime, default=func.now(), nullable=False)
    extracted_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # リレーションシップ
    document = relationship("Document", back_populates="extracted_data")
    extractor = relationship("User", back_populates="extracted_data")


class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    property_address = Column(String(255), nullable=False, index=True)
    registry_office = Column(String(100), nullable=False, index=True)
    registration_date = Column(Date, nullable=True)
    property_type = Column(String(50), nullable=False)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # リレーションシップ
    ownerships = relationship("Ownership", back_populates="property")
    registry_requests = relationship("RegistryRequest", back_populates="property")


class Owner(Base):
    __tablename__ = "owners"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    address = Column(String(255), nullable=False)
    postal_code = Column(String(8), nullable=True)
    phone_number = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # リレーションシップ
    ownerships = relationship("Ownership", back_populates="owner")


class Ownership(Base):
    __tablename__ = "ownerships"

    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), index=True)
    owner_id = Column(Integer, ForeignKey("owners.id"), index=True)
    transfer_type = Column(String(50), nullable=True)
    transfer_date = Column(Date, nullable=True)
    transfer_reason = Column(String(100), nullable=True)
    ownership_percentage = Column(Integer, default=100)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # リレーションシップ
    property = relationship("Property", back_populates="ownerships")
    owner = relationship("Owner", back_populates="ownerships")


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    phone_number = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    address = Column(String(255), nullable=False)
    postal_code = Column(String(8), nullable=True)
    property_address = Column(String(255), nullable=False)
    property_type = Column(String(50), nullable=True)
    status = Column(String(20), nullable=False, default="new")
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    last_contact_date = Column(Date, nullable=True)
    next_contact_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    source = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # リレーションシップ
    assigned_user = relationship("User", back_populates="assigned_customers")
    activities = relationship("CustomerActivity", back_populates="customer")
    registry_requests = relationship("RegistryRequest", back_populates="customer")


class CustomerActivity(Base):
    __tablename__ = "customer_activities"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), index=True)
    activity_date = Column(Date, nullable=False)
    activity_type = Column(String(20), nullable=False)
    description = Column(Text, nullable=False)
    result = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # リレーションシップ
    customer = relationship("Customer", back_populates="activities")
    creator = relationship("User", back_populates="customer_activities")


class RegistryRequest(Base):
    __tablename__ = "registry_requests"

    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), index=True)
    request_type = Column(String(50), nullable=False)
    request_date = Column(Date, nullable=False)
    received_date = Column(Date, nullable=True)
    status = Column(String(20), nullable=False, default="pending")
    requested_by = Column(Integer, ForeignKey("users.id"))
    cost = Column(Integer, default=331)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # リレーションシップ
    property = relationship("Property", back_populates="registry_requests")
    customer = relationship("Customer", back_populates="registry_requests")
    requester = relationship("User", back_populates="registry_requests")
    invoice_items = relationship("InvoiceItem", back_populates="registry_request")


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(50), unique=True, nullable=False)
    client_name = Column(String(100), nullable=False, index=True)
    amount = Column(Integer, nullable=False)
    issue_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    payment_method = Column(String(50), nullable=True)
    payment_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # リレーションシップ
    items = relationship("InvoiceItem", back_populates="invoice")


class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), index=True)
    registry_request_id = Column(Integer, ForeignKey("registry_requests.id"), nullable=True)
    amount = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # リレーションシップ
    invoice = relationship("Invoice", back_populates="items")
    registry_request = relationship("RegistryRequest", back_populates="invoice_items")


class ErrorReport(Base):
    __tablename__ = "error_reports"

    id = Column(Integer, primary_key=True, index=True)
    error_type = Column(String(50), nullable=False)
    error_message = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="open")
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    reported_by = Column(Integer, ForeignKey("users.id"))
    reported_at = Column(DateTime, default=func.now(), nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # リレーションシップ
    document = relationship("Document", back_populates="error_reports")
    reporter = relationship("User", foreign_keys=[reported_by], back_populates="reported_errors")
    resolver = relationship("User", foreign_keys=[resolved_by], back_populates="resolved_errors")


class PostalCode(Base):
    __tablename__ = "postal_codes"

    postal_code = Column(String(8), primary_key=True)
    prefecture = Column(String(10), nullable=False)
    city = Column(String(50), nullable=False)
    town = Column(String(100), nullable=False)
    prefecture_kana = Column(String(20), nullable=True)
    city_kana = Column(String(100), nullable=True)
    town_kana = Column(String(100), nullable=True)


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(36), unique=True, nullable=False)
    task_type = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False, default="processing")
    result = Column(Text, nullable=True)
    start_time = Column(DateTime, default=func.now(), nullable=False)
    end_time = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)