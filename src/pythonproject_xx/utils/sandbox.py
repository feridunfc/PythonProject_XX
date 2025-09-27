from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
import os, tempfile, subprocess, pathlib, shutil

@dataclass
class RunResult:
    returncode: Optional[int]
    stdout: str
    stderr: str
    cmd: List[str]
    dry_run: bool

def docker_available() -> bool:
    try:
        subprocess.run(["docker", "--version"], capture_output=True, text=True, timeout=2)
        return True
    except Exception:
        return False

class SandboxRunner:
    """
    Basit Docker sandbox:
      - network off (default)
      - mem/cpu limitleri env'den: SANDBOX_MEM_LIMIT, SANDBOX_CPU_SHARES
      - dry-run: SANDBOX_DRY_RUN=1 olduğunda komut çalıştırılmaz, sadece geri verilir.
    """
    def __init__(
        self,
        image: str = "python:3.12-slim",
        network_disabled: bool = True,
        mem_limit: Optional[str] = os.getenv("SANDBOX_MEM_LIMIT"),
        cpu_shares: Optional[int] = int(os.getenv("SANDBOX_CPU_SHARES", "0")) or None,
    ) -> None:
        self.image = image
        self.network_disabled = network_disabled
        self.mem_limit = mem_limit
        self.cpu_shares = cpu_shares

    def _docker_base(self) -> List[str]:
        cmd = ["docker", "run", "--rm"]
        if self.network_disabled:
            cmd += ["--network", "none"]
        if self.mem_limit:
            cmd += ["-m", self.mem_limit]
        if self.cpu_shares:
            cmd += ["--cpu-shares", str(self.cpu_shares)]
        return cmd

    def run_python(self, code: str, timeout_s: int = 15) -> RunResult:
        # temp dosyaya yaz, read-only mount et
        tmpdir = pathlib.Path(tempfile.mkdtemp(prefix="sbx_"))
        try:
            (tmpdir / "main.py").write_text(code, encoding="utf-8")
            mount = f"{tmpdir}:/app:ro"
            cmd = self._docker_base() + ["-v", mount, self.image, "python", "-u", "/app/main.py"]

            dry = os.getenv("SANDBOX_DRY_RUN") == "1"
            if dry:
                return RunResult(None, "", "", cmd, True)

            if not docker_available():
                return RunResult(None, "", "docker not available", cmd, False)

            try:
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_s)
                return RunResult(proc.returncode, proc.stdout, proc.stderr, cmd, False)
            except subprocess.TimeoutExpired:
                return RunResult(None, "", f"timeout after {timeout_s}s", cmd, False)
        finally:
            # güvenlik: dosyaları temizle
            shutil.rmtree(tmpdir, ignore_errors=True)