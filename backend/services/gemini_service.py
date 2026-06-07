import os
import json
import logging
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
from agent.tools import (
    get_assets, create_asset, get_asset_by_id, update_asset, 
    delete_asset, assign_asset, return_asset, mark_clearance, 
    search_assets, get_assets_by_status, get_assets_by_employee, 
    get_all_assets, get_asset_count, get_dashboard_stats, get_audit_logs
)
from agent.prompt import ROOT_AGENT_PROMPT

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Model configuration
MODEL_NAME = "gemini-flash-latest"


# Custom Function Declaration for create_asset to support optional arguments without default value errors.
create_asset_decl = types.FunctionDeclaration(
    name="create_asset",
    description="Create a new corporate asset. Required parameters: asset_type, brand, model_number. All other parameters are optional.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "asset_type": types.Schema(type=types.Type.STRING, description="The type of the asset (e.g. Laptop, Mobile, Monitor)."),
            "brand": types.Schema(type=types.Type.STRING, description="The brand of the asset (e.g. Apple, Dell, Lenovo)."),
            "model_number": types.Schema(type=types.Type.STRING, description="The model number of the asset (e.g. MacBook Pro 16)."),
            "status": types.Schema(type=types.Type.STRING, description="Optional. The status of the asset (e.g. Available, Assigned). Defaults to 'Available'."),
            "assigned_to": types.Schema(type=types.Type.STRING, description="Optional. The name of the employee to assign this asset to."),
            "purchase_date": types.Schema(type=types.Type.STRING, description="Optional. The purchase date in YYYY-MM-DD format."),
            "asset_name": types.Schema(type=types.Type.STRING, description="Optional. A custom name for the asset. Defaults to asset_type."),
            "category": types.Schema(type=types.Type.STRING, description="Optional. The category of the asset (e.g. Laptop, Desktop, Accessory)."),
            "warranty_expiry": types.Schema(type=types.Type.STRING, description="Optional. The warranty expiry date in YYYY-MM-DD format."),
            "location": types.Schema(type=types.Type.STRING, description="Optional. The location of the asset."),
            "notes": types.Schema(type=types.Type.STRING, description="Optional. Additional notes.")
        },
        required=["asset_type", "brand", "model_number"]
    )
)


