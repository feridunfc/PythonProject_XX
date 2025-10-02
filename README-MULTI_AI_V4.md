# MULTI_AI v4.0 (Ollama + Ensemble + Human-in-the-loop)

## Kurulum
```bash
pip install -r requirements.txt
# Ollama modelleri
ollama pull llama3.1:8b
ollama pull deepseek-coder:6.7b
ollama pull qwen2.5:7b-instruct
ollama pull llama3.2:3b-instruct
```

## Çalıştırma
```bash
python -m multi_ai_v4_ollama.main
# veya dashboard
streamlit run multi_ai_v4_ollama/dashboard/streamlit_app.py
```
