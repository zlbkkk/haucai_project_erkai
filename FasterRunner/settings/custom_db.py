from django.db.backends.mysql.base import DatabaseWrapper as MySQLDatabaseWrapper
from FasterRunner.mysql_operations import CustomMySQLOperations

# 替换MySQL操作类
MySQLDatabaseWrapper.ops_class = CustomMySQLOperations 