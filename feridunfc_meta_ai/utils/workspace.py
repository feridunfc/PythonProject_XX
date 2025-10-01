# feridunfc_meta_ai/utils/workspace.py
from __future__ import annotations
import os, uuid

def make_workspace(base_dir: str) -> str:
    """
    base_dir/.workspaces/<uuid> klasörünü oluşturur ve yolunu döndürür.
    """
    ws_root = os.path.join(base_dir, ".workspaces")
    os.makedirs(ws_root, exist_ok=True)
    ws = os.path.join(ws_root, uuid.uuid4().hex)
    os.makedirs(ws, exist_ok=True)
    return ws
