![CI](https://github.com/feridunfc/PythonProject_XX/actions/workflows/ci.yml/badge.svg?branch=main)

# feridunfc_meta_ai (secure MVP 0.4.0)

Bu sÃ¼rÃ¼m; **async + retry** AI Ã§aÄŸrÄ±larÄ±, **DAG + concurrency** scheduler,
**Docker sandbox** (opsiyonel), **feedback loop**, **SQLite persist** ve
**dinamik model routing** iÃ§erir.

> Sandbox default **subprocess** ile Ã§alÄ±ÅŸÄ±r. GÃ¼vende Ã§alÄ±ÅŸtÄ±rmak iÃ§in `USE_DOCKER=true`
> ve host'ta Docker kurulu olmalÄ±dÄ±r.

## CLI
```bash
python -m feridunfc_meta_ai.cli run   -r "Basit TODO API: kullanÄ±cÄ±, gÃ¶rev ekle/listele"   --workdir ./workdir   --max-retries 2   -o ./out
```

## API
```bash
uvicorn feridunfc_meta_ai.api.main:app --reload
```

Auth: `X-API-Key: dev-secret` (ya da `.env` ile deÄŸiÅŸtirin)


> Minor: trace report komutu eklendi.
## Quickstart (v0.8 skeleton)

1. \pip install -r requirements.txt\
2. \cp .env.example .env\ ve **FORCE_PROVIDER=mock** ayarla
3. Test: \PYTHONPATH=src pytest -q\

