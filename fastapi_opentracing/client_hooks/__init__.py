from . import mysql_client
from . import pg_client
from . import sqlite_client


def install_all_patch():
    mysql_client.install_patch()
    pg_client.install_patch()
    sqlite_client.install_patch()