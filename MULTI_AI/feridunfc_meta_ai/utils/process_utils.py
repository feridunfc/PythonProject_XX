# feridunfc_meta_ai/utils/process_utils.py
import asyncio, logging
logger = logging.getLogger(__name__)

async def run_cmd(cmd, cwd=None, timeout=60):
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd, cwd=cwd,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
        )
        try:
            out, _ = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            return 124, "TIMEOUT"
        return proc.returncode, out.decode(errors="replace")
    except Exception as e:
        logger.exception("run_cmd failed")
        return 1, f"ERROR: {e}"
