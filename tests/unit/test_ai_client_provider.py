import os
os.environ.setdefault("FORCE_PROVIDER", "mock")

from pythonproject_xx.ai.ai_client import AIClient

def test_ai_client_mock():
    c = AIClient()  # default mock
    out = c.run("Hello world")
    assert isinstance(out["output"], str)
    assert out["output"].startswith("[MOCK]")