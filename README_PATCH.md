
# MULTI_AI Full Patch (RAG + Plan&Execute + Scheduler + Trace + Dashboard)

## Kurulum
1) ZIP'i repo köküne açın (üzerine yazabilirsiniz).
2) Gerekli paketler:
    ```bash
    pip install -r requirements.txt
    pip install -r requirements.extra.txt   # RAG & Dashboard için
    ```
3) .env
    ```
    FORCE_PROVIDER=gemini
    AI_ALLOW_MOCK=1
    AI_RETRY_429=0
    GEMINI_API_KEY=...   # veya OPENAI_API_KEY / DEEPSEEK_API_KEY
    RAG_ENABLED=1
    EMBED_MODEL=all-MiniLM-L6-v2
    ```

## RAG İndeksleme
```python
from feridunfc_meta_ai.memory.rag import index_codebase
index_codebase(workdir=".")
```

## Trace Raporu
```bash
python -c "from feridunfc_meta_ai.utils.trace_reporter import generate_html_report as g; g()"
start trace_report.html
```

## Dashboard
```bash
streamlit run feridunfc_meta_ai/web/dashboard.py
```

## Orchestrator (örnek akış)
```python
import anyio
from feridunfc_meta_ai.orchestrator.sprint_orchestrator import SprintOrchestrator

async def main():
    orch = SprintOrchestrator(concurrency=2)
    await orch.initialize(workdir=".")
    await orch.plan_sprint_from_requirements("Basit TODO API: kullanıcı, görev ekle/listele")
    res = await orch.execute_sprint(max_workers=2)
    print(res)
    await orch.aclose()

anyio.run(main)
```
