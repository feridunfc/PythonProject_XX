#!/usr/bin/env python3
# bootstrap-v4-ollama.py
# Unpacks multi_ai_v4_ollama_package.zip into the current repo root and prints next steps.
import zipfile, pathlib, sys

def main():
    here = pathlib.Path(__file__).resolve().parent
    z = here / "multi_ai_v4_ollama_package.zip"
    if not z.exists():
        print("multi_ai_v4_ollama_package.zip bulunamadı (aynı klasörde olmalı)."); sys.exit(1)
    with zipfile.ZipFile(z, "r") as zf:
        zf.extractall(here)
    print("✅ v4.0-ollama dosyaları açıldı.")
    print("Sonraki adımlar:")
    print("  pip install -r requirements.txt")
    print("  python -m multi_ai_v4_ollama.main")
    print("  streamlit run multi_ai_v4_ollama/dashboard/streamlit_app.py")

if __name__ == "__main__":
    main()
