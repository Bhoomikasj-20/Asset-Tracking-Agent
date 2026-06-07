from fastapi import APIRouter, Query
from services import assets_service
from typing import Optional

router = APIRouter()


@router.get("/")
def list_assets():
    return assets_service.get_all_assets()


@router.get("/stats")
def get_stats():
    return assets_service.get_dashboard_stats()


@router.get("/search")
def search_assets(q: str = Query("", description="Search query")):
    if not q.strip():
        return assets_service.get_all_assets()
    return assets_service.search_assets(q)


@router.get("/status/{status}")
def get_by_status(status: str):
    return assets_service.get_assets_by_status(status)


@router.get("/employee/{employee}")
def get_by_employee(employee: str):
    return assets_service.get_assets_by_employee(employee)


@router.get("/category/{category}")
def get_by_category(category: str):
    return assets_service.get_assets_by_category(category)


@router.get("/audit-logs")
def get_audit_logs(asset_id: Optional[str] = None):
    return assets_service.get_audit_logs(asset_id)


@router.get("/{asset_id}")
def read_asset(asset_id: str):
    return assets_service.get_asset_by_id(asset_id)


@router.post("/")
def create_new_asset(asset_data: dict):
    return assets_service.create_asset(asset_data)


@router.put("/{asset_id}")
def modify_asset(asset_id: str, asset_data: dict):
    return assets_service.update_asset(asset_id, asset_data)


@router.put("/{asset_id}/assign")
def assign_asset(asset_id: str, data: dict):
    employee = data.get("employee", data.get("assigned_to", ""))
    return assets_service.assign_asset(asset_id, employee)


@router.put("/{asset_id}/return")
def return_asset(asset_id: str):
    return assets_service.return_asset(asset_id)


@router.put("/{asset_id}/clearance")
def mark_clearance(asset_id: str):
    return assets_service.mark_clearance(asset_id)


@router.delete("/{asset_id}")
def remove_asset(asset_id: str):
    return assets_service.delete_asset(asset_id)
