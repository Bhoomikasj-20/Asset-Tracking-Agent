from datetime import datetime
from models.data_model import Asset
from repos.assets_repo import AssetRepo


def create_asset(asset_data: dict):
    asset_data["asset_id"] = asset_data.get("asset_id", str(uuid.uuid4()))
    asset_data["last_updated_at"] = datetime.now().isoformat()
    existing = AssetRepo.get_by_id(asset_data["asset_id"])
    if existing:
        return {"error": f"Asset with name '{asset_data['asset_id']}' already exists."}
    asset = Asset(**asset_data)
    AssetRepo.create(asset)
    return {"message": "Asset created successfully", "asset_id": asset.asset_id}


def get_all_assets():
    return AssetRepo.get_all()

def get_asset_by_id(asset_id: str):
    asset = AssetRepo.get_by_id(asset_id)
    if not asset:
        return {"error": f"No asset found with ID '{asset_id}'"}
    return asset

def update_asset(asset_id: str, asset_data: dict):
    existing = AssetRepo.get_by_id(asset_id)
    if not existing:
        return {"error": f"No asset found with ID '{asset_id}'"}

    # Inject the asset_id and update timestamp
    asset_data["asset_id"] = asset_id
    asset_data["last_updated_at"] = datetime.now().isoformat()

    # Now it will pass Pydantic validation
    updated_asset = Asset(**asset_data)
    AssetRepo.update(asset_id, updated_asset)

    return {"message": f"Asset '{asset_id}' updated successfully"}


def delete_asset(asset_id: str):
    """
    Delete an asset by its ID.
    """
    existing = AssetRepo.get_by_id(asset_id)
    if not existing:
        return {"error": f"No asset found with ID '{asset_id}'"}

    AssetRepo.delete(asset_id)

    return {"message": f" Asset '{asset_id}' deleted successfully"}


def get_last_updated_asset():
    assets = AssetRepo.get_all()
    if not assets:
        return {"message": "No assets found"}

    # Find asset with maximum last_updated_at
    last_asset = max(assets, key=lambda x: x["last_updated_at"])

    return {"last_updated_asset": last_asset}

