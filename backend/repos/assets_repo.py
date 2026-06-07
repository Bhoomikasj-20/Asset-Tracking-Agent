from core.db import memory_db
from models.data_model import Asset
import uuid
from datetime import datetime


class AssetRepo:

    def get_all():
        rows = memory_db.execute("SELECT * FROM assets ORDER BY last_updated_at DESC", fetchall=True)
        return [dict(r) for r in rows]

    def get_by_id(asset_id: str):
        row = memory_db.execute("SELECT * FROM assets WHERE asset_id = ?", (asset_id,), fetchone=True)
        return dict(row) if row else None

    def get_by_status(status: str):
        rows = memory_db.execute("SELECT * FROM assets WHERE LOWER(status) = LOWER(?)", (status,), fetchall=True)
        return [dict(r) for r in rows]

    def get_by_employee(employee: str):
        rows = memory_db.execute(
            "SELECT * FROM assets WHERE LOWER(assigned_to) LIKE LOWER(?)",
            (f"%{employee}%",), fetchall=True
        )
        return [dict(r) for r in rows]

    def get_by_category(category: str):
        rows = memory_db.execute(
            "SELECT * FROM assets WHERE LOWER(category) LIKE LOWER(?)",
            (f"%{category}%",), fetchall=True
        )
        return [dict(r) for r in rows]

    def search(query: str):
        search_term = f"%{query}%"
        rows = memory_db.execute("""
            SELECT * FROM assets WHERE 
            LOWER(asset_name) LIKE LOWER(?) OR
            LOWER(asset_type) LIKE LOWER(?) OR
            LOWER(brand) LIKE LOWER(?) OR
            LOWER(model_number) LIKE LOWER(?) OR
            LOWER(assigned_to) LIKE LOWER(?) OR
            LOWER(category) LIKE LOWER(?) OR
            LOWER(status) LIKE LOWER(?)
            ORDER BY last_updated_at DESC
        """, (search_term, search_term, search_term, search_term, search_term, search_term, search_term), fetchall=True)
        return [dict(r) for r in rows]

    def create(asset: Asset):
        memory_db.execute("""
            INSERT INTO assets (asset_id, asset_name, asset_type, category, brand, model_number, 
                assigned_to, purchase_date, warranty_expiry, location, notes, status, last_updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            asset.asset_id, asset.asset_name, asset.asset_type, asset.category,
            asset.brand, asset.model_number, asset.assigned_to, asset.purchase_date,
            asset.warranty_expiry, asset.location, asset.notes,
            asset.status, asset.last_updated_at
        ))

    def update(asset_id: str, asset: Asset):
        memory_db.execute("""
            UPDATE assets
            SET asset_name = ?, asset_type = ?, category = ?, brand = ?, model_number = ?, 
                assigned_to = ?, purchase_date = ?, warranty_expiry = ?, location = ?, 
                notes = ?, status = ?, last_updated_at = ?
            WHERE asset_id = ?
        """, (
            asset.asset_name, asset.asset_type, asset.category, asset.brand,
            asset.model_number, asset.assigned_to, asset.purchase_date,
            asset.warranty_expiry, asset.location, asset.notes,
            asset.status, asset.last_updated_at, asset_id
        ))

    def delete(asset_id: str):
        memory_db.execute("DELETE FROM assets WHERE asset_id = ?", (asset_id,))

    def get_stats():
        all_assets = AssetRepo.get_all()
        stats = {
            "total_assets": len(all_assets),
            "assigned_assets": 0,
            "available_assets": 0,
            "returned_assets": 0,
            "under_audit": 0,
            "pending_clearance": 0,
            "cleared_assets": 0,
            "categories": {},
            "recent_assets": all_assets[:5],
            "status_distribution": {}
        }
        for asset in all_assets:
            status = (asset.get("status") or "").lower()
            category = asset.get("category") or "General"

            # Count by status
            if status in ["assigned", "active"]:
                stats["assigned_assets"] += 1
            elif status == "available":
                stats["available_assets"] += 1
            elif status == "returned":
                stats["returned_assets"] += 1
            elif status in ["under audit", "in repair"]:
                stats["under_audit"] += 1
            elif status == "pending clearance":
                stats["pending_clearance"] += 1
            elif status in ["cleared", "disposed"]:
                stats["cleared_assets"] += 1

            # Count by category
            stats["categories"][category] = stats["categories"].get(category, 0) + 1

            # Status distribution
            display_status = asset.get("status") or "Unknown"
            stats["status_distribution"][display_status] = stats["status_distribution"].get(display_status, 0) + 1

        return stats


class AuditLogRepo:

    def get_all():
        rows = memory_db.execute("SELECT * FROM audit_logs ORDER BY timestamp DESC", fetchall=True)
        return [dict(r) for r in rows]

    def get_by_asset(asset_id: str):
        rows = memory_db.execute(
            "SELECT * FROM audit_logs WHERE asset_id = ? ORDER BY timestamp DESC",
            (asset_id,), fetchall=True
        )
        return [dict(r) for r in rows]

    def create(log_data: dict):
        log_id = log_data.get("log_id", str(uuid.uuid4()))
        timestamp = log_data.get("timestamp", datetime.now().isoformat())
        memory_db.execute("""
            INSERT INTO audit_logs (log_id, asset_id, action, performed_by, details, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            log_id,
            log_data.get("asset_id", ""),
            log_data.get("action", ""),
            log_data.get("performed_by", "System"),
            log_data.get("details", ""),
            timestamp
        ))
        return {"log_id": log_id, "message": "Audit log created"}
