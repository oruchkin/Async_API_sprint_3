import logging

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.semconv.resource import ResourceAttributes

from .settings import JaegerSettings

logger = logging.getLogger(__name__)


jaeger_settings = JaegerSettings()  # type: ignore
def configure_tracer(app: FastAPI) -> None:
    logger.warn(f"Connecting Jaeger to {jaeger_settings.host}:{jaeger_settings.port}")
    trace.set_tracer_provider(TracerProvider(resource=Resource({ResourceAttributes.SERVICE_NAME: "idp-api"})))
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name=jaeger_settings.host,
                agent_port=jaeger_settings.port,
            )
        )
    )
    # Чтобы видеть трейсы в консоли
    # trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    FastAPIInstrumentor.instrument_app(app)
