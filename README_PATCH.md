# MULTI_AI Patch — Plan & Execute + Trace + Env

Bu paket, MULTI_AI köküne **üzerine yaz (overwrite)** uygulanacak minimal bir yamadır.

## İçerik
- `.env.example` — örnek anahtarlar
- `requirements.txt` — güncel bağımlılıklar
- `.gitignore` — güvenli girdiler eklendi
- `config/agent_config.py` — rol→model eşlemesi
- `utils/ai_client.py` — OpenAI/Anthropic + retry + mock
- `utils/trace_manager.py` — JSONL trace
- `utils/trace_reporter.py` — HTML rapor (f-string ile güvenli)
- `agents/codegen.py` — Plan & Execute
- `orchestrator.py` — basit pipeline + trace + rapor

## Kurulum
```powershell
# kökte .env oluştur
Copy-Item .env.example .env
# en az bir anahtar girin veya FORCE_PROVIDER=mock kullanın
pip install -r requirements.txt
python orchestrator.py --spec "Basit TODO API: kullanıcı, görev ekle/listele" --report
```

Çıktılar:
- `trace_log.jsonl`
- `trace_report.html`

> Not: Anahtar yoksa `FORCE_PROVIDER=mock` ile mock cevaplara düşer.
