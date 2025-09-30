from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
import os

_service = os.getenv("TRACE_SERVICE_NAME", "pythonproject_xx")
_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")

def init_tracer() -> None:
    provider = TracerProvider(resource=Resource.create({"service.name": _service}))
    exporter = OTLPSpanExporter(endpoint=f"{_endpoint}/v1/traces")
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

def get_tracer(name: str = __name__):
    return trace.get_tracer(name)