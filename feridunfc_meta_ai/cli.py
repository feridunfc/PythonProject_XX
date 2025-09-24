# feridunfc_meta_ai/cli.py
import anyio, typer, logging
from pathlib import Path
from rich import print
from .orchestrator.sprint_orchestrator import SprintOrchestrator

app = typer.Typer(help="🚀 Sprint tabanlı Meta AI Orchestrator CLI")

@app.command()
def main(
    requirements: str = typer.Option(..., "--requirements", "-r"),
    workdir: str = typer.Option("./workdir", "--workdir"),
    max_retries: int = typer.Option(1, "--max-retries"),
    concurrency: int = typer.Option(1, "--concurrency"),
    export_dir: str = typer.Option("./out", "--export-dir", "-o"),
    plan_only: bool = typer.Option(False, "--plan-only", help="Sadece plan üret, yürütme yapma"),
    skip_tests: bool = typer.Option(False, "--skip-tests", help="TesterAgent test çalıştırmasın"),
    no_sandbox: bool = typer.Option(False, "--no-sandbox", help="Sandbox/Docker kullanma"),
    log_level: str = typer.Option("INFO", "--log-level", help="DEBUG/INFO/WARNING/ERROR"),
):
    logging.basicConfig(level=getattr(logging, log_level.upper(), logging.INFO),
                        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    export_dir = Path(export_dir); export_dir.mkdir(parents=True, exist_ok=True)
    workdir = Path(workdir); workdir.mkdir(parents=True, exist_ok=True)

    async def _run():
        orch = SprintOrchestrator(concurrency=concurrency)
        await orch.initialize(workdir=str(workdir), no_sandbox=no_sandbox, skip_tests=skip_tests)

        sprint = await orch.plan_sprint_from_requirements(requirements)
        print(f"Plan: {sprint.title} / tasks={sprint.get_total_tasks()}")

        if not plan_only:
            results = await orch.execute_sprint(max_retries=max_retries)
            report = orch.get_sprint_report()
            from .utils.reporting import ReportGenerator  # varsa
            rg = ReportGenerator(out_dir=str(export_dir))
            rg.export_to_excel(sprint, "sprint.xlsx")
            rg.generate_gantt_chart(sprint, "gantt.png")
            print(f"raporlar: {export_dir/'sprint.xlsx'}, {export_dir/'gantt.png'}")
        else:
            print("[yellow]Plan-only mod: yürütme atlandı.[/yellow]")

        await orch.aclose()

    anyio.run(_run)

if __name__ == "__main__":
    app()
