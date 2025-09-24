from __future__ import annotations
from collections import Counter
import math, re
from .indexer import CodebaseIndexer

WORD = re.compile(r"[A-Za-z0-9_]+")

def _tf(tokens):
    c = Counter(tokens)
    total = sum(c.values())
    return {k: v/total for k, v in c.items()} if total else {}

def _cos(a, b):
    dot = sum(a.get(k,0.0)*b.get(k,0.0) for k in set(a)|set(b))
    na = math.sqrt(sum(v*v for v in a.values()))
    nb = math.sqrt(sum(v*v for v in b.values()))
    return (dot / (na*nb)) if na and nb else 0.0

class Retriever:
    def __init__(self, index: CodebaseIndexer):
        self.index = index
        self.doc_tfs = {path: _tf(toks) for path, toks in index.docs.items()}

    def retrieve(self, query: str, k: int = 5):
        q_toks = [w.lower() for w in WORD.findall(query)]
        qtf = _tf(q_toks)
        scored = [(path, _cos(qtf, tf)) for path, tf in self.doc_tfs.items()]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:k]
