import os
import uvicorn
from core.sqlite_db import SQLiteDB
from google.adk.cli.fast_api import get_fast_api_app
from fastapi.middleware.cors import CORSMiddleware
from services import assets_service
from routers import assets


# Get the directory where main.py is located
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Configure allowed origins for CORS - Add your domains here
ALLOWED_ORIGINS = ["*"]  # Only for dev; restrict later

SERVE_WEB_INTERFACE = True

# Create app via ADK wrapper
app = get_fast_api_app(
    agents_dir=AGENT_DIR,
    allow_origins=ALLOWED_ORIGINS,
    web=SERVE_WEB_INTERFACE,
)

# ✅ Add CORS middleware manually
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # e.g., ["http://127.0.0.1:5500"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers

app.include_router(assets.router, prefix="/assets", tags=["Assets"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))


