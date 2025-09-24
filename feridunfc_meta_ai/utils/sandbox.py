import os, tempfile, shutil, logging, subprocess, json
from pathlib import Path
from ..config.settings import settings

logger = logging.getLogger(__name__)

def run_pytests(workdir: str, timeout: int = 180):
    """Run pytest safely. If USE_DOCKER=true, try dockerized run; else fallback to subprocess.
    Returns (code, stdout, stderr)
    """
    if settings.use_docker:
        try:
            return _run_docker(workdir, timeout)
        except Exception as e:
            logger.warning("Docker sandbox failed (%s); falling back to subprocess", e)
    return _run_subprocess(workdir, timeout)

def _run_subprocess(workdir: str, timeout: int):
    try:
        proc = subprocess.run(["pytest", "-q"], cwd=workdir, capture_output=True, text=True, timeout=timeout)
        return proc.returncode, proc.stdout, proc.stderr
    except Exception as e:
        return 1, "", str(e)

def _run_docker(workdir: str, timeout: int):
    # Lazy docker call via cli to avoid SDK dependency overhead in CI
    cmd = [
        "docker", "run", "--rm",
        "-v", f"{str(Path(workdir).resolve())}:/app",
        "-w", "/app",
        "--network", "none",
        "--memory", "512m",
        "python:3.11-slim",
        "bash", "-lc", "pip install -q pytest && pytest -q"
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return proc.returncode, proc.stdout, proc.stderr
