# standard libraries
import base64
import io
import json

# third party libraries
import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html
from dash_ace import DashAceEditor
from utils.yaml_parser import parse_beam_yaml


def register_graph_callbacks(app):
    @app.callback(
        Output("network-graph", "elements", allow_duplicate=True),
        Input("upload-data", "contents"),
        State("upload-data", "filename"),
        prevent_initial_call=True,
    )
    def update_graph(contents, filename):
        if contents is None:
            return []

        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)

        try:
            # Parse YAML and create NetworkX graph
            G = parse_beam_yaml(io.StringIO(decoded.decode("utf-8")))

            # Convert NetworkX graph to Cytoscape format
            elements = []

            # Add nodes
            for node in G.nodes(data=True):
                node_id = node[0]
                node_data = node[1]
                elements.append(
                    {
                        "data": {
                            "id": node_id,
                            "type": node_data.get("type", "Unknown"),
                            "config": node_data.get("config", {}),
                        }
                    }
                )

            # Add edges
            for edge in G.edges():
                elements.append({"data": {"source": edge[0], "target": edge[1]}})

            return elements
        except Exception as e:
            print(e)
            return []

    @app.callback(Output("node-data", "children"), Input("network-graph", "tapNodeData"))
    def display_node_data(node_data):
        if not node_data:
            return "Click a node to see its details"

        # Create a formatted display of node data using dbc.Card with a custom background color
        details = [
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            html.H4(
                                f"Transform: {node_data['id']}",
                                style={"color": "#FF6F20"},
                            ),
                            dcc.Dropdown(
                                id="node-type-dropdown",
                                options=[
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
                                ],
                                value=node_data["type"],
                            ),
                            html.H5("Configuration:"),
                            DashAceEditor(
                                id="node-config-editor",
                                value=json.dumps(node_data["config"], indent=2),
                                style={"width": "100%", "height": "200px"},
                                theme="tomorrow",
                                mode="json",
                            ),
                        ]
                    ),
                ],
                style={"backgroundColor": "#F5F5F5", "border": "1px solid #dee2e6"},
                className="shadow-sm",
            )
        ]

        return html.Div(details)

    @app.callback(
        Output("network-graph", "elements", allow_duplicate=True),
        Input("node-config-editor", "value"),
        State("network-graph", "tapNodeData"),
        State("network-graph", "elements"),
        prevent_initial_call=True,
    )
    def save_node_config(config_value, node_data, elements):
        if node_data:
            try:
                new_config = json.loads(config_value)
                node_id = node_data["id"]
                updated_elements = []
                for element in elements:
                    if element.get("data") and element["data"].get("id") == node_id:
                        element["data"]["config"] = new_config
                    updated_elements.append(element)
                return updated_elements
            except json.JSONDecodeError:
                return dash.no_update
        return dash.no_update

    @app.callback(
        Output("network-graph", "zoom"),
        Input("zoom-in", "n_clicks"),
        Input("zoom-out", "n_clicks"),
        Input("reset-view", "n_clicks"),
        Input("network-graph", "zoom"),
        prevent_initial_call=True,
    )
    def zoom_graph(zoom_in_clicks, zoom_out_clicks, reset_view_clicks, current_zoom):
        ctx = dash.callback_context

        if not ctx.triggered:
            return dash.no_update

        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

        # Use the current zoom level as the base
        zoom_level = current_zoom if current_zoom is not None else 1.0  # Default to 1.0 if None

        if triggered_id == "zoom-in":
            zoom_level += 0.1  # Increase zoom level
        elif triggered_id == "zoom-out":
            zoom_level -= 0.1  # Decrease zoom level
            zoom_level = max(0.1, zoom_level)  # Prevent zooming out too much
        elif triggered_id == "reset-view":
            zoom_level = 1.0  # Reset zoom to default

        return zoom_level

    @app.callback(
        Output("graph-log", "value"),
        Input("network-graph", "tapNode"),
        Input("network-graph", "tapEdge"),
        Input("graph-log", "value"),
        # Add other inputs as needed for more interactions
    )
    def update_log(tapNode, tapEdge, log_message):
        if tapNode:
            log_message += f"Node tapped: {tapNode['data']['id']}\n"
        if tapEdge:
            log_message += f"Edge tapped: {tapEdge['data']['id']}\n"
        # Add other log messages based on graph interactions
        return log_message

    @app.callback(
        Output("delete-selected", "disabled"),
        Input("network-graph", "selectedNodeData"),
        Input("network-graph", "selectedEdgeData"),
    )
    def enable_delete_button(selected_nodes, selected_edges):
        return not (selected_nodes or selected_edges)

    @app.callback(
        Output("network-graph", "elements"),
        Output("graph-log", "value", allow_duplicate=True),
        Input("delete-selected", "n_clicks"),
        State("network-graph", "elements"),
        State("network-graph", "selectedNodeData"),
        State("network-graph", "selectedEdgeData"),
        State("graph-log", "value"),
        prevent_initial_call=True,
    )
    def remove_selected_elements(n_clicks, elements, selected_nodes, selected_edges, log_message):
        if n_clicks > 0:
            node_ids_to_remove = {node["id"] for node in selected_nodes} if selected_nodes else set()
            edge_ids_to_remove = (
                {(edge["source"], edge["target"]) for edge in selected_edges} if selected_edges else set()
            )

            deleted_nodes = [node["id"] for node in selected_nodes] if selected_nodes else []
            deleted_edges = (
                [f"({edge['source']}, {edge['target']})" for edge in selected_edges] if selected_edges else []
            )

            if deleted_nodes:
                log_message += f"Deleted nodes: {', '.join(deleted_nodes)}\n"
            if deleted_edges:
                log_message += f"Deleted edges: {', '.join(deleted_edges)}\n"

            new_elements = []
            for element in elements:
                if "source" in element["data"]:  # It's an edge
                    if (element["data"]["source"], element["data"]["target"]) not in edge_ids_to_remove and (
                        element["data"]["target"],
                        element["data"]["source"],
                    ) not in edge_ids_to_remove:
                        new_elements.append(element)
                elif "id" in element["data"]:  # It's a node
                    if element["data"]["id"] not in node_ids_to_remove:
                        new_elements.append(element)
            return new_elements, log_message
        return new_elements, log_message

    @app.callback(
        Output("network-graph", "elements", allow_duplicate=True),
        Output("graph-log", "value", allow_duplicate=True),
        Input("add-node-button", "n_clicks"),
        State("network-graph", "elements"),
        State("graph-log", "value"),
        prevent_initial_call=True,
    )
    def add_new_node(n_clicks, elements, log_message):
        if n_clicks > 0:
            new_node_id = f"node-{len([el for el in elements if 'source' not in el['data']]) + 1}"
            elements = elements + [{"data": {"id": new_node_id, "type": "UNKNOWN", "config": {}}}]
            log_message += f"Added node: {new_node_id}\n"
        return elements, log_message

    @app.callback(
        Output("add-edge-button", "disabled"),
        Input("network-graph", "selectedNodeData"),
    )
    def enable_add_edge_button(selected_nodes):
        return not selected_nodes or len(selected_nodes) != 2

    @app.callback(
        Output("network-graph", "elements", allow_duplicate=True),
        Output("graph-log", "value", allow_duplicate=True),
        Input("add-edge-button", "n_clicks"),
        State("network-graph", "elements"),
        State("network-graph", "selectedNodeData"),
        State("graph-log", "value"),
        prevent_initial_call=True,
    )
    def add_edge_between_nodes(n_clicks, elements, selected_nodes, log_message):
        if n_clicks > 0 and selected_nodes and len(selected_nodes) == 2:
            source_id = selected_nodes[0]["id"]
            target_id = selected_nodes[1]["id"]

            # Check if the edge already exists (undirected graph)
            edge_exists = any(
                (el["data"].get("source") == source_id and el["data"].get("target") == target_id)
                or (el["data"].get("source") == target_id and el["data"].get("target") == source_id)
                for el in elements
                if "source" in el["data"]
            )

            if not edge_exists:
                new_edge = {"data": {"source": source_id, "target": target_id}}
                elements.append(new_edge)
                log_message += f"Added edge between {source_id} and {target_id}\n"
            else:
                log_message += f"Edge already exists between {source_id} and {target_id}\n"

        return elements, log_message
