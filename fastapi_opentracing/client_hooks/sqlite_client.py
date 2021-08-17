from typing import Optional
from ._db_span import db_span
from ._const import BEGIN, COMMIT, ROLLBACK, SQLITE

try:
    import tortoise.backends.sqlite
except ImportError:
    pass
else:
    _tortoise_sqlite_client_execute_query = (
        tortoise.backends.sqlite.client.SqliteClient.execute_query
    )
    _tortoise_sqlite_client_execute_insert = (
        tortoise.backends.sqlite.client.SqliteClient.execute_insert
    )
    _tortoise_sqlite_client_execute_query_dict = (
        tortoise.backends.sqlite.client.SqliteClient.execute_query_dict
    )

    """transaction"""
    _tortoise_sqlite_client_execute_many = (
        tortoise.backends.sqlite.client.TransactionWrapper.execute_many
    )
    _tortoise_sqlite_client_start = (
        tortoise.backends.sqlite.client.TransactionWrapper.start
    )
    _tortoise_sqlite_client_commit = (
        tortoise.backends.sqlite.client.TransactionWrapper.commit
    )
    _tortoise_sqlite_client_rollback = (
        tortoise.backends.sqlite.client.TransactionWrapper.rollback
    )


item_list = [
    "_tortoise_sqlite_client_execute_query",
    "_tortoise_sqlite_client_execute_insert",
    "_tortoise_sqlite_client_execute_query_dict",
    "_tortoise_sqlite_client_execute_many",
    "_tortoise_sqlite_client_start",
    "_tortoise_sqlite_client_commit",
    "_tortoise_sqlite_client_rollback",
]


async def sqlite_execute_query_wrapper(self, query: str, values: Optional[list] = None):
    with await db_span(self, query=query, db_instance=SQLITE):
        return await _tortoise_sqlite_client_execute_query(self, query, values)


async def sqlite_execute_insert_wrapper(self, query: str, values: list):
    with await db_span(self, query=query, db_instance=SQLITE):
        return await _tortoise_sqlite_client_execute_insert(self, query, values)


async def sqlite_execute_query_dict_wrapper(
    self, query: str, values: Optional[list] = None
):
    with await db_span(self, query=query, db_instance=SQLITE):
        return await _tortoise_sqlite_client_execute_query_dict(self, query, values)


"""transaction"""


async def sqlite_execute_many_wrapper(self, query: str, values: list):
    with await db_span(self, query=query, db_instance=SQLITE):
        return await _tortoise_sqlite_client_execute_many(self, query, values)


async def sqlite_trans_start_wrapper(self):
    with await db_span(self, query=BEGIN, db_instance=SQLITE):
        return await _tortoise_sqlite_client_start(self)


async def sqlite_trans_commit_wrapper(self):
    with await db_span(self, query=COMMIT, db_instance=SQLITE):
        return await _tortoise_sqlite_client_commit(self)


async def sqlite_trans_rollback_wrapper(self):
    with await db_span(self, query=ROLLBACK, db_instance=SQLITE):
        return await _tortoise_sqlite_client_rollback(self)


def install_patch():
    if any(item not in globals() for item in item_list):
        raise Exception("sqlite patch install fail")
    tortoise.backends.sqlite.client.SqliteClient.execute_query = (
        sqlite_execute_query_wrapper
    )
    tortoise.backends.sqlite.client.SqliteClient.execute_insert = (
        sqlite_execute_insert_wrapper
    )
    tortoise.backends.sqlite.client.SqliteClient.execute_query_dict = (
        sqlite_execute_query_dict_wrapper
    )
    
    """transaction"""
    tortoise.backends.sqlite.client.TransactionWrapper.execute_many = (
        sqlite_execute_many_wrapper
    )
    tortoise.backends.sqlite.client.TransactionWrapper.start = (
        sqlite_trans_start_wrapper
    )
    tortoise.backends.sqlite.client.TransactionWrapper.commit = (
        sqlite_trans_commit_wrapper
    )
    tortoise.backends.sqlite.client.TransactionWrapper.rollback = (
        sqlite_trans_rollback_wrapper
    )
