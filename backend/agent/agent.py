from agent.tools import *
from agent.prompt import *

# This file now only serves as a configuration/tool registry
# The Groq service handles the actual LLM logic

Model = "llama-3.3-70b-versatile"

AGENT_DESCRIPTION = "AssetsTrackingAgent - an intelligent AI assistant that helps corporates and enterprises manage, track, assign, return, and audit corporate assets through natural conversation."

ALL_TOOLS = [
    get_assets,
    create_asset,
    delete_asset,
    get_asset_by_id,
    update_asset,
    assign_asset,
    return_asset,
    mark_clearance,
    search_assets,
    get_assets_by_status,
    get_assets_by_employee,
    get_asset_count,
    get_dashboard_stats,
    get_audit_logs,
    get_asset_summary,
    get_asset_analytics,
    filter_assets,
]
