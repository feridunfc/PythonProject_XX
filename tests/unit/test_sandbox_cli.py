import os
import sys
import platform
from pythonproject_xx.utils.sandbox import SandboxRunner

def test_sandbox_builds_docker_cmd_dryrun(monkeypatch):
    monkeypatch.setenv("SANDBOX_DRY_RUN", "1")
    monkeypatch.setenv("SANDBOX_MEM_LIMIT", "64m")
    monkeypatch.delenv("SANDBOX_CPU_SHARES", raising=False)

    sbx = SandboxRunner()
    res = sbx.run_python('print("hello")')

    assert res.dry_run is True
    assert isinstance(res.cmd, list)
    # Komutta docker ve network none beklenir (default)
    assert "docker" in res.cmd[0]
    assert "--network" in res.cmd and "none" in res.cmd
    assert "-m" in res.cmd and "64m" in res.cmd

def test_sandbox_cpu_shares_flag(monkeypatch):
    monkeypatch.setenv("SANDBOX_DRY_RUN", "1")
    monkeypatch.setenv("SANDBOX_CPU_SHARES", "256")
    sbx = SandboxRunner()
    res = sbx.run_python('print("x")')
    assert "--cpu-shares" in res.cmd and "256" in res.cmd