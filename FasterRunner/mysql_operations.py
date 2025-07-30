from django.db.backends.mysql.operations import DatabaseOperations

class CustomMySQLOperations(DatabaseOperations):
    def last_executed_query(self, cursor, sql, params):
        # 修复decode问题
        if hasattr(cursor, '_executed'):
            query = cursor._executed
            if isinstance(query, bytes):
                query = query.decode(errors='replace')
            return query
        return sql 