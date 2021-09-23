from . import mysql_client
from . import pg_client
from . import sqlite_client
from . import redis_client
try:
    import tortoise
except Exception as e:
    raise e
else:
    res = tortoise.__version__.split('.')
    assert int(res[0]) == 0
    res.pop(0)
    assert 16.17 <= float(".".join(res)) <= 17.5

def install_all_patch():
    mysql_client.install_patch()
    pg_client.install_patch()
    sqlite_client.install_patch()
    redis_client.install_patch()