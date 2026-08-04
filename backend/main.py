import os
import sys
import uuid
import json
import uvicorn
import logging
import socket
from datetime import datetime
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Validate API key
api_key = os.environ.get("GROQ_API_KEY", "")

from core.sqlite_db import SQLiteDB
from services import assets_service
from services.groq_service import groq_service
from routers import assets

app = FastAPI(title="AssetsTracking Agent API")

# Configure allowed origins for CORS
ALLOWED_ORIGINS = [
    "https://asset-tracking-agent.vercel.app",
    "https://asset-tracking-agent-git-main-bhoomika-s-js-projects.vercel.app",
    "http://localhost:5173",
    "http://localhost:8080",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8080",
]
if os.environ.get("CORS_ORIGINS"):
    ALLOWED_ORIGINS.extend([origin.strip() for origin in os.environ["CORS_ORIGINS"].split(",") if origin.strip()])

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"https://.*\.vercel\.app|http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Persistent session store
SESSIONS_FILE = "sessions.json"

def load_sessions():
    if os.path.exists(SESSIONS_FILE):
        try:
            with open(SESSIONS_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading sessions: {e}")
    return {}

def save_sessions(sessions):
    try:
        with open(SESSIONS_FILE, "w") as f:
            json.dump(sessions, f)
    except Exception as e:
        logger.error(f"Error saving sessions: {e}")

def get_session_data(sid):
    if sid not in sessions_db:
        sessions_db[sid] = {
            "history": [],
            "metadata": {
                "last_created_asset": None,
                "recent_assets": [],
                "selected_employee": None
            }
        }
    # Migration for old list-based sessions
    if isinstance(sessions_db[sid], list):
        sessions_db[sid] = {
            "history": sessions_db[sid],
            "metadata": {
                "last_created_asset": None,
                "recent_assets": [],
                "selected_employee": None
            }
        }
    return sessions_db[sid]

sessions_db: Dict[str, Any] = load_sessions()

class ChatRequest(BaseModel):
    appName: str
    newMessage: Dict[str, Any]
    sessionId: str
    userId: str
    streaming: bool = False

@app.get("/apps/agent/users/user/sessions")
async def get_sessions():
    return [{"id": sid, "updated_at": datetime.now().isoformat()} for sid in sessions_db.keys()]

@app.post("/apps/agent/users/user/sessions")
async def create_session():
    sid = str(uuid.uuid4())
    sessions_db[sid] = {
        "history": [],
        "metadata": {
            "last_created_asset": None,
            "recent_assets": [],
            "selected_employee": None
        }
    }
    save_sessions(sessions_db)
    return {"id": sid}

@app.get("/apps/agent/users/user/sessions/{sid}")
async def get_session(sid: str):
    if sid not in sessions_db:
        raise HTTPException(status_code=404, detail="Session not found")
    data = get_session_data(sid)
    return {"id": sid, "events": [{"content": msg} for msg in data["history"]]}

@app.delete("/apps/agent/users/user/sessions/{sid}")
async def delete_session(sid: str):
    if sid in sessions_db:
        del sessions_db[sid]
        save_sessions(sessions_db)
    return {"status": "deleted"}

@app.post("/run_sse")
async def run_sse(req: ChatRequest):
    sid = req.sessionId
    session = get_session_data(sid)
    
    # Add user message to history
    session["history"].append(req.newMessage)
    
    async def event_generator():
        try:
            async for chunk in groq_service.generate_response_sse(session):
                yield chunk
                
                # Parse chunk to collect for history
                if chunk.startswith("data: "):
                    try:
                        data = json.loads(chunk[6:])
                        if "content" in data:
                            role = data["content"].get("role", "model")
                            parts = data["content"].get("parts", [])
                            
                            # Filter only text parts for history
                            text_parts = [p for p in parts if isinstance(p, dict) and "text" in p and p["text"]]
                            
                            if text_parts:
                                session["history"].append({
                                    "role": role,
                                    "parts": text_parts
                                })
                                save_sessions(sessions_db)
                        
                        # Update metadata if returned in chunk (internal protocol)
                        if "metadata" in data:
                            session["metadata"].update(data["metadata"])
                            save_sessions(sessions_db)
                            
                    except Exception as e:
                        logger.error(f"Error parsing SSE chunk for history: {e}")
        except Exception as e:
            logger.error(f"SSE Error: {e}")
            yield "data: " + json.dumps({
                "content": {
                    "role": "model",
                    "parts": [{"text": "I'm sorry, I encountered an issue processing your request. Please try again."}]
                }
            }) + "\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# Include routers
app.include_router(assets.router, prefix="/assets", tags=["Assets"])

# Serve the React frontend build
frontend_dist = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "dist")
if not os.path.isdir(frontend_dist):
    frontend_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "dist")

if os.path.isdir(frontend_dist):
    from fastapi.responses import FileResponse
    
    @app.get("/app/{full_path:path}")
    async def serve_frontend(full_path: str):
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))
    
    app.mount("/app-static", StaticFiles(directory=frontend_dist), name="frontend")

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "api_key_configured": bool(api_key and api_key != "your_groq_api_key_here"),
        "version": "2.3.0"
    }

if os.path.isdir(frontend_dist):
    from fastapi.responses import FileResponse
    @app.get("/")
    async def serve_root():
        return FileResponse(os.path.join(frontend_dist, "index.html"))

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))

def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0

def find_available_port(priority_ports: List[int]) -> int:
    for port in priority_ports:
        if not is_port_in_use(port):
            return port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]

if __name__ == "__main__":
    priority_ports = [8080, 8000, 8001, 9000]
    default_port = int(os.environ.get("PORT", 0))
    
    if default_port and not is_port_in_use(default_port):
        final_port = default_port
    else:
        final_port = find_available_port(priority_ports)
        
    print(f"\n>>> AssetsTracking Server running at:")
    print(f">>> http://localhost:{final_port}\n")
    
    uvicorn.run(app, host="0.0.0.0", port=final_port)
