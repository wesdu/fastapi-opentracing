from __future__ import absolute_import

import opentracing
from opentracing.ext import tags
from fastapi_opentracing import tracer, get_current_span
from ._const import TRANS_TAGS


async def db_span(self, query: str, db_instance, db_type="SQL"):
    """
    Span for database
    """
    span = await get_current_span()
    statement = query.strip()
    spance_idx = statement.find(" ")
    if query in TRANS_TAGS:
        operation = query
    else:
        if spance_idx == -1:
            operation = " "
        else:
            operation = statement[0:spance_idx]

    span_tag = {tags.SPAN_KIND: tags.SPAN_KIND_RPC_CLIENT}
    span_tag[tags.DATABASE_STATEMENT] = statement
    span_tag[tags.DATABASE_TYPE] = db_type
    span_tag[tags.DATABASE_INSTANCE] = db_instance
    span_tag[tags.DATABASE_USER] = self.user if hasattr(self, "user") else self._parent.user
    host = self.host if hasattr(self, "host") else self._parent.host
    port = self.port if hasattr(self, "port") else self._parent.port
    database = self.database if hasattr(self, "database") else self._parent.database
    span_tag[tags.PEER_ADDRESS] = f'{db_instance}://{host}:{port}/{database}'
    
    return start_child_span(
        operation_name=operation, tracer=tracer, parent=span, span_tag=span_tag
    )


def start_child_span(operation_name: str, tracer=None, parent=None, span_tag=None):
    """
    Start a new span as a child of parent_span. If parent_span is None,
    start a new root span.
    :param operation_name: operation name
    :param tracer: Tracer or None (defaults to opentracing.tracer)
    :param parent: parent or None
    :param span_tag: optional tags
    :return: new span
    """
    tracer = tracer or opentracing.tracer
    return tracer.start_span(
        operation_name=operation_name, child_of=parent, tags=span_tag
    )
