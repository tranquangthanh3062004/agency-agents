import os
import json
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

class PipelineAgentStep(BaseModel):
    division: str
    agent_slug: str
    label: Optional[str] = ""

class PipelineRequest(BaseModel):
    pipeline_name: str
    task_prompt: str
    steps: List[PipelineAgentStep]
    api_key: Optional[str] = None
    router_base_url: Optional[str] = "https://openrouter.ai/api/v1"
    model_name: Optional[str] = "google/gemma-2-9b-it:free"

class ClientBrief(BaseModel):
    name: str
    contact: str
    service: str
    details: Optional[str] = ""

@app.get("/", response_class=HTMLResponse)
async def home_landing(request: Request):
    """Client-facing landing page."""
    return templates.TemplateResponse("landing.html", {"request": request})

@app.get("/studio", response_class=HTMLResponse)
async def studio_app(request: Request):
    """Internal studio for running multi-agent workflows."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/admin", response_class=HTMLResponse)
async def admin_portal(request: Request):
    """Admin portal to view and manage leads and briefs."""
    return templates.TemplateResponse("admin.html", {"request": request})

@app.get("/api/leads")
async def get_leads():
    """Retrieve all leads from persistent ledger."""
    leads_file = BASE_DIR / "leads.json"
    if not leads_file.exists():
        return JSONResponse({"leads": []})
    try:
        with open(leads_file, "r", encoding="utf-8") as f:
            leads = json.load(f)
        return JSONResponse({"leads": leads})
    except Exception as e:
        return JSONResponse({"leads": [], "error": str(e)})

class UpdateStatusRequest(BaseModel):
    status: str

@app.put("/api/leads/{index}/status")
async def update_lead_status(index: int, req: UpdateStatusRequest):
    """Update lead status by index."""
    leads_file = BASE_DIR / "leads.json"
    if not leads_file.exists():
        raise HTTPException(status_code=404, detail="No leads found")
    with open(leads_file, "r", encoding="utf-8") as f:
        leads = json.load(f)
    if index < 0 or index >= len(leads):
        raise HTTPException(status_code=404, detail="Lead index out of range")
    leads[index]["status"] = req.status
    with open(leads_file, "w", encoding="utf-8") as f:
        json.dump(leads, f, ensure_ascii=False, indent=2)
    return JSONResponse({"success": True})

class RefineRequest(BaseModel):
    current_content: str
    feedback_instruction: str
    agent_slug: Optional[str] = "assistant"
    division: Optional[str] = "engineering"
    api_key: Optional[str] = None
    router_base_url: Optional[str] = "https://openrouter.ai/api/v1"
    model_name: Optional[str] = "google/gemma-2-9b-it:free"

@app.post("/api/refine")
async def refine_deliverable(req: RefineRequest):
    """Refine an existing deliverable based on founder/client feedback."""
    api_key = req.api_key or DEFAULT_API_KEY or os.getenv("OPENROUTER_API_KEY", "")
    if not api_key:
        return JSONResponse({
            "success": False,
            "error": "Thiếu API Key để tinh chỉnh sản phẩm!"
        }, status_code=400)
    
    base_url = (req.router_base_url or "https://openrouter.ai/api/v1").rstrip("/")
    target_endpoint = f"{base_url}/chat/completions"
    
    system_prompt = (
        "Bạn là một chuyên gia AI cao cấp đang hỗ trợ người dùng chỉnh sửa, hoàn thiện và nâng cấp một sản phẩm bàn giao (Deliverable). "
        "Hãy đọc kỹ sản phẩm hiện tại và yêu cầu chỉnh sửa, sau đó trả về bản cập nhật hoàn chỉnh, giữ nguyên các phần tốt và sửa các điểm được yêu cầu."
    )
    user_prompt = (
        f"### SẢN PHẨM HIỆN TẠI:\n{req.current_content}\n\n"
        f"### YÊU CẦU ĐIỀU CHỈNH / PHẢN HỒI:\n{req.feedback_instruction}\n\n"
        f"Hãy trả về bản cập nhật hoàn chỉnh nhất."
    )
    
    try:
        content = await call_llm(target_endpoint, api_key, req.model_name, system_prompt, user_prompt)
        return JSONResponse({
            "success": True,
            "result": content,
            "model_used": req.model_name
        })
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": f"Lỗi tinh chỉnh: {str(e)}"
        }, status_code=500)


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
DEFAULT_API_KEY = os.getenv("DEFAULT_API_KEY", "") or os.getenv("OPENROUTER_API_KEY", "")

@app.post("/api/submit-brief")
async def submit_brief(brief: ClientBrief):
    """Save customer brief into a persistent JSON ledger and push Telegram alert if configured."""
    leads_file = BASE_DIR / "leads.json"
    leads = []
    if leads_file.exists():
        try:
            with open(leads_file, "r", encoding="utf-8") as f:
                leads = json.load(f)
        except Exception:
            leads = []
    
    new_lead = brief.dict()
    new_lead["created_at"] = import_time()
    leads.append(new_lead)
    
    with open(leads_file, "w", encoding="utf-8") as f:
        json.dump(leads, f, ensure_ascii=False, indent=2)
        
    # Gửi thông báo Telegram tức thì về điện thoại (nếu có cấu hình)
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        try:
            tg_text = (
                f"🚀 <b>CÓ KHÁCH HÀNG MỚI ĐĂNG KÝ!</b>\n\n"
                f"👤 <b>Họ tên:</b> {brief.name}\n"
                f"📞 <b>Liên hệ:</b> {brief.contact}\n"
                f"💼 <b>Gói quan tâm:</b> {brief.service}\n"
                f"📝 <b>Mô tả:</b> {brief.details or 'Không có'}\n"
                f"⏰ <b>Thời gian:</b> {new_lead['created_at']}"
            )
            tg_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            async with httpx.AsyncClient(timeout=10.0) as client:
                await client.post(tg_url, json={
                    "chat_id": TELEGRAM_CHAT_ID,
                    "text": tg_text,
                    "parse_mode": "HTML"
                })
        except Exception as e:
            print(f"Lỗi gửi Telegram: {e}")
        
    return JSONResponse({"success": True, "message": "Lead saved successfully"})

def import_time():
    from datetime import datetime
    return datetime.now().isoformat()


@app.get("/api/divisions")
async def get_divisions():
    """Return all agent divisions."""
    divisions_list = []
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

async def call_llm(target_endpoint: str, api_key: str, model_name: str, system_prompt: str, user_prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://agency-test.local",
        "X-Title": "The Agency Multi-Agent Test Studio"
    }
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 4000
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(target_endpoint, headers=headers, json=payload)
        if resp.status_code != 200:
            raise Exception(f"Router API error ({resp.status_code}): {resp.text}")
        data = resp.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", "Không có nội dung phản hồi.")

@app.post("/api/execute")
async def execute_task(req: ExecutionRequest):
    """Execute a single agent task."""
    file_path = REPO_ROOT / req.division / f"{req.agent_slug}.md"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Agent file not found")
    
    with open(file_path, "r", encoding="utf-8") as f:
        agent_system_prompt = f.read()
    
    api_key = req.api_key or DEFAULT_API_KEY or os.getenv("OPENROUTER_API_KEY", "")
    if not api_key:
        return JSONResponse({
            "success": False,
            "error": "Thiếu API Key! Vui lòng dán OpenRouter API Key hoặc cấu hình biến DEFAULT_API_KEY trên server."
        }, status_code=400)
    
    base_url = (req.router_base_url or "https://openrouter.ai/api/v1").rstrip("/")
    target_endpoint = f"{base_url}/chat/completions"
    
    try:
        content = await call_llm(target_endpoint, api_key, req.model_name, agent_system_prompt, req.task_prompt)
        return JSONResponse({
            "success": True,
            "result": content,
            "model_used": req.model_name
        })
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": f"Lỗi thực thi: {str(e)}"
        }, status_code=500)

@app.post("/api/execute-pipeline")
async def execute_pipeline(req: PipelineRequest):
    """Execute a multi-agent pipeline using NEXUS handoff protocol."""
    api_key = req.api_key or DEFAULT_API_KEY or os.getenv("OPENROUTER_API_KEY", "")
    if not api_key:
        return JSONResponse({
            "success": False,
            "error": "Thiếu API Key! Vui lòng nhập API Key hoặc cấu hình biến DEFAULT_API_KEY trên server để chạy Pipeline."
        }, status_code=400)
    
    base_url = (req.router_base_url or "https://openrouter.ai/api/v1").rstrip("/")
    target_endpoint = f"{base_url}/chat/completions"
    
    steps_results = []
    accumulated_context = ""
    
    for idx, step in enumerate(req.steps):
        file_path = REPO_ROOT / step.division / f"{step.agent_slug}.md"
        if not file_path.exists():
            return JSONResponse({
                "success": False,
                "error": f"Không tìm thấy agent file: {step.division}/{step.agent_slug}.md"
            }, status_code=404)
        
        with open(file_path, "r", encoding="utf-8") as f:
            system_prompt = f.read()
        
        if idx == 0:
            prompt_for_agent = (
                f"DỰ ÁN / NHIỆM VỤ GỐC TỪ KHÁCH HÀNG:\n{req.task_prompt}\n\n"
                f"Hãy phân tích và thực hiện phần việc của bạn theo đúng quy trình chuyên môn."
            )
        else:
            prev_agent = req.steps[idx - 1].agent_slug
            prompt_for_agent = (
                f"### [NEXUS PROTOCOL] BIÊN BẢN CHUYỂN GIAO (HANDOFF TRANSFER)\n"
                f"- **Từ chuyên gia tiền nhiệm**: {prev_agent}\n"
                f"- **Nhiệm vụ tổng thể**: {req.task_prompt}\n"
                f"- **Sản phẩm bàn giao từ bước trước**:\n\n"
                f"{accumulated_context}\n\n"
                f"--- \n"
                f"NHIỆM VỤ CỦA BẠN ({step.agent_slug}):\n"
                f"Dựa trên sản phẩm của chuyên gia tiền nhiệm, hãy đánh giá, hoàn thiện, phản biện, kiểm tra chất lượng (QA) "
                f"hoặc bổ sung phần chuyên môn của bạn để tạo ra sản phẩm hoàn chỉnh nhất."
            )
        
        try:
            output = await call_llm(target_endpoint, api_key, req.model_name, system_prompt, prompt_for_agent)
            accumulated_context = output
            steps_results.append({
                "step_number": idx + 1,
                "agent_slug": step.agent_slug,
                "division": step.division,
                "label": step.label or step.agent_slug,
                "output": output
            })
        except Exception as e:
            return JSONResponse({
                "success": False,
                "error": f"Lỗi tại Bước {idx+1} ({step.agent_slug}): {str(e)}"
            }, status_code=500)
            
    return JSONResponse({
        "success": True,
        "pipeline_name": req.pipeline_name,
        "steps": steps_results,
        "final_result": accumulated_context
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
