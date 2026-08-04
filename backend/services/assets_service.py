import uuid
from datetime import datetime
from models.data_model import Asset
from repos.assets_repo import AssetRepo, AuditLogRepo


def create_asset(asset_data: dict):
    asset_data["asset_id"] = asset_data.get("asset_id", str(uuid.uuid4()))
    asset_data["last_updated_at"] = datetime.now().isoformat()
    # Set defaults for new fields
    asset_data.setdefault("asset_name", asset_data.get("asset_type", ""))
    asset_data.setdefault("category", "General")
    asset_data.setdefault("warranty_expiry", "")
    asset_data.setdefault("location", "")
    asset_data.setdefault("notes", "")

    existing = AssetRepo.get_by_id(asset_data["asset_id"])
    if existing:
        return {"error": f"Asset with ID '{asset_data['asset_id']}' already exists."}
    asset = Asset(**asset_data)
    AssetRepo.create(asset)

    # Log the action
    AuditLogRepo.create({
        "asset_id": asset.asset_id,
        "action": "Created",
        "details": f"Asset '{asset.asset_name or asset.asset_type}' created and set to '{asset.status}'"
    })

    return {
        "success": True,
        "asset_id": asset.asset_id,
        "asset_type": asset.asset_type,
        "brand": asset.brand,
        "model_number": asset.model_number,
        "status": asset.status,
        "assigned_to": asset.assigned_to,
        "message": "Asset created successfully"
    }


def get_all_assets():
    return AssetRepo.get_all()


def get_asset_by_id(asset_id: str):
    asset = AssetRepo.get_by_id(asset_id)
    if not asset:
        return {"error": f"No asset found with ID '{asset_id}'"}
    return asset


def get_assets_by_status(status: str):
    return AssetRepo.get_by_status(status)


def get_assets_by_employee(employee: str):
    return AssetRepo.get_by_employee(employee)


def get_assets_by_category(category: str):
    return AssetRepo.get_by_category(category)


def search_assets(query: str):
    return AssetRepo.search(query)


def update_asset(asset_id: str, asset_data: dict):
    existing = AssetRepo.get_by_id(asset_id)
    if not existing:
        return {"error": f"No asset found with ID '{asset_id}'"}

    # Merge existing data with updates
    for key in existing:
        if key not in asset_data:
            asset_data[key] = existing[key]

    asset_data["asset_id"] = asset_id
    asset_data["last_updated_at"] = datetime.now().isoformat()

    updated_asset = Asset(**asset_data)
    AssetRepo.update(asset_id, updated_asset)

    # Log the action
    AuditLogRepo.create({
        "asset_id": asset_id,
        "action": "Updated",
        "details": f"Asset updated. Status: '{updated_asset.status}'"
    })

    return {
        "success": True,
        "asset_id": updated_asset.asset_id,
        "asset_type": updated_asset.asset_type,
        "brand": updated_asset.brand,
        "model_number": updated_asset.model_number,
        "status": updated_asset.status,
        "assigned_to": updated_asset.assigned_to,
        "message": f"Asset '{asset_id}' updated successfully"
    }


def assign_asset(asset_id: str, employee: str):
    existing = AssetRepo.get_by_id(asset_id)
    if not existing:
        return {"error": f"No asset found with ID '{asset_id}'"}

    existing["assigned_to"] = employee
    existing["status"] = "Assigned"
    existing["last_updated_at"] = datetime.now().isoformat()

    updated_asset = Asset(**existing)
    AssetRepo.update(asset_id, updated_asset)

    AuditLogRepo.create({
        "asset_id": asset_id,
        "action": "Assigned",
        "details": f"Asset assigned to '{employee}'"
    })

    return {
        "success": True,
        "asset_id": updated_asset.asset_id,
        "asset_type": updated_asset.asset_type,
        "brand": updated_asset.brand,
        "model_number": updated_asset.model_number,
        "status": updated_asset.status,
        "assigned_to": updated_asset.assigned_to,
        "message": f"Asset '{asset_id}' assigned to '{employee}'"
    }


