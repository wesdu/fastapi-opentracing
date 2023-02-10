from fastapi_opentracing.client_hooks._db_span import redis_span_high_level
from fastapi_opentracing.client_hooks._const import REDIS
from typing import Optional

from fastapi_opentracing import get_current_span, sync_get_current_span
from fastapi_opentracing import tracer

try:
    import aioredis
    from aioredis import client
except ImportError:
    pass
else:
    _execute_command = aioredis.Redis.execute_command
    _pipeline = aioredis.Redis.pipeline
    _pipeline_execute = client.Pipeline.execute

try:
    import ujson as json
except Exception:
    import json


async def excute_command_wrapper(self, *args, **kwargs):
    span = await get_current_span()
    if span is None:
        return await _execute_command(self, *args, **kwargs)
    try:
        cmd = args[0]
        statement = json.dumps(dict(cmd=cmd, args=list(map(str, args[1:]))))
    except Exception as e:
        print(f"opentracing-error {repr(e)}")
        return await _execute_command(self, *args, **kwargs)
    else:
        with await redis_span_high_level(
            self,
            span=span,
            operation=cmd,
            statement=statement,
            db_instance=REDIS,
        ):
            return await _execute_command(self, *args, **kwargs)


def pipeline_wrapper(
    self, transaction: bool = True, shard_hint: Optional[str] = None
):
    pipe = _pipeline(self, transaction, shard_hint)
    span = sync_get_current_span()
    pipe._span = tracer.start_span(operation_name="PIPELINE", child_of=span)
    return pipe


async def pipeline_execute_wrapper(self, raise_on_error: bool = True):
    response = await _pipeline_execute(self, raise_on_error)
    if self._span:
        self._span.finish()
    return response


def install_patch():
    aioredis.Redis.execute_command = excute_command_wrapper
    aioredis.Redis.pipeline = pipeline_wrapper
    client.Pipeline.execute = pipeline_execute_wrapper
