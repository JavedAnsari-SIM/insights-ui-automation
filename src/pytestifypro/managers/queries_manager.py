#src/pytestifypro/managers/query_manager.py
import yaml
import os

class YAMLQueriesManager:
    def __init__(self, queries_file='src/pytestifypro/data/queries.yaml'):
        with open(queries_file) as f:
            self.queries = yaml.safe_load(f)

    def get_query(self, query_name, **kwargs):
        if query_name not in self.queries:
            raise ValueError(f"Query '{query_name}' not found.")
        query = self.queries[query_name]
        # Substitute placeholders
        for key, value in kwargs.items():
            query = query.replace(f"{{{{{key}}}}}", str(value))
        return query

class SQLFileQueriesManager:
    def __init__(self, base_dir='src/pytestifypro/data/queries'):
        self.base_dir = base_dir

    def get_query(self, query_name, **kwargs):
        file_path = os.path.join(self.base_dir, f"{query_name}")
        if not os.path.exists(file_path):
            raise ValueError(f"Query file {file_path} not found.")
        with open(file_path, 'r') as f:
            query = f.read()
        for key, value in kwargs.items():
            query = query.replace(f"{{{{{key}}}}}", str(value))
        return query