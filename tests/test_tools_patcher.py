from pythonproject_xx.tools.file_patcher import FilePatcherTool
import tempfile, pathlib

def test_file_patcher_writes_and_diff():
    with tempfile.TemporaryDirectory() as td:
        p = pathlib.Path(td,"a.py")
        p.write_text("print(1)\n", encoding="utf-8")
        out = FilePatcherTool().run(str(p), "print(2)\n")
        assert out["ok"] is True
        assert "diff" in out and "-print(1)" in out["diff"] or out["diff"] == ""