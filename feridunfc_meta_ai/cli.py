from __future__ import annotations

import argparse
import asyncio
import logging
from pathlib import Path

from .orchestrator.sprint_orchestrator import SprintOrchestrator


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="feridunfc_meta_ai.cli",
        description="Meta AI sprint planlama ve yürütme aracı"
    )
    p.add_argument("--requirements", type=str, required=True, help="Doğal dil gereksinimleri")
    p.add_argument("--workdir", type=str, default="workdir", help="Çalışma dizini")
    p.add_argument("--export-dir", type=str, default="out", help="Raporların yazılacağı dizin")
    p.add_argument("--log-level", type=str, default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    p.add_argument("--plan-only", action="store_true", help="Sadece plan üret, yürütme yapma")
    p.add_argument("--no-sandbox", action="store_true", help="Sandbox devre dışı (tehlikeli olabilir)")
    p.add_argument("--skip-tests", action="store_true", help="Test adımlarını atla")
    p.add_argument("--concurrency", type=int, default=1, help="Eşzamanlı görev sayısı")
    return p.parse_args()


async def _run() -> None:
    args = parse_args()

    # Logging
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    logger = logging.getLogger(__name__)

    # Dizinler
    workdir = Path(args.workdir)
    export_dir = Path(args.export_dir)
    workdir.mkdir(parents=True, exist_ok=True)
    export_dir.mkdir(parents=True, exist_ok=True)

    orch = SprintOrchestrator(concurrency=args.concurrency)

    try:
        await orch.initialize(
            workdir=str(workdir),
            no_sandbox=args.no_sandbox,
            skip_tests=args.skip_tests,
        )

        sprint = await orch.plan_sprint_from_requirements(args.requirements)
        # Plan özeti
        try:
            total = sprint.get_total_tasks()  # pydantic model/dc içinde mevcut
        except Exception:
            total = getattr(sprint, "total_tasks", None) or "?"
        print(f"Plan: {getattr(sprint, 'title', 'N/A')} / tasks={total}")

        # Rapor denemesi (modül fonksiyon isimleri projede değişken olabilir)
        try:
            from .utils import reporting as rep  # type: ignore

            # Esnek çağrılar: mevcut olanı dener
            called = False
            if hasattr(rep, "export_sprint_reports"):
                rep.export_sprint_reports(sprint, str(export_dir))  # type: ignore
                called = True
            else:
                if hasattr(rep, "save_sprint_excel"):
                    rep.save_sprint_excel(sprint, str(export_dir))  # type: ignore
                    called = True
                if hasattr(rep, "save_gantt_png"):
                    rep.save_gantt_png(sprint, str(export_dir))  # type: ignore
                    called = True

            if called:
                print(f"raporlar: {export_dir}\\sprint.xlsx, {export_dir}\\gantt.png")
        except Exception as e:
            logger.debug("Rapor yazımı atlandı/başarısız: %s", e)

        # Yürütme (istenirse)
        if not args.plan_only:
            try:
                # Projede yürütme adımı farklı isimde olabilir; yoksa sessiz geç
                if hasattr(orch, "execute_active_sprint"):
                    await orch.execute_active_sprint()  # type: ignore
                elif hasattr(orch, "run_active_sprint"):
                    await orch.run_active_sprint()  # type: ignore
            except Exception as e:
                logger.error("Yürütme sırasında hata: %s", e)

    finally:
        try:
            await orch.aclose()
        except Exception:
            pass


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()
