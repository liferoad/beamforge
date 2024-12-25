# standard libraries
import base64
import io

# third party libraries
from dash import Input, Output, State, html
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

        # Create a formatted display of node data
        details = [
            html.H4(f"Transform: {node_data['id']}"),
            html.P(f"Type: {node_data['type']}"),
            html.H5("Configuration:"),
            html.Pre(
                str(node_data["config"]),
                style={
                    "whiteSpace": "pre-wrap",
                    "wordBreak": "break-all",
                    "backgroundColor": "#f5f5f5",
                    "padding": "10px",
                    "borderRadius": "4px",
                },
            ),
        ]

        return html.Div(details)
