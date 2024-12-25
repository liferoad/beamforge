# standard libraries
import base64

# third party libraries
import yaml
from dash import Input, Output


def register_yaml_callbacks(app):
    @app.callback(
        Output("yaml-content", "children"),
        Input("upload-data", "contents"),
    )
    def update_yaml_content(contents):
        if contents is None:
            return "YAML content will appear here..."

        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)

        try:
            yaml_dict = yaml.safe_load(decoded)
            formatted_yaml = yaml.dump(yaml_dict, default_flow_style=False, sort_keys=False)
            return formatted_yaml
        except Exception as e:
            return f"Error processing YAML file: {str(e)}"
