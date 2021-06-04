import typing

from fastapi_tools.middlewares import SimpleBaseMiddleware
from opentracing.ext import tags
from opentracing.propagation import Format
from starlette.requests import Request
from starlette.responses import Response
from . import tracer
RequestResponseEndpoint = typing.Callable[[Request], typing.Awaitable[Response]]
DispatchFunction = typing.Callable[
    [Request, RequestResponseEndpoint], typing.Awaitable[Response]
]


class OpenTracingMiddleware(SimpleBaseMiddleware):
    _extra_headers = [
        # All applications should propagate x-request-id. This header is
        # included in access log statements and is used for consistent trace
        # sampling and log sampling decisions in Istio.
        'x-request-id',

        # Lightstep tracing header. Propagate this if you use lightstep tracing
        # in Istio (see
        # https://istio.io/latest/docs/tasks/observability/distributed-tracing/lightstep/)
        # Note: this should probably be changed to use B3 or W3C TRACE_CONTEXT.
        # Lightstep recommends using B3 or TRACE_CONTEXT and most application
        # libraries from lightstep do not support x-ot-span-context.
        'x-ot-span-context',

        # Datadog tracing header. Propagate these headers if you use Datadog
        # tracing.
        'x-datadog-trace-id',
        'x-datadog-parent-id',
        'x-datadog-sampling-priority',

        # W3C Trace Context. Compatible with OpenCensusAgent and Stackdriver Istio
        # configurations.
        'traceparent',
        'tracestate',

        # Cloud trace context. Compatible with OpenCensusAgent and Stackdriver Istio
        # configurations.
        'x-cloud-trace-context',

        # Grpc binary trace context. Compatible with OpenCensusAgent nad
        # Stackdriver Istio configurations.
        'grpc-trace-bin',

        # b3 trace headers. Compatible with Zipkin, OpenCensusAgent, and
        # Stackdriver Istio configurations. Commented out since they are
        # propagated by the OpenTracing tracer above.
        # 'x-b3-traceid',
        # 'x-b3-spanid',
        # 'x-b3-parentspanid',
        # 'x-b3-sampled',
        # 'x-b3-flags',

        # Application-specific headers to forward.
        'user-agent',
        'x-weike-forward',
    ]

    async def before_request(self, request: Request) -> [Response, None]:
        try:
            # Create a new span context, reading in values (traceid,
            # spanid, etc) from the incoming x-b3-*** headers.
            span_ctx = tracer.extract(
                Format.HTTP_HEADERS,
                dict(request.headers)
            )
            # Note: this tag means that the span will *not* be
            # a child span. It will use the incoming traceid and
            # spanid. We do this to propagate the headers verbatim.
            rpc_tag = {tags.SPAN_KIND: tags.SPAN_KIND_RPC_SERVER}
            span = tracer.start_span(
                operation_name='op', child_of=span_ctx, tags=rpc_tag
            )
        except Exception as e:
            # We failed to create a context, possibly due to no
            # incoming x-b3-*** headers. Start a fresh span.
            # Note: This is a fallback only, and will create fresh headers,
            # not propagate headers.
            span = tracer.start_span('op')
            # Keep this in sync with the headers in details and reviews.
        extra_headers = {}

        for ihdr in self._extra_headers:
            val = request.headers.get(ihdr)
            if val is not None:
                extra_headers[ihdr] = val
                
        scope = tracer.scope_manager.activate(span, False)
        setattr(span, 'extra_headers', extra_headers)

    async def after_request(self, request: Request):
        scope = tracer.scope_manager.active
        if scope:
            scope.close()
