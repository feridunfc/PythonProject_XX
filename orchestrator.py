import os
import uuid
import argparse
import logging

from dotenv import load_dotenv
load_dotenv()

from utils.trace_manager import log_trace
from utils.trace_reporter import generate_html_report

# Var olan dosyaları değiştirmiyoruz: architect.py, critic.py, tester.py
# Hepsinde `class Agent` ve `handle(context)` arayüzü olduğunu varsayıyoruz.
from agents.architect import ArchitectAgent
from agents.codegen import CodegenAgent   # Plan & Execute sürümü (bu patch ile gelir)
from agents.critic import CriticAgent
from agents.tester import TesterAgent

logging.basicConfig(level=getattr(logging, os.getenv("LOG_LEVEL","INFO").upper(), logging.INFO))
logger = logging.getLogger("orchestrator")

class Orchestrator:
    def __init__(self):
        self.architect = ArchitectAgent(model=os.getenv("ARCHITECT_MODEL","gpt-4o-mini"))
        self.codegen = CodegenAgent(model=os.getenv("CODEGEN_MODEL","gpt-4o-mini"))
        self.critic = CriticAgent(model=os.getenv("CRITIC_MODEL","gpt-4o-mini"))
        self.tester = TesterAgent(model=os.getenv("TESTER_MODEL","gpt-4o-mini"))

    def run(self, spec: str, make_report: bool = False):
        task_id = str(uuid.uuid4())
        ctx = {"task_id": task_id, "spec": spec}

        logger.info("Pipeline start task_id=%s", task_id)
        # 1) Mimari
        arch = self.architect.handle(ctx)
        log_trace("ArchitectAgent", task_id, ctx, arch)

        # 2) Kod üretimi (plan & execute)
        code = self.codegen.handle({**ctx, **arch})
        log_trace("CodegenAgent", task_id, arch, code)

        # 3) Eleştiri
        critique = self.critic.handle({**ctx, **code})
        log_trace("CriticAgent", task_id, code, critique)

        # 4) Test
        test_res = self.tester.handle({**ctx, **code})
        log_trace("TesterAgent", task_id, code, test_res)

        logger.info("Pipeline finished task_id=%s", task_id)

        if make_report:
            try:
                generate_html_report()
            except FileNotFoundError:
                logger.warning("Trace file not found for report generation. Skipping.")
        return {"task_id": task_id, "arch": arch, "code": code, "critique": critique, "test": test_res}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True, help="İş tanımı / gereksinim")
    ap.add_argument("--report", action="store_true", help="Çalışma sonunda HTML trace raporu üret")
    args = ap.parse_args()

    orch = Orchestrator()
    res = orch.run(args.spec, make_report=args.report)
    print("DONE:", res["task_id"])

if __name__ == "__main__":
    main()
