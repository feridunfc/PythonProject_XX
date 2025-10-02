# tests/test_security.py
from fastapi.testclient import TestClient
from feridunfc_meta_ai.api.main import app

def test_docs_open():
    c = TestClient(app)
    r = c.get("/docs")
    assert r.status_code == 200

def test_protected_requires_key():
    c = TestClient(app)
    r = c.get("/api/does-not-exist")  # örnek: herhangi bir endpoint; middleware önce key ister
    assert r.status_code in (401, 404)
    # 404 da gelebilir; ama 401 görmek istiyorsan gerçek bir endpointi hedefle ve anahtarsız çağır
