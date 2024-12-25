# standard libraries
import base64
import io

# third party libraries
import dash
import dash_cytoscape as cyto
import networkx as nx
import yaml
from dash import Input, Output, State, dcc, html

# Register the dagre layout
cyto.load_extra_layouts()

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout
app.layout = html.Div(
    [
        # Main container with flexbox
        html.Div(
            [
                # Left Panel
                html.Div(
                    [
                        html.H3("Upload Beam YAML"),
                        dcc.Upload(
                            id="upload-data",
                            children=html.Div(["Drag and Drop or ", html.A("Select Beam YAML File")]),
                            style={
                                "width": "100%",
                                "height": "60px",
                                "lineHeight": "60px",
                                "borderWidth": "1px",
                                "borderStyle": "dashed",
                                "borderRadius": "5px",
                                "textAlign": "center",
                                "margin": "10px",
                            },
                            multiple=False,
                            accept=".yaml,.yml",
                        ),
                    ],
                    style={"width": "20%", "padding": "20px"},
                ),
                # Middle Panel
                html.Div(
                    [
                        html.H3("Pipeline Graph"),
                        cyto.Cytoscape(
                            id="network-graph",
                            layout={"name": "dagre"},
                            style={"width": "100%", "height": "600px"},
                            elements=[],
                        ),
                    ],
                    style={"width": "60%", "padding": "20px"},
                ),
                # Right Panel
                html.Div(
                    [
                        html.H3("Transform Details"),
                        html.Div(
                            id="node-info",
                            children=[html.P("Click a transform to see its details"), html.Div(id="node-data")],
                        ),
                    ],
                    style={"width": "20%", "padding": "20px"},
                ),
            ],
            style={"display": "flex", "flexDirection": "row", "height": "100vh"},
        )
    ]
)


def parse_beam_yaml(yaml_content):
    """Parse Beam YAML and create a NetworkX graph."""
    G = nx.DiGraph()
    data = yaml.safe_load(yaml_content)

    if "pipeline" not in data:
        raise ValueError("No pipeline section found in YAML")

    pipeline = data["pipeline"]
    transforms = pipeline.get("transforms", [])
    pipeline_type = pipeline.get("type", None)

    # Handle both chain and regular pipeline types
    if pipeline_type == "chain" or pipeline_type is None:
        prev_node = None
        for idx, transform in enumerate(transforms):
            node_id = transform.get("name", f"transform_{idx}")
            transform_type = transform.get("type", "Unknown")

            # Add node with transform details
            G.add_node(node_id, type=transform_type, config=transform.get("config", {}))

            # Connect to previous node if exists
            if prev_node is not None:
                G.add_edge(prev_node, node_id)

            prev_node = node_id

    return G


# Callback to handle file upload and update graph
@app.callback(Output("network-graph", "elements"), Input("upload-data", "contents"), State("upload-data", "filename"))
def update_graph(contents, filename):
    if contents is None:
        return []

    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)

    try:
        # Parse YAML and create NetworkX graph
        yaml_content = io.StringIO(decoded.decode("utf-8"))
        G = parse_beam_yaml(yaml_content)

        elements = []

        # Add nodes with styling
        for node in G.nodes():
            node_data = G.nodes[node]
            elements.append(
                {
                    "data": {"id": str(node), "label": f"{node}\n({node_data['type']})", "type": node_data["type"]},
                    "classes": "transform-node",
                }
            )

        # Add edges
        for source, target in G.edges():
            elements.append({"data": {"source": str(source), "target": str(target), "id": f"{source}-{target}"}})

        return elements
    except Exception as e:
        print(f"Error processing YAML file: {e}")
        return []


# Callback to update node information when clicked
@app.callback(Output("node-data", "children"), Input("network-graph", "tapNodeData"))
def display_node_data(node_data):
    if not node_data:
        return "No transform selected"

    return [html.H4(f"Transform: {node_data['label']}"), html.P(f"Type: {node_data['type']}")]


if __name__ == "__main__":
    app.run_server(debug=True)
