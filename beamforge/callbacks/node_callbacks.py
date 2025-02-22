# standard libraries
# standard libraries
import datetime
import os
import random
import re
import subprocess
import tempfile

# third party libraries
import dash
import dash_bootstrap_components as dbc
import yaml
from dash import Input, Output, State, dcc, html
from dash_ace import DashAceEditor

from beamforge.utils.graph_utils import custom_yaml_dump, format_log_with_timestamp, generate_yaml_content
from beamforge.utils.transform_parser import BEAM_YAML_TRANSFORMS


def get_node_type_options():
    return [{"label": transform, "value": transform} for transform in BEAM_YAML_TRANSFORMS]


def create_dataflow_job_name(base_name="dataflow-job"):
    """
    Creates a Dataflow job name with the following format:
    {base_name}-{timestamp}-{random_number}

    Args:
      base_name: The base name for the job.

    Returns:
      A string representing the Dataflow job name.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    random_number = random.randint(1000, 9999)
    return f"{base_name}-{timestamp}-{random_number}"


def extract_job_id_and_create_url(output, region="us-central1"):
    """
    Extracts the job ID from the output of a subprocess call and creates the Dataflow job URL.

    Args:
      output: The output from the subprocess call.
      region: The region where the job was run.

    Returns:
      The Dataflow job URL, or None if the job ID could not be extracted.
    """
    match = re.search(r"id: (\S+)", output)
    if match:
        job_id = match.group(1)
        return f"https://pantheon.corp.google.com/dataflow/jobs/{region}/{job_id}"
    return None


def _run_beam_pipeline(runner, pipeline_options, yaml_content, log_message):
    region = None
    if pipeline_options:
        region_match = re.search(r"--region\s+([\w-]+)", pipeline_options)
        if region_match:
            region = region_match.group(1)

    if runner == "DataflowRunner" and region is None:
        region = "us-central1"
        if pipeline_options:
            pipeline_options += " --region us-central1"
        else:
            pipeline_options = "--region us-central1"

    with tempfile.TemporaryDirectory() as tmp_dir:
        yaml_path = os.path.join(tmp_dir, "pipeline.yaml")

        # Create a temporary file for the YAML content
        with open(yaml_path, "w") as f:
            f.write(yaml_content)

        dry_run = False
        if pipeline_options and "--dry_run True" in pipeline_options:
            dry_run = True

        # Construct the command
        if runner == "DataflowRunner" and not dry_run:
            command = [
                "gcloud",
                "dataflow",
                "yaml",
                "run",
                create_dataflow_job_name(),
                f"--yaml-pipeline-file={yaml_path}",
            ]
        else:
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
            if runner == "DataflowRunner" and not dry_run:
                dataflow_url = extract_job_id_and_create_url(output, region)
                if dataflow_url:
                    log_message += f"Dataflow job URL: {dataflow_url}\n"
        except Exception as e:
            log_message += f"Error running pipeline: {e}\n"

    return format_log_with_timestamp(log_message)


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
                        dbc.Col(
                            [
                                html.H6("Configuration:"),
                                html.Div(
                                    id="config-validation-status",
                                    style={"marginBottom": "5px", "fontSize": "12px"},
                                ),
                            ],
                            width=12,
                        ),
                        dbc.Col(
                            [
                                DashAceEditor(
                                    id="node-config-editor",
                                    value=custom_yaml_dump(node_data["config"]),
                                    style={
                                        "height": "200px",
                                        "border": "1px solid #ced4da",
                                        "borderRadius": "4px",
                                    },
                                    theme="tomorrow",
                                    mode="yaml",
                                    maxLines=5000,
                                    enableLiveAutocompletion=True,
                                    enableBasicAutocompletion=True,
                                    tabSize=2,
                                ),
                                html.Div(
                                    id="config-error-message",
                                    style={
                                        "color": "#dc3545",
                                        "fontSize": "12px",
                                        "marginTop": "5px",
                                        "display": "none",
                                    },
                                ),
                            ],
                            width=12,
                        ),
                    ],
                    style={"margin-bottom": "10px"},
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
        Output("graph-log-table", "data", allow_duplicate=True),
        Input("node-config-editor", "value"),
        State("network-graph", "tapNodeData"),
        State("network-graph", "elements"),
        State("graph-log-table", "data"),
        prevent_initial_call=True,
    )
    def save_node_config(config_value, node_data, elements, table_data):
        if node_data and config_value:
            try:
                new_config = yaml.safe_load(config_value)
                node_id = node_data["id"]
                updated_elements = []
                for element in elements:
                    if element.get("data") and element["data"].get("id") == node_id and new_config != {}:
                        element["data"]["config"] = new_config
                    updated_elements.append(element)
                yaml_content = generate_yaml_content(updated_elements)
                formatted_logs = format_log_with_timestamp(f"Updated config for node '{node_data['id']}'\n")
                if table_data is None:
                    table_data = []
                return updated_elements, yaml_content, table_data + formatted_logs
            except yaml.YAMLError as e:
                print(f"Error processing YAML file: {str(e)}")
                return dash.no_update, dash.no_update, dash.no_update
        return dash.no_update, dash.no_update, dash.no_update

    @app.callback(
        Output("network-graph", "elements", allow_duplicate=True),
        Output("yaml-content", "value", allow_duplicate=True),
        Output("graph-log-table", "data", allow_duplicate=True),
        Input("node-type-dropdown", "value"),
        State("network-graph", "tapNodeData"),
        State("network-graph", "elements"),
        State("graph-log-table", "data"),
        prevent_initial_call=True,
    )
    def update_node_type(new_type, node_data, elements, table_data):
        if node_data and new_type:
            node_id = node_data["id"]
            updated_elements = []
            for element in elements:
                if element.get("data") and element["data"].get("id") == node_id and new_type != node_data["type"]:
                    element["data"]["type"] = new_type
                    element["data"]["config"] = {}  # Reset config to empty
                updated_elements.append(element)
            yaml_content = generate_yaml_content(updated_elements)
            formatted_logs = format_log_with_timestamp(f"Changed type of node '{node_data['id']}' to '{new_type}'")
            if table_data is None:
                table_data = []
            return (
                updated_elements,
                yaml_content,
                table_data + formatted_logs,
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
            return custom_yaml_dump({}), BEAM_YAML_TRANSFORMS[new_type]
        return dash.no_update, dash.no_update

    @app.callback(
        Output("network-graph", "elements", allow_duplicate=True),
        Output("network-graph", "tapNodeData", allow_duplicate=True),
        Output("yaml-content", "value", allow_duplicate=True),
        Output("graph-log-table", "data", allow_duplicate=True),
        Input("node-id-input", "value"),
        State("network-graph", "tapNodeData"),
        State("network-graph", "elements"),
        State("graph-log-table", "data"),
        prevent_initial_call=True,
    )
    def update_node_id(new_node_id, node_data, elements, table_data):
        if len(new_node_id) == 0:
            formatted_logs = format_log_with_timestamp("Node ID cannot be empty\n")
            if table_data is None:
                table_data = []
            return dash.no_update, dash.no_update, dash.no_update, table_data + formatted_logs
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
            formatted_logs = format_log_with_timestamp(f"Renamed node from '{node_data['id']}' to '{new_node_id}'\n")
            if table_data is None:
                table_data = []
            return updated_elements, node_data, yaml_content, table_data + formatted_logs
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update

    @app.callback(
        Output("run-pipeline-button", "disabled"),
        Input("run-pipeline-button", "n_clicks"),
    )
    def disable_run_pipeline_button(n_clicks):
        if n_clicks is None:
            return False  # Button starts enabled
        else:
            return True  # Disable after click

    @app.callback(
        Output("graph-log-table", "data", allow_duplicate=True),
        Output("run-pipeline-button", "disabled", allow_duplicate=True),
        Input("run-pipeline-button", "n_clicks"),
        State("pipeline-runner-dropdown", "value"),
        State("pipeline-options-input", "value"),
        State("yaml-content", "value"),
        State("graph-log-table", "data"),
        prevent_initial_call=True,
    )
    def run_beam_pipeline(n_clicks, runner, pipeline_options, yaml_content, table_data):
        if n_clicks is None:
            return dash.no_update, dash.no_update

        formatted_logs = _run_beam_pipeline(runner, pipeline_options, yaml_content, "")
        if table_data is None:
            table_data = []
        return table_data + formatted_logs, False

    @app.callback(
        Output("graph-log-table", "data", allow_duplicate=True),
        Input("clear-graph-logs", "n_clicks"),
        prevent_initial_call=True,
    )
    def clear_graph_logs(n_clicks):
        if n_clicks is None:
            return dash.no_update
        else:
            return []

    @app.callback(
        Output("config-validation-status", "children"),
        Output("config-validation-status", "style"),
        Output("config-error-message", "children"),
        Output("config-error-message", "style"),
        Input("node-config-editor", "value"),
    )
    def validate_yaml_config(config_value):
        if not config_value:
            return (
                "Empty configuration",
                {"color": "#6c757d", "marginBottom": "5px", "fontSize": "12px"},
                "",
                {"display": "none"},
            )

        try:
            yaml.safe_load(config_value)
            return (
                "✓ Valid YAML",
                {"color": "#28a745", "marginBottom": "5px", "fontSize": "12px"},
                "",
                {"display": "none"},
            )
        except yaml.YAMLError as e:
            return (
                "✗ Invalid YAML",
                {"color": "#dc3545", "marginBottom": "5px", "fontSize": "12px"},
                str(e),
                {
                    "color": "#dc3545",
                    "fontSize": "12px",
                    "marginTop": "5px",
                    "display": "block",
                    "whiteSpace": "pre-wrap",
                    "fontFamily": "monospace",
                },
            )
