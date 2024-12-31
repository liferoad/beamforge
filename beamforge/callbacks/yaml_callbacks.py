# standard libraries
import base64

# third party libraries
import yaml
from dash import Input, Output, State

from beamforge.utils.graph_utils import generate_yaml_content


def register_yaml_callbacks(app):
    @app.callback(
        Output("yaml-content", "value"),
        Input("upload-data", "contents"),
        prevent_initial_call=True,
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

    @app.callback(
        Output("download-yaml", "data"),
        Input("create-yaml-button", "n_clicks"),
        State("network-graph", "elements"),
        prevent_initial_call=True,
    )
    def create_yaml_file(n_clicks, elements):
        if n_clicks is None or not elements:
            return None

        yaml_string = generate_yaml_content(elements)
        return dict(content=yaml_string, filename="beam_graph.yaml")
