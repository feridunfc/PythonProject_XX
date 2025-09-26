import tempfile, pathlib, py_compile, subprocess, sys
from typing import Tuple
class SandboxRunner:
    def __init__(self, allow_run=False, timeout_s=10):
        self.allow_run=allow_run; self.timeout_s=timeout_s
    def syntax_check(self, filename, content)->Tuple[int,str,str]:
        with tempfile.TemporaryDirectory() as td:
            p=pathlib.Path(td)/filename; p.write_text(content, encoding='utf-8')
            try:
                py_compile.compile(str(p), doraise=True); return 0,'OK',''
            except Exception as e:
                return 1,'',str(e)
    def run_python(self, filename, content)->Tuple[int,str,str]:
        if not self.allow_run: return 2,'','Execution disabled'
        with tempfile.TemporaryDirectory() as td:
            p=pathlib.Path(td)/filename; p.write_text(content, encoding='utf-8')
            try:
                proc=subprocess.run([sys.executable,str(p)],capture_output=True,text=True,timeout=self.timeout_s)
                return proc.returncode, proc.stdout, proc.stderr
            except Exception as e:
                return 3,'',str(e)
