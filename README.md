![CI](https://github.com/feridunfc/PythonProject_XX/actions/workflows/ci.yml/badge.svg?branch=main)

# feridunfc_meta_ai (secure MVP 0.4.0)

Bu sürüm; **async + retry** AI çağrıları, **DAG + concurrency** scheduler,
**Docker sandbox** (opsiyonel), **feedback loop**, **SQLite persist** ve
**dinamik model routing** içerir.

> Sandbox default **subprocess** ile çalışır. Güvende çalıştırmak için `USE_DOCKER=true`
> ve host'ta Docker kurulu olmalıdır.

## CLI
```bash
python -m feridunfc_meta_ai.cli run   -r "Basit TODO API: kullanıcı, görev ekle/listele"   --workdir ./workdir   --max-retries 2   -o ./out
```

## API
```bash
uvicorn feridunfc_meta_ai.api.main:app --reload
```

Auth: `X-API-Key: dev-secret` (ya da `.env` ile değiştirin)


> Minor: trace report komutu eklendi.
## Quickstart (v0.8 skeleton)

1. \pip install -r v0_8/requirements.txt\
2. \cp v0_8/.env.example v0_8/.env\ ve **FORCE_PROVIDER=mock** ayarla
3. Test: \pytest -q v0_8/tests\



### Reporting & Integrations
- \pythonproject_xx.reporting.run_report.build_report_md('logs/trace.jsonl')\ ile Markdown rapor �retir.
- PR a�mak i�in \GITHUB_TOKEN\ ve \GITHUB_REPOSITORY\ ayarla (token yoksa no-op).
