import inspect
import json
import sys


# get model attribute document if exist.
def get_model_attribute_docs(model):
    attribute_docs = None
    if model.__doc__:
        try:
            doc = json.loads(model.__doc__)
            attribute_docs = doc.get("Attribute")
        except:
            pass

    return attribute_docs


class SQLAlchemy_generator:
    from sqlalchemy.sql import sqltypes
    sql2swagger_type_mapping_dict = {
        sqltypes.BigInteger: dict(type="integer", example=100),
        sqltypes.Integer: dict(type="integer", example=1),
        sqltypes.Unicode: dict(type="string", example="中文字"),
        sqltypes.String: dict(type="string", example="string"),
        sqltypes.Float: dict(type="integer", example=100.00),
        sqltypes.Numeric: dict(type="integer", example=10.00),
        sqltypes.DECIMAL: dict(type="integer", example=166.6),
        sqltypes.DateTime: dict(type="string", example="2021-03-16T00:00:00.000"),
        sqltypes.Boolean: dict(type="boolean", example="true"),
        sqltypes.Date: dict(type="string", example="2021-03-16"),
        sqltypes.Time: dict(type="string", example="2021-03-16T00:00:00.000"),
        sqltypes.Interval: dict(type="integer", example=100),
        sqltypes.TIMESTAMP: dict(type="string", example="2021-03-16T00:00:00.000")
    }

    @classmethod
    def get_components(cls, mysql_schemas_list, model_base):
        components = {}
        for c in model_base._decl_class_registry.values():
            clsmembers = inspect.getmembers(sys.modules[c.__module__], inspect.isclass)
            members = [value for (key, value) in clsmembers if key in mysql_schemas_list]
            for model in members:
                # get attribute document if exist.
                attribute_docs = get_model_attribute_docs(model)

                # get attribute and parsing to swagger type.
                properties = {}
                for column in model.__table__.columns:
                    p_type = cls.sql2swagger_type_mapping_dict[type(column.type)]
                    properties[column.name] = dict(type=p_type["type"], example=p_type["example"])
                    # update value if document exist.
                    if attribute_docs:
                        attr_doc = attribute_docs.get(column.name)
                        if attr_doc:
                            properties[column.name].update(attr_doc)

                components[model.__tablename__] = dict(type="object", properties=properties)

        return components


class py_generator:
    import datetime
    from typing import List
    python2swagger_type_mapping_dict = {
        int: dict(type="integer", example=100),
        str: dict(type="string", example="string"),
        float: dict(type="integer", example=160.50),
        datetime.datetime: dict(type="string", example="2021-03-16T00:00:00.000"),
        datetime.date: dict(type="string", example="2021-03-16"),
        datetime.time: dict(type="string", example="2021-03-16T00:00:00.000"),
        bool: dict(type="boolean", example="true"),
        List[int]: dict(type="object", example="[123,456,789]"),
        list: dict(type="array", example="[]"),
        dict: dict(type="object", example="{}"),
    }

    @classmethod
    def py_gen_properties(cls, model):
        from typing import get_type_hints
        # get attribute document if exist.
        attribute_docs = get_model_attribute_docs(model)

        properties = {}

        isList = False
        try:
            # get attribute and type hint.
            type_hints = get_type_hints(model)
        except:
            if model._name == 'List':
                isList = True
                type_class = model.__dict__['__args__'][0]
                # get attribute and type hint.
                type_hints = get_type_hints(type_class)

        for hint_key, hint_value in type_hints.items():
            try:
                p_type = cls.python2swagger_type_mapping_dict[hint_value]
                properties[hint_key] = dict(type=p_type["type"], example=p_type["example"])
                # update value if document exist.
                if attribute_docs:
                    attr_doc = attribute_docs.get(hint_key)
                    if attr_doc:
                        properties[hint_key].update(attr_doc)
            except:
                # nested class action.
                # recursive.
                sub_properties = cls.py_gen_properties(hint_value)
                properties[hint_key] = sub_properties
                if attribute_docs:
                    attr_doc = attribute_docs.get(hint_key)
                    if attr_doc:
                        properties[hint_key].update(attr_doc)

        return dict(type="array", items=dict(type="object", properties=properties)) if isList \
            else dict(type="object", properties=properties)

    @classmethod
    def get_components(cls, request_content_schemas):
        # from typing import get_type_hints
        components = {}
        for key, values in request_content_schemas.items():
            clsmembers = inspect.getmembers(sys.modules[f"application.{key}.model"], inspect.isclass)
            for content_name in values:
                # get request content from class member.
                model = [value for (key, value) in clsmembers if key == content_name in (key, value)][0]
                # get model properties.
                properties = cls.py_gen_properties(model)
                components[content_name] = properties

        return components
