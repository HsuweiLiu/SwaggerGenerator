# This generator could generate swagger 2.0 api document automatically.
# all path is get from url map of Flask application.
# only the rule function which has set the function document with swagger format will be generated.
def gennerate_swagger_yaml(flask_app, sqlalchemy_base_model, title="api document", description="", version="1.0.0",
                           contact_email="", host="", outfile_name='api_document'):
    from swagger_generator.generator import generator
    gen = generator(flask_app)

    definitions = gen.get_definitions(sqlalchemy_base_model=sqlalchemy_base_model)
    tags = gen.get_api_tags()
    paths = gen.get_paths()

    # add token component.
    # definitions["Token"] = dict(
    #    type="object",
    #    properties=dict(
    #        access_token=dict(type="string"),
    #        refresh_token=dict(type="string")
    #    )
    # )

    # defined security schema.
    bearer_auth = dict(type="apiKey", name="Authorization")
    bearer_auth["in"] = "header"

    # defined the yaml dictionary.
    data = dict(
        swagger="2.0",
        info=dict(
            title=title,
            description=description,
            version=version,
            contact=dict(email=contact_email)
        ),
        host=host,
        schemes=["https"],
        tags=tags,
        paths=paths,
        definitions=definitions,
        securityDefinitions=dict(
            Bearer=bearer_auth
        )
    )

    # write data to yaml file.
    import yaml
    with open(f"{outfile_name}.yml", 'w') as outfile:
        yaml.dump(data, outfile, default_flow_style=False)
