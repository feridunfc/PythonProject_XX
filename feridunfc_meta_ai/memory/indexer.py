from __future__ import annotations
from pathlib import Path
import re, json

WORD = re.compile(r"[A-Za-z0-9_]+")

class CodebaseIndexer:
    def __init__(self, root: str):
        self.root = Path(root)
        self.docs = {}   # path -> token list
        self.vocab = set()

    def _tokens(self, text: str):
        return [w.lower() for w in WORD.findall(text)]

    def index(self, exts=(".py", ".md", ".txt")):
        for p in self.root.rglob("*"):
            if p.suffix.lower() in exts and p.is_file():
                try:
                    t = p.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    continue
                toks = self._tokens(t)
                if toks:
                    rel = str(p.relative_to(self.root))
                    self.docs[rel] = toks
                    self.vocab.update(toks)
        return self

    def dump(self, out_path: str):
        Path(out_path).write_text(json.dumps({"root": str(self.root), "docs": self.docs}), encoding="utf-8")

    @staticmethod
    def load(path: str) -> "CodebaseIndexer":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        idx = CodebaseIndexer(data["root"])
        idx.docs = {k: v for k, v in data["docs"].items()}
        idx.vocab = set(t for toks in idx.docs.values() for t in toks)
        return idx
