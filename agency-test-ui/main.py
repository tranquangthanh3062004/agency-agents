import os
import json
import glob
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import httpx

app = FastAPI(title="The Agency - Multi-Agent Studio")

BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parent

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# Load divisions configuration if available
DIVISIONS_PATH = REPO_ROOT / "divisions.json"
DIVISIONS_DATA = {}
if DIVISIONS_PATH.exists():
    try:
        with open(DIVISIONS_PATH, "r", encoding="utf-8") as f:
            DIVISIONS_DATA = json.load(f).get("divisions", {})
    except Exception as e:
        print(f"Error loading divisions.json: {e}")

class ExecutionRequest(BaseModel):
    division: str
    agent_slug: str
    task_prompt: str
    api_key: Optional[str] = None
    router_base_url: Optional[str] = "https://openrouter.ai/api/v1"
    model_name: Optional[str] = "google/gemma-2-9b-it:free"

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/divisions")
async def get_divisions():
    """Return all agent divisions."""
    divisions_list = []
    # Scan directories in repo root that have markdown files (excluding scripts, .github, etc.)
    excluded_dirs = {".git", ".github", "scripts", "strategy", "integrations", "examples", "agency-test-ui"}
    
    for item in os.listdir(REPO_ROOT):
        dir_path = REPO_ROOT / item
        if dir_path.is_dir() and item not in excluded_dirs and not item.startswith("."):
            md_files = list(dir_path.glob("*.md"))
            if md_files:
                meta = DIVISIONS_DATA.get(item, {})
                divisions_list.append({
                    "id": item,
                    "label": meta.get("label", item.replace("-", " ").title()),
                    "icon": meta.get("icon", "Folder"),
                    "color": meta.get("color", "#3B82F6"),
                    "agent_count": len(md_files)
                })
    
    divisions_list.sort(key=lambda x: x["label"])
    return JSONResponse({"divisions": divisions_list})

@app.get("/api/agents/{division}")
async def get_agents(division: str):
    """Return list of agents for a given division."""
    div_path = REPO_ROOT / division
    if not div_path.exists() or not div_path.is_dir():
        raise HTTPException(status_code=404, detail="Division not found")
    
    agents = []
    for file_path in div_path.glob("*.md"):
        slug = file_path.stem
        # Extract title or first header from file
        title = slug.replace(f"{division}-", "").replace("-", " ").title()
        agents.append({
            "slug": slug,
            "filename": file_path.name,
            "title": title
        })
    
    agents.sort(key=lambda x: x["title"])
    return JSONResponse({"agents": agents})

@app.get("/api/agent-detail/{division}/{slug}")
async def get_agent_detail(division: str, slug: str):
    """Read agent system prompt definition."""
    file_path = REPO_ROOT / division / f"{slug}.md"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Agent file not found")
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return JSONResponse({"slug": slug, "content": content})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/execute")
async def execute_task(req: ExecutionRequest):
    """Execute a task with the chosen agent prompt via OpenRouter or custom router."""
    file_path = REPO_ROOT / req.division / f"{req.agent_slug}.md"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Agent file not found")
    
    with open(file_path, "r", encoding="utf-8") as f:
        agent_system_prompt = f.read()
    
    api_key = req.api_key or os.getenv("OPENROUTER_API_KEY", "")
    if not api_key:
        return JSONResponse({
            "success": False,
            "error": "Thiếu API Key! Vui lòng nhập OpenRouter API Key (hoặc Omni Router Key) trên giao diện."
        }, status_code=400)
    
    base_url = (req.router_base_url or "https://openrouter.ai/api/v1").rstrip("/")
    target_endpoint = f"{base_url}/chat/completions"
    
    payload = {
        "model": req.model_name or "google/gemma-2-9b-it:free",
        "messages": [
            {
                "role": "system",
                "content": agent_system_prompt
            },
            {
                "role": "user",
                "content": req.task_prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 4000
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://agency-test.local",
        "X-Title": "The Agency Multi-Agent Test Studio"
    }
    
    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            resp = await client.post(target_endpoint, headers=headers, json=payload)
            if resp.status_code != 200:
                return JSONResponse({
                    "success": False,
                    "error": f"Router API trả về lỗi {resp.status_code}: {resp.text}"
                }, status_code=resp.status_code)
            
            data = resp.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "Không có phản hồi.")
            usage = data.get("usage", {})
            return JSONResponse({
                "success": True,
                "result": content,
                "usage": usage,
                "model_used": data.get("model", req.model_name)
            })
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": f"Lỗi kết nối tới Router: {str(e)}"
        }, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

