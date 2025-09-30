import subprocess, shlex, os, tempfile, json, uuid

class SandboxResult(dict):
    pass

def run_python(code: str, timeout: int = 60) -> SandboxResult:
    img = os.getenv("SANDBOX_IMAGE", "python:3.11-slim")
    name = f"sbox-{uuid.uuid4().hex[:8]}"
    with tempfile.TemporaryDirectory() as tmp:
        code_path = os.path.join(tmp, "main.py")
        with open(code_path, "w", encoding="utf-8") as f:
            f.write(code)

        cmd = [
            "docker","run","--rm","--name",name,
            "--network","none",
            "--pids-limit","128",
            "--memory","256m","--memory-swap","256m",
            "--cpus","1.0",
            "--cap-drop=ALL",
            "--security-opt","no-new-privileges:true",
            "--read-only",
            "--tmpfs","/tmp:rw,noexec,nosuid,size=100m",
            "--security-opt","seccomp=unconfined",   # prod: custom json profil varsayımıyla değiştir
            "--security-opt","apparmor=docker-default",
            "-v", f"{code_path}:/app/main.py:ro",
            "-w","/app", img, "python","-u","/app/main.py"
        ]
        try:
            out = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return SandboxResult(code=out.returncode, stdout=out.stdout, stderr=out.stderr, container=name)
        except subprocess.TimeoutExpired as e:
            return SandboxResult(code=124, stdout=e.stdout or "", stderr="TIMEOUT")