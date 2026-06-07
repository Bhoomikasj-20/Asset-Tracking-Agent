from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
import uuid


class Asset(BaseModel):
    asset_id: str
    asset_name: str = ""
    asset_type: str
    category: str = "General"
    brand: str
    model_number: str
    assigned_to: str = ""
    purchase_date: str = ""
    warranty_expiry: str = ""
    location: str = ""
    notes: str = ""
    status: str
    last_updated_at: str


class AuditLog(BaseModel):
    log_id: str = ""
    asset_id: str
    action: str
    performed_by: str = "System"
    details: str = ""
    timestamp: str = ""


class DashboardStats(BaseModel):
    total_assets: int = 0
    assigned_assets: int = 0
    available_assets: int = 0
    returned_assets: int = 0
    under_audit: int = 0
    pending_clearance: int = 0
    cleared_assets: int = 0
    categories: dict = {}
    recent_assets: list = []
    status_distribution: dict = {}
