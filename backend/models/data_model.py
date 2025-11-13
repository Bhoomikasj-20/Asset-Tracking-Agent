from datetime import datetime
from pydantic import BaseModel, Field
import uuid


class Asset(BaseModel):
    
    asset_id: str 
    asset_type: str 
    brand: str 
    model_number: str 
    assigned_to: str 
    purchase_date: str 
    status: str 
    last_updated_at: str


