import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    root = logging.getLogger()
    if root.handlers:
        return
    root.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    ch = logging.StreamHandler(); ch.setFormatter(fmt); root.addHandler(ch)
    fh = RotatingFileHandler("meta_ai.log", maxBytes=1_000_000, backupCount=2); fh.setFormatter(fmt); root.addHandler(fh)
