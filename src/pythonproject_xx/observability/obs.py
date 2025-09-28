# src/pythonproject_xx/observability/obs.py
import os, json, time, threading, contextlib
from typing import Dict, Any, Optional

# OTel isteğe bağlı; yoksa JSONL ile devam
_HAS_OTEL = False
try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    _HAS_OTEL = True
except Exception:
    pass

def _utc() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

class ObservabilityHub:
    def __init__(self) -> None:
        self.backends = [s.strip() for s in os.getenv("OBS_BACKENDS","jsonl").split(",") if s.strip()]
        self.service  = os.getenv("TRACE_SERVICE_NAME","pythonproject_xx")
        self.jsonl    = os.getenv("TRACE_JSONL_PATH","trace_log.jsonl")
        self._lock    = threading.Lock()
        self._tracer  = None

        if "otel" in self.backends and _HAS_OTEL:
            endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT","http://localhost:4318")
            provider = TracerProvider(resource=Resource.create({"service.name": self.service}))
            provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint)))
            trace.set_tracer_provider(provider)
            self._tracer = trace.get_tracer(self.service)

    def _write_jsonl(self, rec: Dict[str, Any]) -> None:
        if "jsonl" not in self.backends:
            return
        with self._lock:
            with open(self.jsonl, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    @contextlib.contextmanager
    def span(self, name: str, attrs: Optional[Dict[str, Any]] = None):
        start = time.time()
        otel_cm = None
        if self._tracer is not None:
            otel_cm = self._tracer.start_as_current_span(name)
            span = otel_cm.__enter__()
            if attrs:
                for k, v in attrs.items():
                    try:
                        span.set_attribute(k, v)
                    except Exception:
                        pass
        try:
            yield
        finally:
            dur = time.time() - start
            self._write_jsonl({
                "ts": _utc(), "service": self.service, "type": "span",
                "name": name, "duration_s": round(dur, 6), "attrs": attrs or {}
            })
            if otel_cm is not None:
                otel_cm.__exit__(None, None, None)

    def event(self, name: str, attrs: Optional[Dict[str, Any]] = None) -> None:
        self._write_jsonl({
            "ts": _utc(), "service": self.service, "type": "event",
            "name": name, "attrs": attrs or {}
        })

# Tekil hub
obs = ObservabilityHub()