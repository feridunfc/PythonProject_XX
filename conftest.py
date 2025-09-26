import sys, pathlib

ROOT = pathlib.Path(__file__).parent.resolve()
# src ve workdir'i en başa ekle (çakışma riskini azaltır)
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "workdir")]