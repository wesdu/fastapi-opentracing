from typing import Optional
from ._db_span import db_span
from ._const import BEGIN, COMMIT, ROLLBACK, PGDB

try:
    import tortoise.backends.asyncpg
except ImportError:
    pass
else:
    _tortoise_pg_client_execute_query = (
        tortoise.backends.asyncpg.client.AsyncpgDBClient.execute_query
    )
    _tortoise_pg_client_execute_insert = (
        tortoise.backends.asyncpg.client.AsyncpgDBClient.execute_insert
    )
    _tortoise_pg_client_execute_query_dict = (
        tortoise.backends.asyncpg.client.AsyncpgDBClient.execute_query_dict
    )
    """transaction"""
    _tortoise_pg_client_execute_many = (
        tortoise.backends.asyncpg.client.TransactionWrapper.execute_many
    )
    _tortoise_pg_client_start = (
        tortoise.backends.asyncpg.client.TransactionWrapper.start
    )
    _tortoise_pg_client_commit = (
        tortoise.backends.asyncpg.client.TransactionWrapper.commit
    )
    _tortoise_pg_client_rollback = (
        tortoise.backends.asyncpg.client.TransactionWrapper.rollback
    )

item_list = [
    "_tortoise_pg_client_execute_query",
    "_tortoise_pg_client_execute_insert",
    "_tortoise_pg_client_execute_query_dict",
    "_tortoise_pg_client_execute_many",
    "_tortoise_pg_client_start",
    "_tortoise_pg_client_commit",
    "_tortoise_pg_client_rollback",
]


async def pg_execute_query_wrapper(
    self, query: str, values: Optional[list] = None
):
    with await db_span(self, query=query, db_instance=PGDB):
        return await _tortoise_pg_client_execute_query(self, query, values)


async def pg_execute_insert_wrapper(self, query: str, values: list):
    with await db_span(self, query=query, db_instance=PGDB):
        return await _tortoise_pg_client_execute_insert(self, query, values)


async def pg_execute_query_dict_wrapper(
    self, query: str, values: Optional[list] = None
):
    with await db_span(self, query=query, db_instance=PGDB):
        return await _tortoise_pg_client_execute_query_dict(
            self, query, values
        )


"""transaction"""


async def pg_execute_many_wrapper(self, query: str, values: list):
    with await db_span(self, query=query, db_instance=PGDB):
        return await _tortoise_pg_client_execute_many(self, query, values)


async def pg_trans_start_wrapper(self):
    with await db_span(self, query=BEGIN, db_instance=PGDB):
        return await _tortoise_pg_client_start(self)


async def pg_trans_commit_wrapper(self):
    with await db_span(self, query=COMMIT, db_instance=PGDB):
        return await _tortoise_pg_client_commit(self)


async def pg_trans_rollback_wrapper(self):
    with await db_span(self, query=ROLLBACK, db_instance=PGDB):
        return await _tortoise_pg_client_rollback(self)


def install_patch():
    if any(item not in globals() for item in item_list):
        raise Exception("asyncpg patch install fail")
    tortoise.backends.asyncpg.client.AsyncpgDBClient.execute_query = (
        pg_execute_query_wrapper
    )
    tortoise.backends.asyncpg.client.AsyncpgDBClient.execute_insert = (
        pg_execute_insert_wrapper
    )
    tortoise.backends.asyncpg.client.AsyncpgDBClient.execute_query_dict = (
        pg_execute_query_dict_wrapper
    )
    """transaction"""
    tortoise.backends.asyncpg.client.TransactionWrapper.execute_many = (
        pg_execute_many_wrapper
    )
    tortoise.backends.asyncpg.client.TransactionWrapper.start = (
        pg_trans_start_wrapper
    )
    tortoise.backends.asyncpg.client.TransactionWrapper.commit = (
        pg_trans_commit_wrapper
    )
    tortoise.backends.asyncpg.client.TransactionWrapper.rollback = (
        pg_trans_rollback_wrapper
    )
