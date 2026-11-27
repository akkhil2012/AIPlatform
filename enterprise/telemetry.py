"""OpenTelemetry OTLP traces with FastAPI instrumentation."""
import os
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor,ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

_initialized=False

def setup_telemetry(app):
    global _initialized
    if not _initialized:
        provider=TracerProvider(resource=Resource.create({"service.name":os.getenv("OTEL_SERVICE_NAME","aiplatform-api")}))
        endpoint=os.getenv("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT")
        if endpoint: provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint)))
        else: provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
        trace.set_tracer_provider(provider)
        _initialized=True
    FastAPIInstrumentor.instrument_app(app)
