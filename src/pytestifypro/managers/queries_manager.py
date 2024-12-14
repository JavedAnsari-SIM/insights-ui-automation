#src/pytestifypro/managers/queries_manager.py
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

    def get_query(self, query_name, specific_query=None, **kwargs):
        """
        Fetch a specific query from a file. If `specific_query` is provided,
        it will return only that query from a multi-query file.
        """
        file_path = os.path.join(self.base_dir, query_name)
        if not os.path.exists(file_path):
            raise ValueError(f"Query file {file_path} not found.")

        with open(file_path, 'r') as f:
            queries_content = f.read()

        if specific_query:
            queries = self._parse_queries(queries_content)
            if specific_query not in queries:
                raise ValueError(f"Specific query '{specific_query}' not found in {query_name}.")
            query = queries[specific_query]
        else:
            query = queries_content

        # Replace placeholders with provided kwargs
        for key, value in kwargs.items():
            query = query.replace(f"{{{{{key}}}}}", str(value))

        return query

    def _parse_queries(self, queries_content):
        """
        Parse a file containing multiple queries, separated by comments in the format '-- query_name'.
        Returns a dictionary of query_name -> query.
        """
        queries = {}
        current_name = None
        current_query = []

        for line in queries_content.splitlines():
            line = line.strip()
            if line.startswith("--"):
                if current_name:
                    queries[current_name] = "\n".join(current_query).strip()
                current_name = line[2:].strip()
                current_query = []
            elif line:
                current_query.append(line)

        if current_name:
            queries[current_name] = "\n".join(current_query).strip()

        return queries