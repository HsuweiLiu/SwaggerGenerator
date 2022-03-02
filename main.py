from flask import Flask, Blueprint, jsonify
from model import TestContent, TestModel, Base

from swagger_ui import flask_api_doc
from swagger_generator import gennerate_swagger_yaml
from sqlalchemy.ext.declarative import declarative_base


YAML_FILE_NAME = "TestDoc"

# Create Main BluePrint.
main = Blueprint('Main', __name__)


@main.route('/Model', methods=['Get'])
def GetModel():
    """
    {
        "get":{
            "summary": "Get TestModel",
            "security": [{"Bearer":[]}],
            "responses":{
                "200":{
                    "description":"Success.",
                    "schema":{
                        "type": "object",
                        "properties":{
                            "Data":{
                                "$ref":"#/definitions/TestModel"
                            }
                        }
                    }
                }
            }
        }
    }
    """
    test_model = TestModel(Id=1, ValidFlag=True, CreateUser="test")
    return jsonify(f"{test_model.__class__}:{test_model.__dict__}")


@main.route('/Content', methods=['Get'])
def GetContent():
    """
    {
        "get":{
            "summary": "Get TestContent",
            "security": [{"Bearer":[]}],
            "responses":{
                "200":{
                    "description":"Success.",
                    "schema":{
                        "type": "object",
                        "properties":{
                            "Data":{
                                "$ref":"#/definitions/TestContent"
                            }
                        }
                    }
                }
            }
        }
    }
    """
    test_content = TestContent(test_str="I am string", test_int=123)
    return jsonify(f"{test_content.__class__}:{test_content.__dict__}")


if __name__ == '__main__':
    app = Flask(__name__)
    app.register_blueprint(main)

    gennerate_swagger_yaml(app,
                           sqlalchemy_base_model=Base,
                           title="Test APIs",
                           description="API.",
                           version="1.0.0",
                           contact_email="",
                           host="",
                           outfile_name=YAML_FILE_NAME)

    # register swagger web view.
    flask_api_doc(app, config_path=f'./{YAML_FILE_NAME}.yml', url_prefix='/api/doc', title='API doc')

    app.run()
