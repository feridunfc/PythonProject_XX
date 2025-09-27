# Architecture 2.0 – Meta AI Orchestrator (MVI)

Bileşenler:
- **AI Client (providers/)**: `mock`, `openai` adapter; `FORCE_PROVIDER` ile zorunlu seçici.
- **Agents (BaseAgent)**: rollere model ataması `Router` ile.
- **Scheduler (DAG)**: `topo_sort` + döngü tespiti.
- **Trace**: JSONL append (`logs/trace.jsonl`).
- **State**: Basit JSON state.
Genişletme: sandbox (Docker), integrator (gh/PyGithub), feedback loop, async/concurrency.