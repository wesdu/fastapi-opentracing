__name__ = "fastapi_opentracing"
from jaeger_client import Tracer, ConstSampler
from jaeger_client.reporter import NullReporter
from jaeger_client.codecs import B3Codec
from opentracing.scope_managers.contextvars import ContextVarsScopeManager
from opentracing.propagation import Format
from jaeger_client import Config
import os
# tracer = Tracer(
#     one_span_per_rpc=True,
#     service_name='wk_api_gateway',
#     reporter=NullReporter(),
#     sampler=ConstSampler(decision=True),
#     extra_codecs={Format.HTTP_HEADERS: B3Codec()},
#     scope_manager=ContextVarsScopeManager(),
# )

project_name = os.getenv("PROJECT_NAME", "PROJECT_NAME")
namespace = os.getenv("NAMESPACE", "NAMESPACE")

config = Config(
    config={  
        "sampler": {
            "type": "const",
            "param": 1
        },
        "logging": False,
        "reporter_queue_size": 2000,
        "propagation": "b3", # Compatible with istio
        "generate_128bit_trace_id": True, # Compatible with istio
    },
    service_name=f"{project_name}.{namespace}", # deployment.yaml will set this env for each service
    scope_manager=ContextVarsScopeManager(),
    validate=True,
)

tracer = config.initialize_tracer()

async def get_opentracing_span_headers():
    scope = tracer.scope_manager.active
    carrier = {}
    if scope is not None:
        span = scope.span
        tracer.inject(
            span_context=span,
            format=Format.HTTP_HEADERS,
            carrier=carrier)
        for k, v in getattr(span, 'extra_headers', {}).items():
            carrier[k] = v
    return carrier

async def get_current_span():
    scope = tracer.scope_manager.active
    if scope is not None:
        return scope.span
    return None

def sync_get_current_span():
    scope = tracer.scope_manager.active
    if scope is not None:
        return scope.span
    return None