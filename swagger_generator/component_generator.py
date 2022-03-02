
class component_generator:
    mysql_schemas = set()
    request_content_schemas = {}
    sql_gen = None
    py_gen = None

    def __init__(self):
        from .model_generator import SQLAlchemy_generator, py_generator
        self.sql_gen = SQLAlchemy_generator()
        self.py_gen = py_generator()

    def add_request_content_schema(self, api_tag:str, content:dict):
        api_tag = api_tag.lower()
        c_schemas = self.request_content_schemas.get(api_tag)
        if c_schemas is None:
            self.request_content_schemas[api_tag] = {content}
        else:
            self.request_content_schemas[api_tag].add(content)

    def parse_definitions(self, sqlalchemy_base_model):
        definitions = {}
        # get mysql components.
        mysql_schemas_list = list(self.mysql_schemas)
        sql_component = self.sql_gen.get_components(mysql_schemas_list, sqlalchemy_base_model)
        definitions.update(sql_component)
        # get request content components.
        py_component = self.py_gen.get_components(self.request_content_schemas)
        definitions.update(py_component)

        return definitions
