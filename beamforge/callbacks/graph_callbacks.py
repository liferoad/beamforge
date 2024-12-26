# standard libraries
import base64
import io
import json

# third party libraries
import dash_bootstrap_components as dbc
from dash import Input, Output, State, html
from dash_ace import DashAceEditor
from utils.yaml_parser import parse_beam_yaml


def register_graph_callbacks(app):
    # Clientside callback for fitting the graph
    app.clientside_callback(
        """
        function(elements) {
            if (elements && elements.length > 0) {
                const cy = document.getElementById('network-graph')._cyreg.cy;
                setTimeout(() => cy.fit(), 100);
            }
            return elements;
        }
        """,
        Output("network-graph", "elements"),
        Input("network-graph", "elements"),
    )

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
                    dbc.CardHeader(
                        f"Transform: {node_data['id']}", className="text-white"
                    ),  # Keep text white for contrast
                    dbc.CardBody(
                        [
                            html.H5(f"Type: {node_data['type']}", className="text-info"),
                            html.H5("Configuration:", className="mt-3"),
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
                style={"backgroundColor": "#f8f9fa", "border": "1px solid #dee2e6"},
                className="shadow-sm",
            )  # Light background with border
        ]

        return html.Div(details)
