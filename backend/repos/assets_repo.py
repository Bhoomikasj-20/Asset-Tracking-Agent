from core.db import memory_db
from models.data_model import Asset

class AssetRepo:
    
    def get_all():
        rows = memory_db.execute("SELECT * FROM assets ORDER BY asset_id ASC", fetchall=True)
        return [dict(r) for r in rows]

    
    def get_by_id(asset_id: str):
        row = memory_db.execute("SELECT * FROM assets WHERE asset_id = ?", (asset_id,), fetchone=True)
        return dict(row) if row else None

    
    def create(asset: Asset):
        memory_db.execute("""
            INSERT INTO assets (asset_id, asset_type, brand, model_number, assigned_to, purchase_date, status, last_updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            asset.asset_id, asset.asset_type, asset.brand, asset.model_number,
            asset.assigned_to, asset.purchase_date, asset.status, asset.last_updated_at
        ))

    
    def update(asset_id: str, asset: Asset):
        memory_db.execute("""
            UPDATE assets
            SET asset_type = ?, brand = ?, model_number = ?, assigned_to = ?, 
                purchase_date = ?, status = ?, last_updated_at = ?
            WHERE asset_id = ?
        """, (
            asset.asset_type, asset.brand, asset.model_number, asset.assigned_to,
            asset.purchase_date, asset.status, asset.last_updated_at, asset_id
        ))

    
    def delete(asset_id: str):
        memory_db.execute("DELETE FROM assets WHERE asset_id = ?", (asset_id,))


