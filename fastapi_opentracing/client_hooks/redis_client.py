from ._db_span import redis_span
from ._const import REDIS
import json
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


try:
    import ujson as json
except:
    import json


from aioredis.commands.transaction import _RedisBuffer


def excute_wrapper(self, command, *args, **kwargs):
    span = sync_get_current_span()
    if span is None:
        return _excute(self, command, *args, **kwargs)
    if isinstance(self._pool_or_conn, _RedisBuffer):
        return _excute(self, command, *args, **kwargs)
    try:
        cmd = str(command, encoding="utf-8")
        statement = json.dumps(dict(cmd=cmd, args=list(map(str, args))))
    except Exception as e:
        print(f'opentracing-error {repr(e)}')
        return _excute(self, command, *args, **kwargs)
    else:
        with redis_span(
            self, span=span, operation=cmd, statement=statement, db_instance=REDIS
        ):
            return _excute(self, command, *args, **kwargs)


def pipeline_wrapper(self):
    pipe = _pipeline(self)
    span = sync_get_current_span()
    pipe._span = tracer.start_span(operation_name="PIPELINE", child_of=span)
    return pipe


def _send_pipeline(self, conn):
    with conn._buffered():
        for fut, cmd, args, kw in self._pipeline:
            try:
                cmd = str(cmd, encoding="utf-8")
                statement = json.dumps(dict(cmd=cmd, args=list(args)))
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
    self._span.finish()
    return results


def install_patch():
    if "aioredis" not in globals():
        raise Exception("aioredis import fail")
    aioredis.Redis.execute = excute_wrapper
    aioredis.Redis.pipeline = pipeline_wrapper

    aioredis.commands.transaction.Pipeline._send_pipeline = _send_pipeline
    aioredis.commands.transaction.Pipeline._gather_result = _gather_result
