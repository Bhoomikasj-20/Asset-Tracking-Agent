import json
import ast
from services import assets_service

def get_assets() ->  dict:
    return assets_service.get_all_assets()

def create_asset(asset_data: dict) -> dict:
    return assets_service.create_asset(asset_data)

def get_all_assets() -> dict:
    return assets_service.get_all_assets()

def get_asset_by_id(asset_id: str) -> dict:
    return assets_service.get_asset_by_id(asset_id)

def update_asset(asset_id: str, asset_data: dict) -> dict:
    return assets_service.update_asset(asset_id, asset_data)

def delete_asset(asset_data: dict) -> dict:
    return assets_service.delete_asset(asset_data)



















