# third party libraries
import dash
import dash_bootstrap_components as dbc
import yaml
from dash import Input, Output, State, dcc, html
from dash_ace import DashAceEditor

from beamforge.utils.graph_utils import generate_yaml_content


def get_node_type_options():
    return [
        {"label": "AssertEqual", "value": "AssertEqual"},
        {"label": "AssignTimestamps", "value": "AssignTimestamps"},
        {"label": "Combine", "value": "Combine"},
        {"label": "Create", "value": "Create"},
        {"label": "Enrichment", "value": "Enrichment"},
        {"label": "Explode", "value": "Explode"},
        {"label": "Filter", "value": "Filter"},
        {"label": "Flatten", "value": "Flatten"},
        {"label": "Join", "value": "Join"},
        {"label": "LogForTesting", "value": "LogForTesting"},
        {"label": "MLTransform", "value": "MLTransform"},
        {"label": "MapToFields", "value": "MapToFields"},
        {"label": "Partition", "value": "Partition"},
        {"label": "PyTransform", "value": "PyTransform"},
        {"label": "Sql", "value": "Sql"},
        {"label": "StripErrorMetadata", "value": "StripErrorMetadata"},
        {"label": "ValidateWithSchema", "value": "ValidateWithSchema"},
        {"label": "WindowInto", "value": "WindowInto"},
        {"label": "ReadFromAvro", "value": "ReadFromAvro"},
        {"label": "WriteToAvro", "value": "WriteToAvro"},
        {"label": "ReadFromBigQuery", "value": "ReadFromBigQuery"},
        {"label": "WriteToBigQuery", "value": "WriteToBigQuery"},
        {"label": "ReadFromCsv", "value": "ReadFromCsv"},
        {"label": "WriteToCsv", "value": "WriteToCsv"},
        {"label": "ReadFromJdbc", "value": "ReadFromJdbc"},
        {"label": "WriteToJdbc", "value": "WriteToJdbc"},
        {"label": "ReadFromJson", "value": "ReadFromJson"},
        {"label": "WriteToJson", "value": "WriteToJson"},
        {"label": "ReadFromKafka", "value": "ReadFromKafka"},
        {"label": "WriteToKafka", "value": "WriteToKafka"},
        {"label": "ReadFromMySql", "value": "ReadFromMySql"},
        {"label": "WriteToMySql", "value": "WriteToMySql"},
        {"label": "ReadFromOracle", "value": "ReadFromOracle"},
        {"label": "WriteToOracle", "value": "WriteToOracle"},
        {"label": "ReadFromParquet", "value": "ReadFromParquet"},
        {"label": "WriteToParquet", "value": "WriteToParquet"},
        {"label": "ReadFromPostgres", "value": "ReadFromPostgres"},
        {"label": "WriteToPostgres", "value": "WriteToPostgres"},
        {"label": "ReadFromPubSub", "value": "ReadFromPubSub"},
        {"label": "WriteToPubSub", "value": "WriteToPubSub"},
        {"label": "ReadFromPubSubLite", "value": "ReadFromPubSubLite"},
        {"label": "WriteToPubSubLite", "value": "WriteToPubSubLite"},
        {"label": "ReadFromSpanner", "value": "ReadFromSpanner"},
        {"label": "WriteToSpanner", "value": "WriteToSpanner"},
        {"label": "ReadFromSqlServer", "value": "ReadFromSqlServer"},
        {"label": "WriteToSqlServer", "value": "WriteToSqlServer"},
        {"label": "ReadFromText", "value": "ReadFromText"},
        {"label": "WriteToText", "value": "WriteToText"},
    ]


def register_node_callbacks(app):
    @app.callback(Output("node-data", "children"), Input("network-graph", "tapNodeData"))
    def display_node_data(node_data):
        if not node_data:
            return "Click a node to see its details"

        # Create a formatted display of node data using dbc.Card with a custom background color
        details = [
            dbc.Row(
                [
                    dbc.Col(html.H5("Name:")),
                    dbc.Col(
                        dcc.Input(
                            id="node-id-input",
                            value=node_data["id"],
                            type="text",
                            style={
                                "width": "80%",
                            },
                        ),
                    ),
                ],
            ),
            dbc.Row(
                [
                    dbc.Col(html.H5("Type:")),
                    dbc.Col(
                        dcc.Dropdown(
                            id="node-type-dropdown",
                            options=get_node_type_options(),
                            value=node_data["type"],
                            style={
                                "width": "80%",
                            },
                        ),
                    ),
                ],
                className="mb-2",
            ),
            html.H5("Configuration:"),
            DashAceEditor(
                id="node-config-editor",
                value=yaml.dump(node_data["config"], indent=2),
                style={"width": "100%"},
                theme="tomorrow",
                mode="yaml",
            ),
        ]

        return html.Div(details)

    @app.callback(
        Output("network-graph", "elements", allow_duplicate=True),
        Output("yaml-content", "value", allow_duplicate=True),
        Input("node-config-editor", "value"),
        State("network-graph", "tapNodeData"),
        State("network-graph", "elements"),
        prevent_initial_call=True,
    )
    def save_node_config(config_value, node_data, elements):
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
                return updated_elements, yaml_content
            except yaml.YAMLError:
                return dash.no_update, dash.no_update
        return dash.no_update, dash.no_update

    @app.callback(
        Output("network-graph", "elements", allow_duplicate=True),
        Output("yaml-content", "value", allow_duplicate=True),
        Input("node-type-dropdown", "value"),
        State("network-graph", "tapNodeData"),
        State("network-graph", "elements"),
        prevent_initial_call=True,
    )
    def update_node_type(new_type, node_data, elements):
        if node_data:
            node_id = node_data["id"]
            updated_elements = []
            for element in elements:
                if element.get("data") and element["data"].get("id") == node_id:
                    element["data"]["type"] = new_type
                updated_elements.append(element)
            yaml_content = generate_yaml_content(updated_elements)
            return updated_elements, yaml_content
        return dash.no_update, dash.no_update

    @app.callback(
        Output("network-graph", "elements", allow_duplicate=True),
        Output("network-graph", "tapNodeData", allow_duplicate=True),
        Output("yaml-content", "value", allow_duplicate=True),
        Input("node-id-input", "value"),
        State("network-graph", "tapNodeData"),
        State("network-graph", "elements"),
        prevent_initial_call=True,
    )
    def update_node_id(new_node_id, node_data, elements):
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
            return updated_elements, node_data, yaml_content
        return dash.no_update, dash.no_update, dash.no_update
