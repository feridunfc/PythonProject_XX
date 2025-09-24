# feridunfc_meta_ai/utils/file_utils.py
from pathlib import Path
from typing import Union

PathLike = Union[str, Path]

def ensure_dir(path: PathLike) -> str:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return str(p)

def write_text(path: PathLike, content: str, encoding: str = "utf-8") -> str:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding=encoding)
    return str(p)
