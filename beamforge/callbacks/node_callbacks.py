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
from dash import ALL, Input, Output, State, dcc, html
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


def _display_node_data_callback(node_data):
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
            html.Div(
                id="node-config-container",
                children=[
                    # Configuration rows will be added here
                ],
            ),
            dbc.Row(
                [
                    html.H6("Usage Example:"),
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
            # Add dcc.Store to store node config data
            dcc.Store(id="node-config-data"),
        ],
        fluid=True,
    )

    return html.Div(details)


def _update_node_config_display_callback(node_data, new_type):
    if not node_data and not new_type:
        return [], ""

    if new_type and node_data.get("type", {}) != new_type:
        config = yaml.safe_load(BEAM_YAML_TRANSFORMS[new_type]).get("config", {})
    else:
        config = node_data.get("config", {})
        if not config:
            node_type = node_data.get("type", {})
            if node_type != "UNKNOWN":
                config = yaml.safe_load(BEAM_YAML_TRANSFORMS[node_type]).get("config", {})

    formatted_config = custom_yaml_dump(config)
    config_lines = formatted_config.strip().split("\n")

    has_config = False
    for line in config_lines:
        if ":" in line:
            has_config = True
            break
    if not has_config or not config:
        config_rows = [html.H6("No Configuration.")]
    else:
        config_rows = [html.H6("Configuration:")]
        for key, value in config.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    config_rows.append(
                        dbc.Row(
                            [
                                dbc.Col(html.Label(f"{sub_key}:"), width=4),
                                dbc.Col(
                                    dcc.Input(
                                        value=str(sub_value),
                                        type="text",
                                        style={"width": "100%"},
                                        id={"type": "node-config-input", "index": sub_key},
                                    ),
                                    width=8,
                                ),
                            ],
                            style={"margin-bottom": "5px"},
                        )
                    )
            else:
                config_rows.append(
                    dbc.Row(
                        [
                            dbc.Col(html.Label(f"{key}:"), width=4),
                            dbc.Col(
                                dcc.Input(
                                    value=str(value),
                                    type="text",
                                    style={"width": "100%"},
                                    id={"type": "node-config-input", "index": key},
                                ),
                                width=8,
                            ),
                        ],
                        style={"margin-bottom": "5px"},
                    )
                )

    return config_rows, BEAM_YAML_TRANSFORMS[new_type]


def _update_node_config_callback(config_values, node_data, elements, table_data):
    if not node_data or not config_values:
        return dash.no_update, dash.no_update, dash.no_update

    node_id = node_data["id"]
    config_keys = [key["id"]["index"] for key in dash.ctx.inputs_list[0]]

    updated_elements = []
    for element in elements:
        if element.get("data") and element["data"].get("id") == node_id:
            config = {}
            for key, value in zip(config_keys, config_values):
                config[key] = value
            element["data"]["config"] = config
        updated_elements.append(element)

    yaml_content = generate_yaml_content(updated_elements)
    formatted_logs = format_log_with_timestamp(f"Updated config of node '{node_id}'")
    if table_data is None:
        table_data = []

    return updated_elements, yaml_content, table_data + formatted_logs


def _update_node_type_callback(new_type, node_data, elements, table_data):
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


def _update_tap_node_data_callback(new_type, node_data):
    if node_data and new_type:
        node_data["type"] = new_type
    return node_data


def _update_node_id_callback(new_node_id, node_data, elements, table_data):
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


def _disable_run_pipeline_button_callback(n_clicks):
    if n_clicks is None:
        return False  # Button starts enabled
    else:
        return True  # Disable after click


def _run_beam_pipeline_callback(n_clicks, runner, pipeline_options, yaml_content, table_data):
    if n_clicks is None:
        return dash.no_update, dash.no_update

    formatted_logs = _run_beam_pipeline(runner, pipeline_options, yaml_content, "")
    if table_data is None:
        table_data = []
    return table_data + formatted_logs, False


def _clear_graph_logs_callback(n_clicks):
    if n_clicks is None:
        return dash.no_update
    else:
        return []


def register_node_callbacks(app):
    app.callback(Output("node-data", "children"), Input("network-graph", "tapNodeData"))(_display_node_data_callback)
    app.callback(
        Output("node-config-container", "children"),
        Output("node-config-usage", "value"),
        Input("network-graph", "tapNodeData"),
        Input("node-type-dropdown", "value"),
        prevent_initial_call=True,
    )(_update_node_config_display_callback)
    app.callback(
        Output("network-graph", "elements", allow_duplicate=True),
        Output("yaml-content", "value", allow_duplicate=True),
        Output("graph-log-table", "data", allow_duplicate=True),
        Input({"type": "node-config-input", "index": ALL}, "value"),
        State("network-graph", "tapNodeData"),
        State("network-graph", "elements"),
        State("graph-log-table", "data"),
        prevent_initial_call=True,
    )(_update_node_config_callback)
    app.callback(
        Output("network-graph", "elements", allow_duplicate=True),
        Output("yaml-content", "value", allow_duplicate=True),
        Output("graph-log-table", "data", allow_duplicate=True),
        Input("node-type-dropdown", "value"),
        State("network-graph", "tapNodeData"),
        State("network-graph", "elements"),
        State("graph-log-table", "data"),
        prevent_initial_call=True,
    )(_update_node_type_callback)
    app.callback(
        Output("network-graph", "tapNodeData"),
        Input("node-type-dropdown", "value"),
        State("network-graph", "tapNodeData"),
        prevent_initial_call=True,
    )(_update_tap_node_data_callback)
    app.callback(
        Output("network-graph", "elements", allow_duplicate=True),
        Output("network-graph", "tapNodeData", allow_duplicate=True),
        Output("yaml-content", "value", allow_duplicate=True),
        Output("graph-log-table", "data", allow_duplicate=True),
        Input("node-id-input", "value"),
        State("network-graph", "tapNodeData"),
        State("network-graph", "elements"),
        State("graph-log-table", "data"),
        prevent_initial_call=True,
    )(_update_node_id_callback)
    app.callback(
        Output("run-pipeline-button", "disabled"),
        Input("run-pipeline-button", "n_clicks"),
    )(_disable_run_pipeline_button_callback)
    app.callback(
        Output("graph-log-table", "data", allow_duplicate=True),
        Output("run-pipeline-button", "disabled", allow_duplicate=True),
        Input("run-pipeline-button", "n_clicks"),
        State("pipeline-runner-dropdown", "value"),
        State("pipeline-options-input", "value"),
        State("yaml-content", "value"),
        State("graph-log-table", "data"),
        prevent_initial_call=True,
    )(_run_beam_pipeline_callback)
    app.callback(
        Output("graph-log-table", "data", allow_duplicate=True),
        Input("clear-graph-logs", "n_clicks"),
        prevent_initial_call=True,
    )(_clear_graph_logs_callback)
