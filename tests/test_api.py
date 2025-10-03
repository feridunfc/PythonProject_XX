import pytest
from httpx import AsyncClient
import httpx
from feridunfc_meta_ai.api.main import app

@pytest.mark.anyio
async def test_api_flow():
    headers = {"X-API-Key":"dev-secret"}
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post("/sprints", json={"requirements":"Mini API"}, headers=headers)
        assert r.status_code == 200, r.text
        sid = r.json()["sprint_id"]
        r = await ac.post(f"/sprints/{sid}/execute", headers=headers); assert r.status_code == 200
        r = await ac.get(f"/sprints/{sid}/report", headers=headers); assert r.status_code == 200
