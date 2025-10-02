import subprocess, tempfile, os

def _run_cmd(cmd, cwd=None, timeout=60):
    p = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        out, _ = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        p.kill(); out = "TIMEOUT"
    return p.returncode, out

def evaluate_code(candidate_code: str) -> dict:
    with tempfile.TemporaryDirectory() as td:
        fp = os.path.join(td, "candidate.py")
        with open(fp, "w") as f: f.write(candidate_code)

        # Minimal test to ensure import works
        with open(os.path.join(td, "test_dummy.py"), "w") as f:
            f.write("def test_import():\n import candidate\n assert True\n")

        rc_py, out_py = _run_cmd(["pytest", "-q", "--maxfail=1", "--disable-warnings", td])
        rc_ruff, out_ruff = _run_cmd(["ruff", "--format", "text", td])
        rc_mypy, out_mypy = _run_cmd(["mypy", td])

        tests_passed = (rc_py == 0)
        lint_ok = (rc_ruff == 0)
        type_ok = (rc_mypy == 0)
        final = (tests_passed * 0.6) + (lint_ok * 0.2) + (type_ok * 0.2)
        return {
            "tests_passed": tests_passed,
            "lint_ok": lint_ok,
            "type_ok": type_ok,
            "final_score": final,
            "logs": {"pytest": out_py[-2000:], "ruff": out_ruff[-2000:], "mypy": out_mypy[-2000:]}
        }
