# Filter out rules that require parameters
def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


def get_content_parameter_ref(content):
    parameter_schema = content["parameters"][0].get("schema")
    if not parameter_schema:
        return None

    ref = parameter_schema.get("$ref")
    items = parameter_schema.get("items")
    ref = items.get("$ref") if items else ref
    return ref


def get_content_ref(content):
    content_data = content["responses"]["200"]["schema"]["properties"].get("Data")
    ref = content_data.get("$ref") 
    items = content_data.get("items") 
    ref = items.get("$ref") if items else ref
    return ref


class generator:
    api_set = set()
    paths = {}
    comp_gen = None

    def __init__(self, flask_app):
        from .component_generator import component_generator
        self.comp_gen = component_generator()

        import json
        # get all rules from url map of Flask application.
        for rule in flask_app.url_map.iter_rules():
            # Filter out rules we can't navigate to in a browser and rules that require parameters.
            if "POST" in rule.methods and has_no_empty_params(rule):
                # get view function with endpoint.
                func = flask_app.view_functions[rule.endpoint]
                # only functions with documents.
                if func.__doc__ is not None:
                    # get blueprint name from endpoint.
                    api_tag = rule.endpoint.split('.')[0]
                    self.api_set.add(api_tag)
                    # load json string for function document.
                    rule_content = json.loads(func.__doc__)
                    rule_content["post"]["tags"] = [f"{api_tag} API"]
                    # append paths.
                    if not self.paths.get(str(rule)):
                        self.paths[str(rule)] = rule_content
                    else:
                        self.paths[str(rule)]["post"] = rule_content["post"]

                    # get response schemas.
                    post_content = rule_content["post"]
                    ref = get_content_ref(post_content)
                    if ref:
                        schema = ref.split('/')[2]
                        if 'Content' in schema:
                            # and use add method.
                            self.comp_gen.add_request_content_schema(api_tag, schema)
                        else:
                            # and add to set.
                            self.comp_gen.mysql_schemas.add(schema)

                    # get request content schemas.
                    content = get_content_parameter_ref(post_content)
                    if content:
                        parameter = content.split('/')[2]
                        # and use add method.
                        self.comp_gen.add_request_content_schema(api_tag, parameter)

            elif "GET" in rule.methods and has_no_empty_params(rule):
                # get view function with endpoint.
                func = flask_app.view_functions[rule.endpoint]
                # only functions with documents.
                if func.__doc__ is not None:
                    # get blueprint name from endpoint.
                    api_tag = rule.endpoint.split('.')[0]
                    self.api_set.add(api_tag)
                    # load json string for function document.
                    
                    rule_content = json.loads(func.__doc__)
                    rule_content["get"]["tags"] = [f"{api_tag} API"]
                    # append paths.
                    if not self.paths.get(str(rule)):
                        self.paths[str(rule)] = rule_content
                    else:
                        self.paths[str(rule)]["get"] = rule_content["get"]

                    get_content = rule_content["get"]
                    ref = get_content_ref(get_content)
                    if ref:
                        schema = ref.split('/')[2]
                        if 'Content' in schema:
                            # and use add method.
                            self.comp_gen.add_request_content_schema(api_tag, schema)
                        else:
                            # and add to set.
                            self.comp_gen.mysql_schemas.add(schema)

            elif "DELETE" in rule.methods and has_no_empty_params(rule):
                # get view function with endpoint.
                func = flask_app.view_functions[rule.endpoint]
                # only functions with documents.
                if func.__doc__ is not None:
                    # get blueprint name from endpoint.
                    api_tag = rule.endpoint.split('.')[0]
                    self.api_set.add(api_tag)
                    # load json string for function document.

                    rule_content = json.loads(func.__doc__)
                    rule_content["delete"]["tags"] = [f"{api_tag} API"]
                    # append paths.
                    if not self.paths.get(str(rule)):
                        self.paths[str(rule)] = rule_content
                    else:
                        self.paths[str(rule)]["delete"] = rule_content["delete"]

                    delete_content = rule_content["delete"]
                    ref = get_content_ref(delete_content)
                    if ref:
                        schema = ref.split('/')[2]
                        if 'Content' in schema:
                            # and use add method.
                            self.comp_gen.add_request_content_schema(api_tag, schema)
                        else:
                            # and add to set.
                            self.comp_gen.mysql_schemas.add(schema)

    def get_api_tags(self):
        # distinct the api tags.
        tags = []
        api_tags = list(self.api_set)
        # append tags.
        for tag in api_tags:
            tags.append(dict(name = f"{tag} API", description = ""))

        return tags

    def get_paths(self):
        return self.paths

    def get_definitions(self, sqlalchemy_base_model):
        return self.comp_gen.parse_definitions(sqlalchemy_base_model=sqlalchemy_base_model)
