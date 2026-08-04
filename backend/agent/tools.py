import json
import ast
from services import assets_service


def get_assets(sort_by: str = "", sort_order: str = "asc", **kwargs) -> dict:
    """Get all corporate assets from the database."""
    assets = assets_service.get_all_assets()
    assets = assets_service._sort_asset_list(assets, sort_by=sort_by, sort_order=sort_order)
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
    notes: str = "",
    **kwargs
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


def get_all_assets(sort_by: str = "", sort_order: str = "asc", **kwargs) -> dict:
    """Get all corporate assets from the database."""
    assets = assets_service.get_all_assets()
    assets = assets_service._sort_asset_list(assets, sort_by=sort_by, sort_order=sort_order)
    return {
        "success": True,
        "count": len(assets) if isinstance(assets, list) else 0,
        "assets": assets if isinstance(assets, list) else []
    }


def get_asset_by_id(asset_id: str = "", **kwargs) -> dict:
    """Get a specific asset by its unique ID."""
    if not asset_id and "id" in kwargs:
        asset_id = kwargs["id"]
    asset = assets_service.get_asset_by_id(asset_id)
    if isinstance(asset, dict) and "error" in asset:
        return {"success": False, "error": asset["error"]}
    return {
        "success": True,
        "asset": asset
    }


def update_asset(asset_id: str = "", **kwargs) -> dict:
    """Update an existing asset. Provide asset_id and the fields to update (e.g. status='In Repair', assigned_to='Ravi')."""
    if not asset_id and "id" in kwargs:
        asset_id = kwargs.pop("id")
    result = assets_service.update_asset(asset_id, kwargs)
    if "error" in result:
        return {"success": False, "error": result["error"]}
    return {
        "success": True,
        "asset": result,
        "message": f"Asset {asset_id} updated successfully"
    }


def delete_asset(asset_id: str = "", **kwargs) -> dict:
    """Delete an asset by its unique ID."""
    if not asset_id and "id" in kwargs:
        asset_id = kwargs["id"]
    result = assets_service.delete_asset(asset_id)
    if "error" in result:
        return {"success": False, "error": result["error"]}
    return {
        "success": True,
        "asset_id": asset_id,
        "message": f"Asset {asset_id} deleted successfully"
    }


def assign_asset(asset_id: str = "", employee: str = "", **kwargs) -> dict:
    """Assign an asset to a specific employee. Changes status to 'Assigned'."""
    if not asset_id and "id" in kwargs:
        asset_id = kwargs["id"]
    if not employee and "assigned_to" in kwargs:
        employee = kwargs["assigned_to"]
    result = assets_service.assign_asset(asset_id, employee)
    if "error" in result:
        return {"success": False, "error": result["error"]}
    return {
        "success": True,
        "asset": result,
        "message": f"Asset {asset_id} assigned to {employee}"
    }


def return_asset(asset_id: str = "", **kwargs) -> dict:
    """Mark an asset as returned. Changes status to 'Returned'."""
    if not asset_id and "id" in kwargs:
        asset_id = kwargs["id"]
    result = assets_service.return_asset(asset_id)
    if "error" in result:
        return {"success": False, "error": result["error"]}
    return {
        "success": True,
        "asset": result,
        "message": f"Asset {asset_id} marked as returned"
    }


def mark_clearance(asset_id: str = "", **kwargs) -> dict:
    """Mark an asset as cleared for audit purposes. Changes status to 'Cleared'."""
    if not asset_id and "id" in kwargs:
        asset_id = kwargs["id"]
    result = assets_service.mark_clearance(asset_id)
    if "error" in result:
        return {"success": False, "error": result["error"]}
    return {
        "success": True,
        "asset": result,
        "message": f"Asset {asset_id} cleared successfully"
    }


def search_assets(query: str = "", sort_by: str = "", sort_order: str = "asc", **kwargs) -> dict:
    """Search assets by name, type, brand, model, employee, category, or status."""
    assets = assets_service.search_assets(query)
    assets = assets_service._sort_asset_list(assets, sort_by=sort_by, sort_order=sort_order)
    return {
        "success": True,
        "count": len(assets) if isinstance(assets, list) else 0,
        "assets": assets if isinstance(assets, list) else []
    }


def get_assets_by_status(status: str = "", sort_by: str = "", sort_order: str = "asc", **kwargs) -> dict:
    """Get all assets filtered by status. Valid statuses: Available, Assigned, Returned, Under Audit, Pending Clearance, Cleared, Active, In Repair, Disposed."""
    assets = assets_service.get_assets_by_status(status)
    assets = assets_service._sort_asset_list(assets, sort_by=sort_by, sort_order=sort_order)
    return {
        "success": True,
        "count": len(assets) if isinstance(assets, list) else 0,
        "assets": assets if isinstance(assets, list) else []
    }


def get_assets_by_employee(employee: str = "", sort_by: str = "", sort_order: str = "asc", **kwargs) -> dict:
    """Get all assets assigned to a specific employee."""
    assets = assets_service.get_assets_by_employee(employee)
    assets = assets_service._sort_asset_list(assets, sort_by=sort_by, sort_order=sort_order)
    return {
        "success": True,
        "count": len(assets) if isinstance(assets, list) else 0,
        "assets": assets if isinstance(assets, list) else []
    }


def get_asset_count(**kwargs) -> dict:
    """Get the total number of assets currently tracked."""
    stats = assets_service.get_dashboard_stats()
    return {
        "success": True,
        "count": stats.get("total_assets", 0)
    }


def get_dashboard_stats(**kwargs) -> dict:
    """Get dashboard statistics including total assets, assigned count, returned count, category breakdown, and status distribution."""
    stats = assets_service.get_dashboard_stats()
    return {
        "success": True,
        "stats": stats
    }


def get_audit_logs(**kwargs) -> dict:
    """Get all audit logs showing the history of all asset actions."""
    logs = assets_service.get_audit_logs()
    return {
        "success": True,
        "count": len(logs) if isinstance(logs, list) else 0,
        "logs": logs if isinstance(logs, list) else []
    }


def get_asset_summary(**kwargs) -> dict:
    """Get a comprehensive summary of total assets, status breakdown (available, assigned, repair, returned), and category counts directly from the database."""
    summary = assets_service.get_asset_summary()
    return {
        "success": True,
        "summary": summary,
        **summary
    }


def get_asset_analytics(**kwargs) -> dict:
    """Get smart analytics including repair percentage, assignment percentage, category distribution, and most assigned category."""
    analytics = assets_service.get_asset_analytics()
    return {
        "success": True,
        "analytics": analytics,
        **analytics
    }


def filter_assets(
    status: str = "",
    category: str = "",
    brand: str = "",
    assigned_to: str = "",
    unassigned: bool = False,
    recent: bool = False,
    sort_by: str = "",
    sort_order: str = "asc",
    **kwargs
) -> dict:
    """Filter corporate assets by status, category, brand, employee, unassigned status, or recently added, with optional sorting."""
    assets = assets_service.filter_assets(
        status=status,
        category=category,
        brand=brand,
        assigned_to=assigned_to,
        unassigned=unassigned,
        recent=recent,
        sort_by=sort_by,
        sort_order=sort_order
    )
    return {
        "success": True,
        "count": len(assets) if isinstance(assets, list) else 0,
        "assets": assets if isinstance(assets, list) else []
    }