class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            logger.error("GOOGLE_API_KEY is missing in environment variables")
            self.client = None
        else:
            self.client = genai.Client(api_key=self.api_key)
        
        self.tools_list = [
            get_assets, create_asset, get_asset_by_id, update_asset, 
            delete_asset, assign_asset, return_asset, mark_clearance, 
            search_assets, get_assets_by_status, get_assets_by_employee, 
            get_asset_count, get_dashboard_stats, get_audit_logs
        ]
        
        self.tool_map = {tool.__name__: tool for tool in self.tools_list}
        
        prepared_tools = self._prepare_tools() if self.client else self.tools_list
        
        self.config = types.GenerateContentConfig(
            tools=prepared_tools,
            system_instruction=ROOT_AGENT_PROMPT,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
        )

    def _prepare_tools(self):
        """Converts callable tools to schemas and strips default values to prevent Gemini API errors."""
        decls = []
        for tool in self.tools_list:
            if getattr(tool, "__name__", None) == "create_asset":
                decls.append(create_asset_decl)
            elif callable(tool):
                try:
                    decl = types.FunctionDeclaration.from_callable(callable=tool, client=self.client)
                    self._strip_defaults_from_schema(decl.parameters)
                    decls.append(decl)
                except Exception as e:
                    logger.error(f"Error preparing schema for tool {tool.__name__}: {e}")
            else:
                decls.append(tool)
        return [types.Tool(function_declarations=decls)]

    def _strip_defaults_from_schema(self, schema):
        """Recursively removes 'default' values from schema fields."""
        if not schema:
            return
        schema.__dict__.pop('default', None)
        if hasattr(schema, 'model_fields_set'):
            schema.model_fields_set.discard('default')
        if hasattr(schema, 'properties') and schema.properties:
            for prop in schema.properties.values():
                self._strip_defaults_from_schema(prop)

    def _call_gemini(self, contents, max_retries=3):
        """Standard Gemini call with retry logic."""
        retries = 0
        last_error = None
        while retries < max_retries:
            try:
                return self.client.models.generate_content(
                    model=MODEL_NAME,
                    contents=contents,
                    config=self.config
                )
            except Exception as e:
                last_error = e
                err_str = str(e).lower()
                
                # Fast fail if it's a hard quota limit
                if "quota" in err_str and "exceeded" in err_str:
                    logger.error(f"Hard quota limit hit, aborting retries.")
                    break
                
                if "429" in err_str or "503" in err_str or "resource" in err_str:
                    retries += 1
                    wait_time = retries  # Reduced backoff to 1s, 2s, 3s to improve UX
                    logger.warning(f"Gemini rate limited (attempt {retries}/{max_retries}), waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Gemini API error: {e}")
                    raise e
        raise last_error or Exception("Gemini call failed after retries")

    def _format_tool_result_for_user(self, result: Any) -> str:
        """Format a tool result into a clean, user-friendly response."""
        if not isinstance(result, dict):
            return str(result) if result else ""
        
        parts = []
        
        if result.get("success"):
            # Asset creation
            if "asset" in result and isinstance(result["asset"], dict):
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
            # Asset ID-level result (e.g. create_asset returns flat)
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
            # Count results
            elif "count" in result and "assets" in result:
                count = result["count"]
                assets = result["assets"]
                if count == 0:
                    parts.append("No assets found matching your query.")
                else:
                    parts.append(f"Found **{count}** asset(s):")
                    parts.append("")
                    for a in assets[:10]:
                        brand = a.get("brand", "")
                        model = a.get("model_number", "")
                        atype = a.get("asset_type", "")
                        aid = a.get("asset_id", "")
                        status = a.get("status", "")
                        assigned = a.get("assigned_to", "")
                        line = f"• **{brand} {model}** ({atype}) — ID: `{aid}`, Status: {status}"
                        if assigned:
                            line += f", Assigned to: {assigned}"
                        parts.append(line)
                    if count > 10:
                        parts.append(f"\n...and {count - 10} more.")
            # Count only
            elif "count" in result and "assets" not in result:
                parts.append(f"Total assets tracked: **{result['count']}**")
            # Stats
            elif "stats" in result:
                stats = result["stats"]
                parts.append("📊 **Dashboard Statistics**")
                parts.append("")
                parts.append(f"• Total Assets: **{stats.get('total_assets', 0)}**")
                parts.append(f"• Assigned: **{stats.get('assigned_assets', 0)}**")
                parts.append(f"• Available: **{stats.get('available_assets', 0)}**")
                parts.append(f"• Returned: **{stats.get('returned_assets', 0)}**")
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
        """Generates a response, handling tool calls internally and cleaning history."""
        history = session.get("history", [])
        metadata = session.get("metadata", {})
        
        if not self.client:
            yield "data: " + json.dumps({
                "content": {
                    "role": "model",
                    "parts": [{"text": "I'm sorry, the AI service is not properly configured. Please check the API key configuration."}]
                }
            }) + "\n\n"
            return

        # Filter history to include ONLY text parts for stability.
        cleaned_contents = []
        
        # Inject memory context at the beginning
        memory_str = f"CURRENT_SESSION_MEMORY:\n{json.dumps(metadata, indent=2)}"
        cleaned_contents.append(types.Content(
            role="user", 
            parts=[types.Part.from_text(text=f"[SESSION_MEMORY_SYNC]\n{memory_str}\n\n(This is internal memory for reference. Do not mention it to the user.)")]
        ))

        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            parts = []
            for p in msg.get("parts", []):
                # Only keep plain text for stability
                if isinstance(p, dict) and "text" in p and p["text"]:
                    parts.append(types.Part.from_text(text=p["text"]))
            
            if parts:
                cleaned_contents.append(types.Content(role=role, parts=parts))

        logger.info(f"Request history size: {len(history)}, cleaned contents: {len(cleaned_contents)}")

        try:
            # Step 1: Initial call
            if not cleaned_contents:
                cleaned_contents = [types.Content(role="user", parts=[types.Part.from_text(text="Hello")])]
            
            last_tool_results = []
            
            try:
                response = self._call_gemini(cleaned_contents)
            except Exception as e:
                logger.error(f"Initial Gemini call failed: {e}")
                
                # Fallback: try to guess the tool based on keywords
                user_text = ""
                if history:
                    last_msg = history[-1]
                    for p in last_msg.get("parts", []):
                        if isinstance(p, dict) and "text" in p:
                            user_text += p.get("text", "")
                
                user_text_lower = user_text.lower()
                guessed_result = None
                
                if "show all" in user_text_lower or "all assets" in user_text_lower or "list" in user_text_lower:
                    guessed_result = get_all_assets()
                elif "search" in user_text_lower or "find" in user_text_lower:
                    query = user_text_lower.replace("search", "").replace("find", "").strip()
                    guessed_result = search_assets(query=query)
                elif "how many" in user_text_lower or "count" in user_text_lower:
                    guessed_result = get_asset_count()
                elif "stats" in user_text_lower or "dashboard" in user_text_lower:
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
                
                # If no tool guess possible, give a friendly error
                err_str = str(e).lower()
                if "429" in err_str or "quota" in err_str or "resource" in err_str:
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
                if not response.candidates or not response.candidates[0].content.parts:
                    break
                    
                function_calls = [p.function_call for p in response.candidates[0].content.parts if p.function_call]
                if not function_calls:
                    break
                
                logger.info(f"Iteration {iteration}: Tool calls: {[fc.name for fc in function_calls]}")
                
                # Add model's message to context (containing the function call)
                cleaned_contents.append(response.candidates[0].content)
                
                new_metadata_updates = {}
                tool_responses_parts = []
                for fn_call in function_calls:
                    fn_name = fn_call.name
                    fn_args = fn_call.args
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
                                        "brand": result.get("brand") or result.get("asset", {}).get("brand"),
                                        "model": result.get("model_number") or result.get("asset", {}).get("model_number")
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
                            result = {"error": f"Unknown operation requested"}
                            last_tool_results.append(result)
                    except Exception as e:
                        logger.error(f"Tool {fn_name} execution failed: {e}")
                        result = {"error": str(e)}
                        last_tool_results.append(result)
                    
                    tool_responses_parts.append(types.Part.from_function_response(name=fn_name, response=result))
                
                # Update session with new metadata immediately
                if new_metadata_updates:
                    metadata.update(new_metadata_updates)
                    yield "data: " + json.dumps({"metadata": new_metadata_updates}) + "\n\n"

                # Add tool outputs to context
                cleaned_contents.append(types.Content(role="user", parts=tool_responses_parts))
                
                # Re-generate with tool context
                try:
                    response = self._call_gemini(cleaned_contents)
                except Exception as e:
                    logger.error(f"Gemini re-call after tool execution failed: {e}")
                    # Use formatted tool results as fallback
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
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if part.text:
                        final_text += part.text
            
            if final_text:
                yield "data: " + json.dumps({
                    "content": {
                        "role": "model",
                        "parts": [{"text": final_text}]
                    }
                }) + "\n\n"
            elif last_tool_results:
                # Gemini returned empty but we have tool results — format them nicely
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
            logger.error(f"Gemini processing error: {e}")
            
            # Clean fallback — never expose internals
            fallback_text = ""
            
            if last_tool_results:
                try:
                    fallback_text = self._format_tool_result_for_user(last_tool_results[-1])
                except Exception:
                    pass
            
            if not fallback_text:
                err_str = str(e).lower()
                if "429" in err_str or "quota" in err_str or "resource" in err_str:
                    fallback_text = "I'm experiencing high demand right now. Please try again in a few moments."
                else:
                    fallback_text = "I'm sorry, I encountered an issue processing your request. Please try again."

            yield "data: " + json.dumps({
                "content": {
                    "role": "model",
                    "parts": [{"text": fallback_text}]
                }
            }) + "\n\n"

gemini_service = GeminiService()
