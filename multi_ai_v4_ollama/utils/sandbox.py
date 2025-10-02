import docker, tempfile, os

def run_in_sandbox(code: str, timeout: int = 30):
    client = docker.from_env()
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code); path = f.name
    try:
        out = client.containers.run(
            "python:3.11-slim",
            f"python /tmp/{os.path.basename(path)}",
            volumes={path: {'bind': f'/tmp/{os.path.basename(path)}', 'mode': 'ro'}},
            network_mode="none", mem_limit="200m",
            read_only=True, remove=True, stdout=True, stderr=True, detach=False
        )
        return True, out.decode("utf-8")
    except Exception as e:
        return False, str(e)
    finally:
        os.unlink(path)
