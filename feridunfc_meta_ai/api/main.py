from fastapi import FastAPI, HTTPException, Header, Depends, status, Query
from pydantic import BaseModel
from typing import Dict, Optional, List
import os  # <-- EKLE

from ..orchestrator.sprint_orchestrator import SprintOrchestrator
from ..config.settings import settings

from ..orchestrator.sprint_orchestrator import SprintOrchestrator
from ..config.settings import settings

app = FastAPI(title="Secure Meta AI Orchestrator")

class CreateReq(BaseModel):
    requirements: str
    workdir: Optional[str] = None
    concurrency: int = 2
    max_retries: int = 1

class Summary(BaseModel):
    sprint_id: str; title: str; total_tasks: int

def auth(x_api_key: Optional[str] = Header(None)):
    import os  # lokal import
    expected = getattr(settings, "api_key", os.getenv("API_KEY", "dev-secret"))
    if expected and x_api_key != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    return True


class Manager:
    def __init__(self): self.pool: Dict[str, SprintOrchestrator] = {}

    async def create(self, req: CreateReq) -> Summary:
        orch = SprintOrchestrator(concurrency=req.concurrency)
        await orch.initialize(workdir=req.workdir)
        s = await orch.plan_sprint_from_requirements(req.requirements)
        self.pool[s.id] = orch
        return Summary(sprint_id=s.id, title=s.title, total_tasks=s.get_total_tasks())

    def get(self, sid: str) -> SprintOrchestrator:
        if sid not in self.pool: raise HTTPException(status_code=404, detail="Not found")
        return self.pool[sid]

    def list(self) -> List[str]: return list(self.pool.keys())

mgr = Manager()

@app.post("/sprints", response_model=Summary)
async def create_sprint(req: CreateReq, _=Depends(auth)): return await mgr.create(req)

@app.get("/sprints", response_model=List[Summary])
async def list_sprints(_=Depends(auth)):
    out = []
    for sid in mgr.list():
        o = mgr.get(sid); rep = o.get_sprint_report()
        out.append(Summary(sprint_id=sid, title=rep.get("title",""), total_tasks=rep.get("total_tasks",0)))
    return out

@app.post("/sprints/{sid}/execute", response_model=Dict)
async def execute_sprint(sid: str, max_retries: int = Query(1, ge=0, le=5), _=Depends(auth)):
    o = mgr.get(sid); return await o.execute_sprint(max_retries=max_retries)

@app.get("/sprints/{sid}/report", response_model=Dict)
async def report(sid: str, _=Depends(auth)):
    o = mgr.get(sid); return o.get_sprint_report()
# --- API Key middleware (auto-added) ---
from fastapi import Request
from fastapi.responses import JSONResponse

try:
    from .dependencies import API_KEY  # type: ignore
except Exception:   # pragma: no cover
    import os
    API_KEY = os.getenv("API_KEY", "dev-secret")

@app.middleware("http")
async def _api_key_guard(request: Request, call_next):
    # docs ve health serbest
    if request.url.path in ("/", "/health") or request.url.path.startswith(("/docs", "/openapi", "/redoc")):
        return await call_next(request)
    if request.headers.get("x-api-key") != API_KEY:
        return JSONResponse({"detail": "Invalid API Key"}, status_code=401)
    return await call_next(request)
# --- /API Key middleware ---




def auth(x_api_key: Optional[str] = Header(None)):
    # API key'i şu öncelik ile al:
    # 1) settings.api_key (varsa)
    # 2) ortam değişkeni API_KEY (varsa)
    # 3) "dev-secret" (default)
    expected = (getattr(settings, "api_key", None) or os.getenv("API_KEY") or "dev-secret")
    if expected and x_api_key != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid api key")



def auth(x_api_key: Optional[str] = Header(None)):
    import os  # local import: global olmasa da garanti
    # Öncelik: settings.api_key -> env(API_KEY) -> "dev-secret"
    expected = (getattr(settings, "api_key", None) or os.getenv("API_KEY") or "dev-secret")
    if expected and x_api_key != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid api key")

