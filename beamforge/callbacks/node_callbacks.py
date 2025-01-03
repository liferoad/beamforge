# standard libraries
import os
import subprocess
import tempfile

# third party libraries
import dash
import dash_bootstrap_components as dbc
import yaml
from dash import Input, Output, State, dcc, html
from dash_ace import DashAceEditor

from beamforge.utils.graph_utils import format_log_with_timestamp, generate_yaml_content
from beamforge.utils.transform_parser import BEAM_YAML_TRANSFORMS


def get_node_type_options():
    return [{"label": transform, "value": transform} for transform in BEAM_YAML_TRANSFORMS]


def register_node_callbacks(app):
    @app.callback(Output("node-data", "children"), Input("network-graph", "tapNodeData"))
    def display_node_data(node_data):
        if not node_data:
            return "Click a node to see its details"

        # Create a formatted display of node data using dbc.Card with a custom background color
        details = dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(html.H6("Name:"), width=4),
                        dbc.Col(
                            dcc.Input(
                                id="node-id-input",
                                value=node_data["id"],
                                type="text",
                                style={"border": "1px solid #ced4da", "fontSize": "14px"},
                            ),
                            width=8,
                        ),
                    ],
                    style={"margin-bottom": "10px"},
                ),
                dbc.Row(
                    [
                        dbc.Col(html.H6("Type:"), width=4),
                        dbc.Col(
                            dcc.Dropdown(
                                id="node-type-dropdown",
                                options=get_node_type_options(),
                                value=node_data["type"],
                                style={"border": "1px solid #ced4da", "fontSize": "14px"},
                            ),
                            width=8,
                        ),
                    ],
                    style={"margin-bottom": "10px"},
                ),
                dbc.Row(
                    [
                        html.H6("Configuration:"),
                        DashAceEditor(
                            id="node-config-editor",
                            value=yaml.dump(node_data["config"], indent=2),
                            style={"height": "200px"},
                            theme="tomorrow",
                            mode="yaml",
                            maxLines=5000,
                        ),
                    ],
                    style={"margin-bottom": "5px"},
                ),
                dbc.Row(
                    [
                        html.H6("Usage/Example:"),
                        DashAceEditor(
                            id="node-config-usage",
                            value=BEAM_YAML_TRANSFORMS[node_data["type"]],
                            maxLines=5000,
                            theme="tomorrow",
                            readOnly=True,
                            mode="yaml",
                        ),
                    ],
                    style={"margin-bottom": "5px"},
                ),
            ],
            fluid=True,
        )

        return html.Div(details)

    @app.callback(
        Output("network-graph", "elements", allow_duplicate=True),
        Output("yaml-content", "value", allow_duplicate=True),
        Output("graph-log", "children", allow_duplicate=True),
        Input("node-config-editor", "value"),
        State("network-graph", "tapNodeData"),
        State("network-graph", "elements"),
        State("graph-log", "children"),
        prevent_initial_call=True,
    )
    def save_node_config(config_value, node_data, elements, log_message):
        if node_data:
            try:
                new_config = yaml.safe_load(config_value)
                node_id = node_data["id"]
                updated_elements = []
                for element in elements:
                    if element.get("data") and element["data"].get("id") == node_id:
                        element["data"]["config"] = new_config
                    updated_elements.append(element)
                yaml_content = generate_yaml_content(updated_elements)
                log_message += f"Updated config for node '{node_data['id']}'\n"
                return updated_elements, yaml_content, format_log_with_timestamp(log_message)
            except yaml.YAMLError:
                return dash.no_update, dash.no_update, dash.no_update
        return dash.no_update, dash.no_update, dash.no_update

    @app.callback(
        Output("network-graph", "elements", allow_duplicate=True),
        Output("yaml-content", "value", allow_duplicate=True),
        Output("graph-log", "children", allow_duplicate=True),
        Input("node-type-dropdown", "value"),
        State("network-graph", "tapNodeData"),
        State("network-graph", "elements"),
        State("graph-log", "children"),
        prevent_initial_call=True,
    )
    def update_node_type(new_type, node_data, elements, log_message):
        if node_data:
            node_id = node_data["id"]
            updated_elements = []
            for element in elements:
                if element.get("data") and element["data"].get("id") == node_id:
                    element["data"]["type"] = new_type
                    element["data"]["config"] = {}  # Reset config to empty
                updated_elements.append(element)
            yaml_content = generate_yaml_content(updated_elements)
            log_message += f"Changed type of node '{node_data['id']}' to '{new_type}'"
            return (
                updated_elements,
                yaml_content,
                format_log_with_timestamp(log_message),
            )
        return dash.no_update, dash.no_update, dash.no_update

    @app.callback(
        Output("node-config-editor", "value"),
        Output("node-config-usage", "value"),
        Input("node-type-dropdown", "value"),
        State("network-graph", "tapNodeData"),
        prevent_initial_call=True,
    )
    def update_node_config_and_usage(new_type, node_data):
        if node_data:
            return yaml.dump({}, indent=2), BEAM_YAML_TRANSFORMS[new_type]
        return dash.no_update, dash.no_update

    @app.callback(
        Output("network-graph", "elements", allow_duplicate=True),
        Output("network-graph", "tapNodeData", allow_duplicate=True),
        Output("yaml-content", "value", allow_duplicate=True),
        Output("graph-log", "children", allow_duplicate=True),
        Input("node-id-input", "value"),
        State("network-graph", "tapNodeData"),
        State("network-graph", "elements"),
        State("graph-log", "children"),
        prevent_initial_call=True,
    )
    def update_node_id(new_node_id, node_data, elements, log_message):
        if len(new_node_id) == 0:
            log_message += "Node ID cannot be empty\n"
            return dash.no_update, dash.no_update, dash.no_update, format_log_with_timestamp(log_message)
        if node_data and node_data["id"] != new_node_id:
            old_node_id = node_data["id"]
            updated_elements = []
            for element in elements:
                if element.get("data") and element["data"].get("id") == old_node_id:
                    element["data"]["id"] = new_node_id
                    node_data = element["data"]
                elif element.get("data") and element["data"].get("source") == old_node_id:
                    element["data"]["source"] = new_node_id
                    element["data"]["id"] = None
                elif element.get("data") and element["data"].get("target") == old_node_id:
                    element["data"]["target"] = new_node_id
                    element["data"]["id"] = None
                updated_elements.append(element)
            yaml_content = generate_yaml_content(updated_elements)
            log_message += f"Renamed node from '{node_data['id']}' to '{new_node_id}'\n"
            return updated_elements, node_data, yaml_content, format_log_with_timestamp(log_message)
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update

    @app.callback(
        Output("graph-log", "children", allow_duplicate=True),
        Input("run-pipeline-button", "n_clicks"),
        State("pipeline-runner-dropdown", "value"),
        State("pipeline-options-input", "value"),
        State("yaml-content", "value"),
        State("graph-log", "children"),
        prevent_initial_call=True,
    )
    def run_beam_pipeline(n_clicks, runner, pipeline_options, yaml_content, log_message):
        if n_clicks is None:
            return dash.no_update

        with tempfile.TemporaryDirectory() as tmp_dir:
            yaml_path = os.path.join(tmp_dir, "pipeline.yaml")

            # Create a temporary file for the YAML content
            with open(yaml_path, "w") as f:
                f.write(yaml_content)

            # Construct the command
            command = [
                "python",
                "-m",
                "apache_beam.yaml.main",
                f"--yaml_pipeline_file={yaml_path}",
                f"--runner={runner}",
            ]
            if pipeline_options:
                command.extend(pipeline_options.split())

            # Execute the command and capture the output
            try:
                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()
                output = (stdout.decode() + "\n" + stderr.decode()).strip()
                log_message += f"Ran pipeline with command: {' '.join(command)}\n"
                log_message += f"Output:\n{output}\n"
            except Exception as e:
                log_message += f"Error running pipeline: {e}\n"

            return format_log_with_timestamp(log_message)
        return format_log_with_timestamp(log_message)
