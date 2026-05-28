"""Optional Cloud Trace export via OpenTelemetry (Agent Observability analog).

No-op unless GOOGLE_CLOUD_PROJECT is set and the Cloud Trace exporter is available
(i.e., on Cloud Run). Never raises — tracing must not break the onboarding path.
"""

from __future__ import annotations

import contextlib
import os

_tracer = None
_init_done = False


def _tracer_or_none():
    global _tracer, _init_done
    if _init_done:
        return _tracer
    _init_done = True
    try:
        if not os.environ.get("GOOGLE_CLOUD_PROJECT"):
            return None
        from opentelemetry import trace
        from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        provider = TracerProvider()
        provider.add_span_processor(BatchSpanProcessor(CloudTraceSpanExporter()))
        trace.set_tracer_provider(provider)
        _tracer = trace.get_tracer("cpoa")
    except Exception:  # noqa: BLE001
        _tracer = None
    return _tracer


@contextlib.contextmanager
def span(name: str, **attributes):
    """Start a Cloud Trace span (or a no-op context if tracing is unavailable)."""
    tracer = _tracer_or_none()
    if tracer is None:
        yield None
        return
    with tracer.start_as_current_span(name) as s:
        with contextlib.suppress(Exception):
            for k, v in attributes.items():
                s.set_attribute(k, v)
        yield s
