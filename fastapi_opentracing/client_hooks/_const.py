"""transaction tag"""

BEGIN = "BEGIN"

COMMIT = "COMMIT"

ROLLBACK = "ROLLBACK"

TRANS_TAGS = [BEGIN, COMMIT, ROLLBACK]
"""database instance"""

MYSQLDB = "mysql"

PGDB = "postgress"

SQLITE = "sqlite"

REDIS = "redis"
