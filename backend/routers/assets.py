from fastapi import APIRouter
from services import assets_service

router = APIRouter()

@router.get("/")
def list_assets():
    return assets_service.get_all_assets()

@router.get("/{asset_id}")
def read_asset(asset_id: str):
    return assets_service.get_asset_by_id(asset_id)

@router.post("/")
def create_new_asset(asset_data: dict):
    return assets_service.create_asset(asset_data)

@router.put("/{asset_id}")
def modify_asset(asset_id: str, asset_data: dict):
    return assets_service.update_asset(asset_id, asset_data)

@router.delete("/{asset_id}")
def remove_asset(asset_id: str):
    return assets_service.delete_asset(asset_id)
