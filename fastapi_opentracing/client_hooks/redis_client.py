from ._db_span import redis_span
from ._const import REDIS
import functools

from fastapi_opentracing import sync_get_current_span
from fastapi_opentracing import tracer

try:
    import aioredis
except ImportError:
    pass
else:
    _excute = aioredis.Redis.execute
    _pipeline = aioredis.Redis.pipeline
    _multi_exec = aioredis.Redis.multi_exec

try:
    import ujson as json
except Exception:
    import json

from aioredis.commands.transaction import _RedisBuffer


async def fut_done(span=None):
    if span:
        span.finish()


# Use the following function instead of add_done_callback()
async def add_success_callback(fut, callback):
    result = await fut
    await callback()
    return result


def excute_wrapper(self, command, *args, **kwargs):
    span = sync_get_current_span()
    if span is None:
        return _excute(self, command, *args, **kwargs)
    if isinstance(self._pool_or_conn, _RedisBuffer):
        return _excute(self, command, *args, **kwargs)
    try:
        cmd = (
            str(command, encoding="utf-8")
            if isinstance(command, bytes)
            else str(command)
        )
        statement = json.dumps(dict(cmd=cmd, args=list(map(str, args))))
    except Exception as e:
        print(f"opentracing-error {repr(e)}")
        return _excute(self, command, *args, **kwargs)
    else:
        exc_span = redis_span(
            self,
            span=span,
            operation=cmd,
            statement=statement,
            db_instance=REDIS,
        )
        fut = _excute(self, command, *args, **kwargs)
        fut = add_success_callback(fut, functools.partial(fut_done, exc_span))
        return fut


def multi_exec_wrapper(self):
    multi = _multi_exec(self)
    span = sync_get_current_span()
    multi._span = tracer.start_span(operation_name="MULTI_EXEC", child_of=span)
    return multi


def pipeline_wrapper(self):
    pipe = _pipeline(self)
    span = sync_get_current_span()
    pipe._span = tracer.start_span(operation_name="PIPELINE", child_of=span)
    return pipe


def _send_pipeline(self, conn):
    with conn._buffered():
        for fut, cmd, args, kw in self._pipeline:
            try:
                cmd = (
                    str(cmd, encoding="utf-8")
                    if isinstance(cmd, bytes)
                    else str(cmd)
                )
                statement = json.dumps(
                    dict(cmd=cmd, args=list(map(str, args)))
                )
                with redis_span(
                    self,
                    span=self._span,
                    operation=cmd,
                    statement=statement,
                    db_instance=REDIS,
                ):
                    result_fut = conn.execute(cmd, *args, **kw)
                    result_fut.add_done_callback(
                        functools.partial(self._check_result, waiter=fut)
                    )
            except Exception as exc:
                fut.set_exception(exc)
            else:
                yield result_fut


async def _gather_result(self, return_exceptions):
    errors = []
    results = []
    for fut in self._results:
        try:
            res = await fut
            results.append(res)
        except Exception as exc:
            errors.append(exc)
            results.append(exc)
    if errors and not return_exceptions:
        raise self.error_class(errors)
    if self._span:
        self._span.finish()
    return results


def install_patch():
    if "aioredis" not in globals():
        raise Exception("aioredis import fail")
    aioredis.Redis.execute = excute_wrapper
    aioredis.Redis.pipeline = pipeline_wrapper
    aioredis.Redis.multi_exec = multi_exec_wrapper

    aioredis.commands.transaction.Pipeline._send_pipeline = _send_pipeline
    aioredis.commands.transaction.Pipeline._gather_result = _gather_result
