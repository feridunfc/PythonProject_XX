from pythonproject_xx.tools.linter import LinterTool

def test_linter_reports_issue_tmpfile():
    code = "x=1+1\n"
    out = LinterTool().run(code=code)
    assert "ok" in out and "issues" in out