# utils/otel_tracer.py
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

def _get_exporter():
    try:
        # Tercih: HTTP
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        return OTLPSpanExporter()
    except Exception:
        # Geri düşüş: gRPC
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        return OTLPSpanExporter()

def init_tracer(service_name: str = "pythonproject_xx"):
    provider = TracerProvider()
    provider.add_span_processor(BatchSpanProcessor(_get_exporter()))
    trace.set_tracer_provider(provider)
    return trace.get_tracer(service_name)
