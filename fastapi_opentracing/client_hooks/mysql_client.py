from typing import Optional
from ._db_span import db_span
from ._const import BEGIN, COMMIT, ROLLBACK, MYSQLDB

try:
    import tortoise.backends.mysql
except ImportError:
    pass
else:
    _tortoise_mysql_client_execute_query = (
        tortoise.backends.mysql.client.MySQLClient.execute_query
    )
    _tortoise_mysql_client_execute_insert = (
        tortoise.backends.mysql.client.MySQLClient.execute_insert
    )
    _tortoise_mysql_client_execute_query_dict = (
        tortoise.backends.mysql.client.MySQLClient.execute_query_dict
    )

    '''transaction'''
    _tortoise_mysql_client_execute_many = (
        tortoise.backends.mysql.client.TransactionWrapper.execute_many
    )
    _tortoise_mysql_client_start = (
        tortoise.backends.mysql.client.TransactionWrapper.start
    )
    _tortoise_mysql_client_commit = (
        tortoise.backends.mysql.client.TransactionWrapper.commit
    )
    _tortoise_mysql_client_rollback = (
        tortoise.backends.mysql.client.TransactionWrapper.rollback
    )

item_list = [
    "_tortoise_mysql_client_execute_query",
    "_tortoise_mysql_client_execute_insert",
    "_tortoise_mysql_client_execute_query_dict",
    "_tortoise_mysql_client_execute_many",
    "_tortoise_mysql_client_start",
    "_tortoise_mysql_client_commit",
    "_tortoise_mysql_client_rollback"
]


async def mysql_execute_query_wrapper(self, query: str, values: Optional[list] = None):
    with await db_span(self, query, db_instance=MYSQLDB):
        return await _tortoise_mysql_client_execute_query(self, query, values)

async def mysql_execute_insert_wrapper(self, query: str, values: list):
    with await db_span(self, query, db_instance=MYSQLDB):
        return await _tortoise_mysql_client_execute_insert(self, query, values)

async def mysql_execute_query_dict(self, query: str, values: Optional[list] = None):
    with await db_span(self, query, db_instance=MYSQLDB):
        return await _tortoise_mysql_client_execute_query_dict(self, query, values)


"""transaction"""

async def mysql_execute_many_wrapper(self, query: str, values: list):
    with await db_span(self, query=query, db_instance=MYSQLDB):
        return await _tortoise_mysql_client_execute_many(self, query, values)


async def mysql_trans_start_wrapper(self):
    with await db_span(self, query=BEGIN, db_instance=MYSQLDB):
        return await _tortoise_mysql_client_start(self)


async def mysql_trans_commit_wrapper(self):
    with await db_span(self, query=COMMIT, db_instance=MYSQLDB):
        return await _tortoise_mysql_client_commit(self)


async def mysql_trans_rollback_wrapper(self):
    with await db_span(self, query=ROLLBACK, db_instance=MYSQLDB):
        return await _tortoise_mysql_client_rollback(self)


def install_patch():
    if any(item not in globals() for item in item_list):
        raise Exception("aiomysql patch install fail")
    tortoise.backends.mysql.client.MySQLClient.execute_query = (
        mysql_execute_query_wrapper
    )
    tortoise.backends.mysql.client.MySQLClient.execute_insert = (
        mysql_execute_insert_wrapper
    )
    tortoise.backends.mysql.client.MySQLClient.execute_query_dict = (
        mysql_execute_query_dict
    )

    '''transaction'''
    tortoise.backends.mysql.client.TransactionWrapper.execute_many = (
        mysql_execute_many_wrapper
    )
    tortoise.backends.mysql.client.TransactionWrapper.start = (
        mysql_trans_start_wrapper
    )
    tortoise.backends.mysql.client.TransactionWrapper.commit = (
        mysql_trans_commit_wrapper
    )
    tortoise.backends.mysql.client.TransactionWrapper.rollback = (
        mysql_trans_rollback_wrapper
    )