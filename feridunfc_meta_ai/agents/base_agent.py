from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

try:
    from ..models.task import Task  # type: ignore
except Exception:  # pragma: no cover
    Task = Any  # type: ignore

logger = logging.getLogger(__name__)

class BaseAIAgent(ABC):
    """
    Tüm ajanlar için ortak taban sınıf.
    - process_task(task, context) alt sınıflarda uygulanır.
    - run(task, context) güvenli wrapper: status ve hata yönetimi sağlar.
    - Context Enrichment: codegen/tester görevleri için workdir içinden ilgili dosyaları toplar.
    """
    def __init__(self, client: Any, agent_type: str, name: Optional[str] = None) -> None:
        self.client = client
        self.agent_type = (agent_type or "").lower()
        self.name = name or self.__class__.__name__

    # --------- yardımcılar ---------
    def _safe_set_attr(self, obj: Any, key: str, value: Any) -> None:
        try:
            setattr(obj, key, value)
        except Exception:
            pass

    def _mark_status(self, task: Task, status: str) -> None:
        self._safe_set_attr(task, "status", status)

    def _attach_result(self, task: Task, result: Any) -> None:
        self._safe_set_attr(task, "result", result)

    # --------- ana akış ---------
    async def run(self, task: Task, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Güvenli yürütme sarmalayıcısı.
        - status: pending -> in_progress -> completed/failed
        - Hata durumunda yakalar, task.result içine error bilgisini yazar.
        - process_task çağrısından önce bağlamsal dosya toplama yapar (codegen/tester için).
        """
        ctx_in = context or {}
        self._mark_status(task, "in_progress")

        try:
            # --- Context Enrichment: ilgili dosyaları ekle ---
            ctx = dict(ctx_in)
            workdir = ctx.get("workdir")
            agent_kind = self.agent_type  # "codegen" | "tester" | ...

            if workdir and agent_kind in {"codegen", "tester"}:
                try:
                    from ..utils.context_collector import collect_related_files  # lokal import

                    files = collect_related_files(
                        workdir=workdir,
                        title=getattr(task, "title", "") or "",
                        description=getattr(task, "description", "") or "",
                    )
                    if files:
                        ctx["related_files"] = files
                        ctx["related_files_summary"] = [
                            {"path": f["path"], "bytes": f.get("bytes", 0)} for f in files
                        ]
                        logger.info(
                            "[%s] Context enriched: %d file(s) added for task '%s'",
                            self.name,
                            len(files),
                            getattr(task, "title", "") or getattr(task, "task_id", "") or "<no-title>",
                        )
                except Exception as e:
                    logger.warning("[%s] Context enrichment skipped: %s", self.name, e)

            # --- Asıl iş: alt sınıfın işini yap ---
            result: Dict[str, Any] = await self.process_task(task, ctx)

            if getattr(task, "status", None) not in {"completed", "failed"}:
                self._mark_status(task, "completed")

            if result is not None:
                self._attach_result(task, result)

            return result or {}

        except asyncio.CancelledError:
            self._mark_status(task, "failed")
            self._attach_result(task, {"error": "Task cancelled"})
            logger.exception("[%s] Task cancelled", self.name)
            raise

        except Exception as e:
            self._mark_status(task, "failed")
            self._attach_result(task, {"error": str(e)})
            logger.exception("[%s] Task failed: %s", self.name, e)
            return {"error": str(e)}

    @abstractmethod
    async def process_task(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        """Ajan-özgü iş mantığı."""
        ...

# Backward-compatibility alias
AIAgent = BaseAIAgent

