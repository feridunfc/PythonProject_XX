from __future__ import annotations

import os
import re
from typing import Dict, List, Set

# Basit ve hızlı sezgisel toplayıcı.
# Ortam değişkenleri ile sınırlar:
MAX_FILES = int(os.getenv("CONTEXT_MAX_FILES", "12"))
MAX_BYTES = int(os.getenv("CONTEXT_FILE_MAX_BYTES", "65536"))  # 64 KB
ALLOWED_EXTS = set(
    (os.getenv("CONTEXT_EXTS") or ".py,.md,.json,.toml,.yaml,.yml,.ini,.cfg,.txt")
    .lower()
    .split(",")
)

def _tokenize(text: str) -> List[str]:
    words = re.findall(r"[A-Za-z0-9_]+", (text or "").lower())
    return [w for w in words if len(w) >= 3]

def _score(relpath: str, keywords: Set[str]) -> int:
    s = relpath.lower()
    score = 0
    for k in keywords:
        if k in s:
            score += 2
    # belirli dosya adlarına küçük bonus
    base = os.path.basename(s)
    if base in {"readme.md", "pyproject.toml", "requirements.txt"}:
        score += 1
    return score

def collect_related_files(workdir: str, title: str = "", description: str = "") -> List[Dict[str, str]]:
    """
    workdir altını tarar, başlık/açıklamadan türetilen anahtar kelimelere göre
    en alakalı (ve küçük) dosyaları seçer; içeriklerini döndürür.
    """
    if not workdir or not os.path.isdir(workdir):
        return []

    # anahtar kelimeler
    kws = set(_tokenize(title) + _tokenize(description))
    results: List[Dict[str, str]] = []

    # aday dosyaları topla
    candidates: List[str] = []
    for root, _, files in os.walk(workdir):
        for fn in files:
            ext = os.path.splitext(fn)[1].lower()
            if ext not in ALLOWED_EXTS:
                continue
            full = os.path.join(root, fn)
            try:
                size = os.path.getsize(full)
            except OSError:
                continue
            if size <= MAX_BYTES:
                candidates.append(full)

    # skorla ve sırala
    def _rel(p: str) -> str:
        try:
            rp = os.path.relpath(p, workdir)
        except Exception:
            rp = p
        return rp.replace("\\", "/")

    ranked = sorted(
        candidates,
        key=lambda p: (_score(_rel(p), kws), -os.path.getsize(p)),
        reverse=True,
    )

    # seç ve oku
    for path in ranked[:MAX_FILES]:
        rel = _rel(path)
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except Exception:
            continue
        try:
            b = os.path.getsize(path)
        except OSError:
            b = len(content.encode("utf-8", "ignore"))

        results.append({
            "path": rel,
            "bytes": b,
            "content": content,
        })

    return results
