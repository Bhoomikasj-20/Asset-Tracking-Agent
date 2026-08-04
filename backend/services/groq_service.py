import os
import json
import logging
import time
from groq import Groq
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
from agent.tools import (
    get_assets, create_asset, get_asset_by_id, update_asset, 
    delete_asset, assign_asset, return_asset, mark_clearance, 
    search_assets, get_assets_by_status, get_assets_by_employee, 
    get_all_assets, get_asset_count, get_dashboard_stats, get_audit_logs,
    get_asset_summary, get_asset_analytics, filter_assets
)
from agent.prompt import ROOT_AGENT_PROMPT

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Model configuration
MODEL_NAME = "llama-3.3-70b-versatile"


class GroqService:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", "")
        if not self.api_key:
            logger.error("GROQ_API_KEY is missing in environment variables")
            self.client = None
        else:
            self.client = Groq(api_key=self.api_key)
        
        self.tools_list = [
            get_assets, create_asset, get_asset_by_id, update_asset, 
            delete_asset, assign_asset, return_asset, mark_clearance, 
            search_assets, get_assets_by_status, get_assets_by_employee, 
            get_asset_count, get_dashboard_stats, get_audit_logs,
            get_asset_summary, get_asset_analytics, filter_assets
        ]
        
        self.tool_map = {tool.__name__: tool for tool in self.tools_list}
        self.tools = self._prepare_tools()

    def _prepare_tools(self):
        """Builds OpenAI/Groq-compatible function definitions for all agent tools."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_assets",
                    "description": "Get all corporate assets from the database.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_asset",
                    "description": "Create a new corporate asset. Required parameters: asset_type, brand, model_number. All other parameters are optional.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "asset_type": {"type": "string", "description": "The type of the asset (e.g. Laptop, Mobile, Monitor)."},
                            "brand": {"type": "string", "description": "The brand of the asset (e.g. Apple, Dell, Lenovo)."},
                            "model_number": {"type": "string", "description": "The model number of the asset (e.g. MacBook Pro 16)."},
                            "status": {"type": "string", "description": "Optional. The status of the asset (e.g. Available, Assigned). Defaults to 'Available'."},
                            "assigned_to": {"type": "string", "description": "Optional. The name of the employee to assign this asset to."},
                            "purchase_date": {"type": "string", "description": "Optional. The purchase date in YYYY-MM-DD format."},
                            "asset_name": {"type": "string", "description": "Optional. A custom name for the asset. Defaults to asset_type."},
                            "category": {"type": "string", "description": "Optional. The category of the asset (e.g. Laptop, Desktop, Accessory)."},
                            "warranty_expiry": {"type": "string", "description": "Optional. The warranty expiry date in YYYY-MM-DD format."},
                            "location": {"type": "string", "description": "Optional. The location of the asset."},
                            "notes": {"type": "string", "description": "Optional. Additional notes."}
                        },
                        "required": ["asset_type", "brand", "model_number"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_asset_by_id",
                    "description": "Get a specific asset by its unique ID.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "asset_id": {"type": "string", "description": "The unique UUID of the asset."}
                        },
                        "required": ["asset_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_asset",
                    "description": "Update an existing asset. Provide asset_id and any optional fields to update (e.g. status='In Repair', assigned_to='Ravi').",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "asset_id": {"type": "string", "description": "The unique UUID of the asset to update."},
                            "status": {"type": "string", "description": "Optional new status."},
                            "assigned_to": {"type": "string", "description": "Optional new employee assignment."},
                            "location": {"type": "string", "description": "Optional new location."},
                            "notes": {"type": "string", "description": "Optional new notes."},
                            "category": {"type": "string", "description": "Optional new category."},
                            "purchase_date": {"type": "string", "description": "Optional new purchase date."},
                            "warranty_expiry": {"type": "string", "description": "Optional new warranty expiry date."},
                            "asset_name": {"type": "string", "description": "Optional new asset name."}
                        },
                        "required": ["asset_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_asset",
                    "description": "Delete an asset by its unique ID. MUST ask user for confirmation before calling this tool.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "asset_id": {"type": "string", "description": "The unique UUID of the asset to delete."}
                        },
                        "required": ["asset_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "assign_asset",
                    "description": "Assign an asset to a specific employee. Changes status to 'Assigned'.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "asset_id": {"type": "string", "description": "The unique UUID of the asset."},
                            "employee": {"type": "string", "description": "The name of the employee to assign the asset to."}
                        },
                        "required": ["asset_id", "employee"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "return_asset",
                    "description": "Mark an asset as returned. Changes status to 'Returned'.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "asset_id": {"type": "string", "description": "The unique UUID of the asset."}
                        },
                        "required": ["asset_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "mark_clearance",
                    "description": "Mark an asset as cleared for audit purposes. Changes status to 'Cleared'.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "asset_id": {"type": "string", "description": "The unique UUID of the asset."}
                        },
                        "required": ["asset_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_assets",
                    "description": "Search assets by name, type, brand, model, employee, category, or status.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "The keyword query to search for."}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_assets_by_status",
                    "description": "Get all assets filtered by status. Valid statuses: Available, Assigned, Returned, Under Audit, Pending Clearance, Cleared, Active, In Repair, Disposed.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "description": "The status string to filter by."}
                        },
                        "required": ["status"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_assets_by_employee",
                    "description": "Get all assets assigned to a specific employee.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "employee": {"type": "string", "description": "The employee name to filter by."}
                        },
                        "required": ["employee"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_asset_count",
                    "description": "Get the total number of assets currently tracked.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_dashboard_stats",
                    "description": "Get dashboard statistics including total assets, assigned count, returned count, category breakdown, and status distribution.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_audit_logs",
                    "description": "Get all audit logs showing the history of all asset actions.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_asset_summary",
                    "description": "Get a comprehensive summary of total assets, status breakdown (available, assigned, repair, returned), and category counts directly from the database.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_asset_analytics",
                    "description": "Get smart analytics including repair percentage, assignment percentage, category distribution, and most assigned category.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "filter_assets",
                    "description": "Filter corporate assets by status, category, brand, employee, unassigned status, or recently added, with optional sorting.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "description": "Filter by status (Available, Assigned, In Repair, Returned, etc.)."},
                            "category": {"type": "string", "description": "Filter by category (Laptop, Mobile, Desktop, etc.)."},
                            "brand": {"type": "string", "description": "Filter by brand (Apple, Dell, HP, etc.)."},
                            "assigned_to": {"type": "string", "description": "Filter by assigned employee name."},
                            "unassigned": {"type": "boolean", "description": "True to show only unassigned assets."},
                            "recent": {"type": "boolean", "description": "True to show recently added assets."},
                            "sort_by": {"type": "string", "description": "Field to sort by (asset_name, category, status, asset_id)."},
                            "sort_order": {"type": "string", "description": "Sort order: asc or desc."}
                        },
                        "required": []
                    }
                }
            }
        ]

    def _call_groq(self, messages, max_retries=3):
        """Standard Groq chat completion call with retry logic."""
        retries = 0
        last_error = None
        while retries < max_retries:
            try:
                return self.client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=messages,
                    tools=self.tools,
                    tool_choice="auto",
                    temperature=0.7
                )
            except Exception as e:
                last_error = e
                err_str = str(e).lower()
                
                # Fast fail if it's a hard auth or quota error
                if "quota" in err_str or "401" in err_str or "unauthorized" in err_str:
                    logger.error("Hard error hit in Groq call, aborting retries: %s", e)
                    break
                
                if "429" in err_str or "503" in err_str or "rate limit" in err_str:
                    retries += 1
                    wait_time = retries
                    logger.warning("Groq rate limited (attempt %d/%d), waiting %ds...", retries, max_retries, wait_time)
                    time.sleep(wait_time)
                else:
                    logger.error("Groq API error: %s", e)
                    raise e
        raise last_error or Exception("Groq call failed after retries")

    def _format_tool_result_for_user(self, result: Any) -> str:
        """Format a tool result into a clean, user-friendly response."""
        if not isinstance(result, dict):
            return str(result) if result else ""
        
        parts = []
        
        if result.get("success"):
            # Analytics
            if "analytics" in result:
                an = result["analytics"]
                parts.append("# 📈 Smart Analytics")
                parts.append("")
                parts.append(f"- **📦 Total Assets:** {an.get('total_assets', 0)}")
                parts.append(f"- **✅ Available:** {an.get('available', 0)}")
                parts.append(f"- **👤 Assigned:** {an.get('assigned', 0)} ({an.get('assignment_percentage', '0.0%')})")
                parts.append(f"- **🔧 In Repair:** {an.get('repair', 0)} ({an.get('repair_percentage', '0.0%')})")
                parts.append(f"- **🏆 Most Assigned Category:** {an.get('most_assigned_category', 'None')}")
                parts.append("")
                parts.append("## Category Distribution")
                parts.append("")
                parts.append("| Category | Count |")
                parts.append("|----------|------:|")
                for cat, cnt in an.get("categories", {}).items():
                    icon = "💻" if "laptop" in cat.lower() else ("📱" if "mobile" in cat.lower() or "phone" in cat.lower() else ("🖥" if "desktop" in cat.lower() else "📦"))
                    parts.append(f"| {icon} {cat} | {cnt} |")
            # Summary / Stats
            elif "summary" in result or "stats" in result:
                data = result.get("summary") or result.get("stats", {})
                tot = data.get("total_assets", 0)
                avail = data.get("available", data.get("available_assets", 0))
                assig = data.get("assigned", data.get("assigned_assets", 0))
                rep = data.get("repair", data.get("under_audit", 0))
                ret = data.get("returned", data.get("returned_assets", 0))
                cats = data.get("categories", {})
                parts.append("# 📊 Asset Dashboard")
                parts.append("")
                parts.append("| Metric | Count |")
                parts.append("|--------|------:|")
                parts.append(f"| 📦 Total Assets | {tot} |")
                parts.append(f"| ✅ Available | {avail} |")
                parts.append(f"| 👤 Assigned | {assig} |")
                parts.append(f"| 🔧 In Repair | {rep} |")
                parts.append(f"| ↩ Returned | {ret} |")
                parts.append("")
                parts.append("## Category Distribution")
                parts.append("")
                parts.append("| Category | Count |")
                parts.append("|----------|------:|")
                for cat, cnt in cats.items():
                    icon = "💻" if "laptop" in cat.lower() else ("📱" if "mobile" in cat.lower() or "phone" in cat.lower() else ("🖥" if "desktop" in cat.lower() else "📦"))
                    parts.append(f"| {icon} {cat} | {cnt} |")
            # Asset creation
            elif "asset" in result and isinstance(result["asset"], dict):
                a = result["asset"]
                parts.append("Here are the asset details:")
                parts.append("")
                if a.get("asset_id"):
                    parts.append(f"**Asset ID:** {a['asset_id']}")
                if a.get("brand"):
                    parts.append(f"**Brand:** {a['brand']}")
                if a.get("model_number"):
                    parts.append(f"**Model:** {a['model_number']}")
                if a.get("asset_type"):
                    parts.append(f"**Type:** {a['asset_type']}")
                if a.get("status"):
                    parts.append(f"**Status:** {a['status']}")
                if a.get("assigned_to"):
                    parts.append(f"**Assigned To:** {a['assigned_to']}")
                if result.get("message"):
                    parts.insert(0, result["message"])
            # Asset ID-level result
            elif result.get("asset_id") and result.get("brand"):
                parts.append(result.get("message", "Operation completed successfully."))
                parts.append("")
                parts.append(f"**Asset ID:** {result['asset_id']}")
                if result.get("brand"):
                    parts.append(f"**Brand:** {result['brand']}")
                if result.get("model_number"):
                    parts.append(f"**Model:** {result['model_number']}")
                if result.get("asset_type"):
                    parts.append(f"**Type:** {result['asset_type']}")
                if result.get("status"):
                    parts.append(f"**Status:** {result['status']}")
                if result.get("assigned_to"):
                    parts.append(f"**Assigned To:** {result['assigned_to']}")
            # Asset lists (get_all_assets, search_assets, filter_assets, etc.)
            elif "assets" in result and isinstance(result["assets"], list):
                assets = result["assets"]
                count = len(assets)
                if count == 0:
                    parts.append("No assets found matching your query.")
                else:
                    all_avail = all((a.get("status") or "").lower() == "available" for a in assets)
                    if all_avail and count > 0:
                        parts.append("# ✅ Available Assets")
                        parts.append("")
                        parts.append("| Asset | Category | Asset ID |")
                        parts.append("|--------|----------|----------|")
                        for a in assets:
                            name = a.get("asset_name") or f"{a.get('brand', '')} {a.get('model_number', '')}".strip() or a.get("asset_type", "Asset")
                            cat = a.get("category", "General")
                            aid = a.get("asset_id", "")
                            parts.append(f"| {name} | {cat} | {aid} |")
                        parts.append("")
                        parts.append(f"Total Available Assets: {count}")
                    else:
                        parts.append("# 📋 Asset List")
                        parts.append("")
                        parts.append("| Asset Name | Category | Asset ID | Status | Assigned To |")
                        parts.append("|------------|----------|----------|---------|-------------|")
                        for a in assets:
                            name = a.get("asset_name") or f"{a.get('brand', '')} {a.get('model_number', '')}".strip() or a.get("asset_type", "Asset")
                            cat = a.get("category", "General")
                            aid = a.get("asset_id", "")
                            st_raw = a.get("status", "Available")
                            st_lower = st_raw.lower()
                            st_icon = "✅" if st_lower == "available" else ("👤" if st_lower in ["assigned", "active"] else ("🔧" if st_lower in ["in repair", "repair", "under audit"] else ("↩" if st_lower == "returned" else "📦")))
                            assigned = (a.get("assigned_to") or "").strip() or "—"
                            parts.append(f"| {name} | {cat} | {aid} | {st_icon} {st_raw} | {assigned} |")
            # Count only
            elif "count" in result and "assets" not in result:
                parts.append(f"Total assets tracked: **{result['count']}**")
            # Delete result
            elif result.get("asset_id") and result.get("message"):
                parts.append(result["message"])
            # Generic message
            elif result.get("message"):
                parts.append(result["message"])
            else:
                parts.append("Operation completed successfully.")
        elif result.get("error"):
            parts.append(f"I encountered an issue: {result['error']}")
        else:
            parts.append("Operation completed.")
        
        return "\n".join(parts)

    async def generate_response_sse(self, session: Dict[str, Any]):
        """Generates a response using Groq, handling tool calls internally and yielding SSE events."""
        history = session.get("history", [])
        metadata = session.get("metadata", {})
        
        if not self.client:
            yield "data: " + json.dumps({
                "content": {
                    "role": "model",
                    "parts": [{"text": "I'm sorry, the AI service is not properly configured. Please check the GROQ_API_KEY configuration."}]
                }
            }) + "\n\n"
            return

        memory_str = f"CURRENT_SESSION_MEMORY:\n{json.dumps(metadata, indent=2)}"
        system_instruction = f"{ROOT_AGENT_PROMPT}\n\n[SESSION_MEMORY_SYNC]\n{memory_str}\n\n(This is internal memory for reference. Do not mention it to the user.)"

        messages = [
            {"role": "system", "content": system_instruction}
        ]

        for msg in history:
            role = "user" if msg["role"] == "user" else "assistant"
            parts = []
            for p in msg.get("parts", []):
                if isinstance(p, dict) and "text" in p and p["text"]:
                    parts.append(p["text"])
            
            if parts:
                messages.append({"role": role, "content": "\n".join(parts)})

        logger.info("Request history size: %d, Groq messages count: %d", len(history), len(messages))

        try:
            if len(messages) == 1:
                messages.append({"role": "user", "content": "Hello"})
            
            last_tool_results = []
            
            try:
                response = self._call_groq(messages)
            except Exception as e:
                logger.error("Initial Groq call failed: %s", e)
                
                user_text = ""
                if history:
                    last_msg = history[-1]
                    for p in last_msg.get("parts", []):
                        if isinstance(p, dict) and "text" in p:
                            user_text += p.get("text", "")
                
                user_text_lower = user_text.lower()
                guessed_result = None
                
                if "dashboard" in user_text_lower or "summary" in user_text_lower or "overview" in user_text_lower:
                    guessed_result = get_asset_summary()
                elif "analytics" in user_text_lower or "percentage" in user_text_lower or "distribution" in user_text_lower:
                    guessed_result = get_asset_analytics()
                elif "available" in user_text_lower:
                    guessed_result = filter_assets(status="Available")
                elif "show all" in user_text_lower or "all assets" in user_text_lower or "list" in user_text_lower:
                    guessed_result = get_all_assets()
                elif "search" in user_text_lower or "find" in user_text_lower:
                    query = user_text_lower.replace("search", "").replace("find", "").strip()
                    guessed_result = search_assets(query=query)
                elif "how many" in user_text_lower or "count" in user_text_lower:
                    guessed_result = get_asset_count()
                elif "stats" in user_text_lower:
                    guessed_result = get_dashboard_stats()
                
                if guessed_result:
                    fallback_text = self._format_tool_result_for_user(guessed_result)
                    yield "data: " + json.dumps({
                        "content": {
                            "role": "model",
                            "parts": [{"text": fallback_text}]
                        }
                    }) + "\n\n"
                    return
                
                err_str = str(e).lower()
                if "429" in err_str or "quota" in err_str or "rate limit" in err_str:
                    fallback_msg = "I'm experiencing high demand right now. Please try again in a few moments."
                else:
                    fallback_msg = "I'm temporarily unable to process your request. Please try again shortly."
                
                yield "data: " + json.dumps({
                    "content": {
                        "role": "model",
                        "parts": [{"text": fallback_msg}]
                    }
                }) + "\n\n"
                return
            
            # Agentic loop — handle tool calls
            max_iterations = 5
            iteration = 0
            
            while iteration < max_iterations:
                iteration += 1
                choice = response.choices[0] if response.choices else None
                if not choice or not choice.message:
                    break
                    
                tool_calls = choice.message.tool_calls
                if not tool_calls:
                    break
                
                logger.info("Iteration %d: Tool calls: %s", iteration, [tc.function.name for tc in tool_calls])
                
                # Add assistant message with tool_calls to context cleanly without unsupported SDK fields
                assistant_msg = {
                    "role": "assistant",
                    "content": choice.message.content
                }
                if choice.message.tool_calls:
                    assistant_msg["tool_calls"] = [
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in choice.message.tool_calls
                    ]
                messages.append(assistant_msg)
                
                new_metadata_updates = {}
                for fn_call in tool_calls:
                    fn_name = fn_call.function.name
                    fn_args_str = fn_call.function.arguments or "{}"
                    try:
                        fn_args = json.loads(fn_args_str)
                        if not isinstance(fn_args, dict):
                            fn_args = {}
                    except Exception:
                        fn_args = {}

                    try:
                        if fn_name in self.tool_map:
                            result = self.tool_map[fn_name](**fn_args)
                            last_tool_results.append(result)
                            
                            # MEMORY LOGIC: Update session metadata based on tool results
                            if isinstance(result, dict) and result.get("success"):
                                asset_id = result.get("asset_id") or (result.get("asset", {}).get("asset_id") if isinstance(result.get("asset"), dict) else None)
                                
                                if fn_name == "create_asset":
                                    new_metadata_updates["last_created_asset"] = {
                                        "id": asset_id,
                                        "brand": result.get("brand") or (result.get("asset", {}).get("brand") if isinstance(result.get("asset"), dict) else None),
                                        "model": result.get("model_number") or (result.get("asset", {}).get("model_number") if isinstance(result.get("asset"), dict) else None)
                                    }
                                
                                if asset_id:
                                    recent = metadata.get("recent_assets", [])
                                    if asset_id not in recent:
                                        recent = [asset_id] + recent
                                        new_metadata_updates["recent_assets"] = recent[:10]
                                
                                assigned = result.get("assigned_to") or (result.get("asset", {}).get("assigned_to") if isinstance(result.get("asset"), dict) else None)
                                if assigned:
                                    new_metadata_updates["selected_employee"] = assigned

                        else:
                            result = {"error": f"Unknown operation requested: {fn_name}"}
                            last_tool_results.append(result)
                    except Exception as e:
                        logger.error("Tool %s execution failed: %s", fn_name, e)
                        result = {"error": str(e)}
                        last_tool_results.append(result)
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": fn_call.id,
                        "name": fn_name,
                        "content": json.dumps(result)
                    })
                
                if new_metadata_updates:
                    metadata.update(new_metadata_updates)
                    yield "data: " + json.dumps({"metadata": new_metadata_updates}) + "\n\n"

                # Re-generate with tool outputs context
                try:
                    response = self._call_groq(messages)
                except Exception as e:
                    logger.error("Groq re-call after tool execution failed: %s", e)
                    if last_tool_results:
                        fallback_text = self._format_tool_result_for_user(last_tool_results[-1])
                        yield "data: " + json.dumps({
                            "content": {
                                "role": "model",
                                "parts": [{"text": fallback_text}]
                            }
                        }) + "\n\n"
                        return
                    raise

            # Final Response Handling
            final_text = ""
            if response.choices and response.choices[0].message and response.choices[0].message.content:
                final_text = response.choices[0].message.content.strip()
            
            if final_text:
                yield "data: " + json.dumps({
                    "content": {
                        "role": "model",
                        "parts": [{"text": final_text}]
                    }
                }) + "\n\n"
            elif last_tool_results:
                fallback_text = self._format_tool_result_for_user(last_tool_results[-1])
                yield "data: " + json.dumps({
                    "content": {
                        "role": "model",
                        "parts": [{"text": fallback_text}]
                    }
                }) + "\n\n"
            else:
                yield "data: " + json.dumps({
                    "content": {
                        "role": "model",
                        "parts": [{"text": "I processed your request but couldn't generate a response. Please try rephrasing your question."}]
                    }
                }) + "\n\n"

        except Exception as e:
            logger.error("Groq processing error: %s", e)
            fallback_text = ""
            
            if last_tool_results:
                try:
                    fallback_text = self._format_tool_result_for_user(last_tool_results[-1])
                except Exception:
                    pass
            
            if not fallback_text:
                err_str = str(e).lower()
                if "429" in err_str or "quota" in err_str or "rate limit" in err_str:
                    fallback_text = "I'm experiencing high demand right now. Please try again in a few moments."
                else:
                    fallback_text = "I'm sorry, I encountered an issue processing your request. Please try again."

            yield "data: " + json.dumps({
                "content": {
                    "role": "model",
                    "parts": [{"text": fallback_text}]
                }
            }) + "\n\n"


groq_service = GroqService()
