# feridunfc_meta_ai/api/dependencies.py
from fastapi import Header, HTTPException
import os

API_KEY = os.getenv("API_KEY", "dev-secret")

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
