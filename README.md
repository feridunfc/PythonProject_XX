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
