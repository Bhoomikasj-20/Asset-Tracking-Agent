import json
import ast
from services import assets_service


def get_assets() -> dict:
    """Get all corporate assets from the database."""
    assets = assets_service.get_all_assets()
    return {
        "success": True,
        "count": len(assets) if isinstance(assets, list) else 0,
        "assets": assets if isinstance(assets, list) else []
    }


def create_asset(
    asset_type: str = "",
    brand: str = "",
    model_number: str = "",
    status: str = "Available",
    assigned_to: str = "",
    purchase_date: str = "",
    asset_name: str = "",
    category: str = "General",
    warranty_expiry: str = "",
    location: str = "",
    notes: str = ""
) -> dict:
    """Create a new corporate asset. Required: asset_type, brand, model_number."""
    asset_data = {
        "asset_type": asset_type,
        "brand": brand,
        "model_number": model_number,
        "assigned_to": assigned_to,
        "status": status or "Available",
        "purchase_date": purchase_date,
        "asset_name": asset_name or asset_type,
        "category": category or "General",
        "warranty_expiry": warranty_expiry,
        "location": location,
        "notes": notes
    }
    result = assets_service.create_asset(asset_data)
    if "error" in result:
        return {"success": False, "error": result["error"]}
    
    return {
        "success": True,
        "asset": result,
        "message": "Asset created successfully"
    }


def get_all_assets() -> dict:
    """Get all corporate assets from the database."""
    assets = assets_service.get_all_assets()
    return {
        "success": True,
        "count": len(assets) if isinstance(assets, list) else 0,
        "assets": assets if isinstance(assets, list) else []
    }


def get_asset_by_id(asset_id: str) -> dict:
    """Get a specific asset by its unique ID."""
    asset = assets_service.get_asset_by_id(asset_id)
    if isinstance(asset, dict) and "error" in asset:
        return {"success": False, "error": asset["error"]}
    return {
        "success": True,
        "asset": asset
    }


def update_asset(asset_id: str, **kwargs) -> dict:
    """Update an existing asset. Provide asset_id and the fields to update (e.g. status='In Repair', assigned_to='Ravi')."""
    result = assets_service.update_asset(asset_id, kwargs)
    if "error" in result:
        return {"success": False, "error": result["error"]}
    return {
        "success": True,
        "asset": result,
        "message": f"Asset {asset_id} updated successfully"
    }


def delete_asset(asset_id: str) -> dict:
    """Delete an asset by its unique ID."""
    result = assets_service.delete_asset(asset_id)
    if "error" in result:
        return {"success": False, "error": result["error"]}
    return {
        "success": True,
        "asset_id": asset_id,
        "message": f"Asset {asset_id} deleted successfully"
    }


def assign_asset(asset_id: str, employee: str) -> dict:
    """Assign an asset to a specific employee. Changes status to 'Assigned'."""
    result = assets_service.assign_asset(asset_id, employee)
    if "error" in result:
        return {"success": False, "error": result["error"]}
    return {
        "success": True,
        "asset": result,
        "message": f"Asset {asset_id} assigned to {employee}"
    }


def return_asset(asset_id: str) -> dict:
    """Mark an asset as returned. Changes status to 'Returned'."""
    result = assets_service.return_asset(asset_id)
    if "error" in result:
        return {"success": False, "error": result["error"]}
    return {
        "success": True,
        "asset": result,
        "message": f"Asset {asset_id} marked as returned"
    }


def mark_clearance(asset_id: str) -> dict:
    """Mark an asset as cleared for audit purposes. Changes status to 'Cleared'."""
    result = assets_service.mark_clearance(asset_id)
    if "error" in result:
        return {"success": False, "error": result["error"]}
    return {
        "success": True,
        "asset": result,
        "message": f"Asset {asset_id} cleared successfully"
    }


def search_assets(query: str) -> dict:
    """Search assets by name, type, brand, model, employee, category, or status."""
    assets = assets_service.search_assets(query)
    return {
        "success": True,
        "count": len(assets) if isinstance(assets, list) else 0,
        "assets": assets if isinstance(assets, list) else []
    }


def get_assets_by_status(status: str) -> dict:
    """Get all assets filtered by status. Valid statuses: Available, Assigned, Returned, Under Audit, Pending Clearance, Cleared, Active, In Repair, Disposed."""
    assets = assets_service.get_assets_by_status(status)
    return {
        "success": True,
        "count": len(assets) if isinstance(assets, list) else 0,
        "assets": assets if isinstance(assets, list) else []
    }


def get_assets_by_employee(employee: str) -> dict:
    """Get all assets assigned to a specific employee."""
    assets = assets_service.get_assets_by_employee(employee)
    return {
        "success": True,
        "count": len(assets) if isinstance(assets, list) else 0,
        "assets": assets if isinstance(assets, list) else []
    }


def get_asset_count() -> dict:
    """Get the total number of assets currently tracked."""
    stats = assets_service.get_dashboard_stats()
    return {
        "success": True,
        "count": stats.get("total_assets", 0)
    }


def get_dashboard_stats() -> dict:
    """Get dashboard statistics including total assets, assigned count, returned count, category breakdown, and status distribution."""
    stats = assets_service.get_dashboard_stats()
    return {
        "success": True,
        "stats": stats
    }


def get_audit_logs() -> dict:
    """Get all audit logs showing the history of all asset actions."""
    logs = assets_service.get_audit_logs()
    return {
        "success": True,
        "count": len(logs) if isinstance(logs, list) else 0,
        "logs": logs if isinstance(logs, list) else []
    }
