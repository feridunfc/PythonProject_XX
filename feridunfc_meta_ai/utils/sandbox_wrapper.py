# feridunfc_meta_ai/utils/sandbox_wrapper.py
from __future__ import annotations
import os, sys, subprocess, tempfile

try:
    # varsa mevcut Docker sandbox implementasyonunu kullan
    from .sandbox import run_code_in_sandbox  # type: ignore
except Exception:  # pragma: no cover
    def run_code_in_sandbox(code: str):
        raise NotImplementedError("Docker sandbox is not available")

def run_code_safely(code: str):
    """
    Basit ve sınırlı bir subprocess fallback.
    - -I: isolated mode
    - -B: bytecode yazma yok
    - timeout: 10s
    """
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "snippet.py")
        with open(path, "w", encoding="utf-8") as f:
            f.write(code)
        p = subprocess.run(
            [sys.executable, "-I", "-B", path],
            capture_output=True, text=True, timeout=10
        )
        return p.returncode, (p.stdout or "") + (p.stderr or "")

def execute_code(code: str, use_docker: bool = True):
    """
    USE_DOCKER=true ise Docker sandbox; değilse subprocess fallback.
    """
    use_docker = os.getenv("USE_DOCKER", "false").lower() == "true" and use_docker
    try:
        if use_docker:
            return run_code_in_sandbox(code)
        return run_code_safely(code)
    except Exception as e:  # pragma: no cover
        return -1, f"Sandbox execution failed: {e}"