def return_asset(asset_id: str):
    existing = AssetRepo.get_by_id(asset_id)
    if not existing:
        return {"error": f"No asset found with ID '{asset_id}'"}

    existing["status"] = "Returned"
    existing["last_updated_at"] = datetime.now().isoformat()

    updated_asset = Asset(**existing)
    AssetRepo.update(asset_id, updated_asset)

    AuditLogRepo.create({
        "asset_id": asset_id,
        "action": "Returned",
        "details": f"Asset returned by '{existing.get('assigned_to', 'Unknown')}'"
    })

    return {
        "success": True,
        "asset_id": updated_asset.asset_id,
        "asset_type": updated_asset.asset_type,
        "brand": updated_asset.brand,
        "model_number": updated_asset.model_number,
        "status": updated_asset.status,
        "assigned_to": updated_asset.assigned_to,
        "message": f"Asset '{asset_id}' marked as returned"
    }


def mark_clearance(asset_id: str):
    existing = AssetRepo.get_by_id(asset_id)
    if not existing:
        return {"error": f"No asset found with ID '{asset_id}'"}

    existing["status"] = "Cleared"
    existing["last_updated_at"] = datetime.now().isoformat()

    updated_asset = Asset(**existing)
    AssetRepo.update(asset_id, updated_asset)

    AuditLogRepo.create({
        "asset_id": asset_id,
        "action": "Cleared",
        "details": f"Asset clearance completed"
    })

    return {
        "success": True,
        "asset_id": updated_asset.asset_id,
        "asset_type": updated_asset.asset_type,
        "brand": updated_asset.brand,
        "model_number": updated_asset.model_number,
        "status": updated_asset.status,
        "assigned_to": updated_asset.assigned_to,
        "message": f"Asset '{asset_id}' cleared successfully"
    }


def delete_asset(asset_id: str):
    """Delete an asset by its ID."""
    existing = AssetRepo.get_by_id(asset_id)
    if not existing:
        return {"error": f"No asset found with ID '{asset_id}'"}

    AssetRepo.delete(asset_id)

    AuditLogRepo.create({
        "asset_id": asset_id,
        "action": "Deleted",
        "details": f"Asset '{existing.get('asset_type', '')}' deleted"
    })

    return {
        "success": True,
        "asset_id": asset_id,
        "message": f"Asset '{asset_id}' deleted successfully"
    }


def get_dashboard_stats():
    return AssetRepo.get_stats()


def get_audit_logs(asset_id: str = None):
    if asset_id:
        return AuditLogRepo.get_by_asset(asset_id)
    return AuditLogRepo.get_all()


def get_last_updated_asset():
    assets = AssetRepo.get_all()
    if not assets:
        return {"message": "No assets found"}
    last_asset = max(assets, key=lambda x: x["last_updated_at"])
    return {"last_updated_asset": last_asset}


def get_asset_summary():
    return AssetRepo.get_summary()


def get_asset_analytics():
    return AssetRepo.get_analytics()


def _sort_asset_list(assets: list, sort_by: str = "", sort_order: str = "asc") -> list:
    if not sort_by or not assets:
        return assets
    key_map = {
        "asset name": "asset_name",
        "asset_name": "asset_name",
        "name": "asset_name",
        "category": "category",
        "status": "status",
        "asset id": "asset_id",
        "asset_id": "asset_id",
        "id": "asset_id"
    }
    field = key_map.get(sort_by.lower().strip(), "")
    if not field:
        return assets
    
    reverse = sort_order.lower().strip() in ["desc", "descending"]
    return sorted(assets, key=lambda x: str(x.get(field) or "").lower(), reverse=reverse)


def filter_assets(
    status: str = "",
    category: str = "",
    brand: str = "",
    assigned_to: str = "",
    unassigned: bool = False,
    recent: bool = False,
    sort_by: str = "",
    sort_order: str = "asc"
):
    assets = AssetRepo.get_all()
    filtered = []
    for a in assets:
        if status and (a.get("status") or "").lower() != status.lower():
            continue
        if category and category.lower() not in (a.get("category") or "").lower():
            continue
        if brand and brand.lower() not in (a.get("brand") or "").lower():
            continue
        if unassigned and (a.get("assigned_to") or "").strip():
            continue
        if assigned_to and assigned_to.lower() not in (a.get("assigned_to") or "").lower():
            continue
        filtered.append(a)

    if recent:
        filtered = sorted(filtered, key=lambda x: str(x.get("last_updated_at") or ""), reverse=True)[:5]
    else:
        filtered = _sort_asset_list(filtered, sort_by=sort_by, sort_order=sort_order)

    return filtered

