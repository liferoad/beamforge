# standard libraries
import base64
import io
import json

# third party libraries
import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, html
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
                                style={
                                    "color": "#FF6F20",
                                },
                            ),
                            html.H5(f"Type: {node_data['type']}"),
                            html.H5("Configuration:"),
                            DashAceEditor(
                                value=json.dumps(node_data["config"], indent=4),
                                style={"width": "100%", "height": "200px"},
                                theme="tomorrow",
                                mode="json",
                                readOnly=True,
                            ),
                        ]
                    ),
                ],
                style={"backgroundColor": "#F5F5F5", "border": "1px solid #dee2e6"},
                className="shadow-sm",
            )  # Light background with border
        ]

        return html.Div(details)

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
