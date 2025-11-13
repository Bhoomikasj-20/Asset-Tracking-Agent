from google.adk.agents import LlmAgent
from agent.tools import *
from agent.prompt import *





Model = "gemini-2.0-flash"
root_agent=LlmAgent(
    name="Assets_tracking_agent",
    model = Model,
    description="AssetsTrackingAgent, corporates and enterprises can converse naturally with AI Agent to eliminate the tedious manual process of tracking inventory and reporting it for audit compliance.", 
    instruction=ROOT_AGENT_PROMPT,
    tools= [
   get_assets,
   create_asset,
   delete_asset, 
   get_asset_by_id,
   update_asset,
   

   ]
)

