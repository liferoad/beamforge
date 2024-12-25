# standard libraries
import base64
import io

# third party libraries
import dash
import dash_cytoscape as cyto
import dash_resizable_panels as drp
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
        # Main container
        drp.PanelGroup(
            [
                # Left Panel
                drp.Panel(
                    html.Div(
                        [
                            html.H3("Upload Beam YAML"),
                            dcc.Upload(
                                id="upload-data",
                                children=html.Div(["Drag and Drop or ", html.A("Select Beam YAML File")]),
                                style={
                                    "width": "80%",
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
                            # Replace Textarea with a Div containing pre element
                            html.Div(
                                [
                                    html.Pre(
                                        id="yaml-content",
                                        style={
                                            "width": "95%",
                                            "margin": "10px",
                                            "fontFamily": "monospace",
                                            "whiteSpace": "pre-wrap",
                                            "wordWrap": "break-word",
                                            "backgroundColor": "#f5f5f5",
                                            "padding": "10px",
                                            "border": "1px solid #ddd",
                                            "borderRadius": "4px",
                                            "overflow": "auto",
                                            "maxHeight": "calc(100vh - 150px)",  # Adjust based on other elements
                                        },
                                    ),
                                ],
                                style={"height": "calc(100% - 100px)", "overflow": "auto"},
                            ),
                        ]
                    ),
                    defaultSizePercentage=20,
                ),
                drp.PanelResizeHandle(className="panel-resize-handle"),
                # Middle Panel
                drp.Panel(
                    html.Div(
                        [
                            html.H3("Pipeline Graph"),
                            cyto.Cytoscape(
                                id="network-graph",
                                layout={"name": "dagre", "rankDir": "TB", "rankSep": 30, "nodeSep": 50, "padding": 10},
                                style={
                                    "width": "100%",
                                    "height": "calc(100vh - 100px)",
                                    "position": "absolute",
                                },
                                stylesheet=[
                                    {
                                        "selector": "node",
                                        "style": {
                                            "shape": "rectangle",
                                            "content": "data(id)",
                                            "text-valign": "center",
                                            "text-halign": "center",
                                            "width": "150px",  # Increased width for better readability
                                            "height": "40px",  # Increased height
                                            "background-color": "#e3f2fd",  # Light blue background
                                            "border-color": "#1976d2",  # Darker blue border
                                            "border-width": "2px",
                                            "padding": "8px",
                                            "font-family": "Roboto, Arial, sans-serif",  # Modern font
                                            "font-size": "12px",  # Larger font
                                            "font-weight": "500",  # Semi-bold text
                                            "text-wrap": "wrap",
                                            "color": "#1565c0",  # Dark blue text
                                        },
                                    },
                                    {
                                        "selector": "edge",
                                        "style": {
                                            "curve-style": "bezier",
                                            "target-arrow-shape": "triangle",
                                            "line-color": "#90caf9",  # Light blue edges
                                            "target-arrow-color": "#90caf9",
                                            "width": 1.5,  # Slightly thicker edges
                                            "arrow-scale": 1.2,  # Larger arrows
                                        },
                                    },
                                    {
                                        "selector": "node:selected",  # Style for selected nodes
                                        "style": {
                                            "background-color": "#bbdefb",
                                            "border-color": "#0d47a1",
                                            "border-width": "3px",
                                        },
                                    },
                                ],
                                elements=[],
                            ),
                        ],
                        style={
                            "height": "100%",
                            "position": "relative",
                            "display": "flex",
                            "flexDirection": "column",
                        },
                    ),
                    defaultSizePercentage=60,
                ),
                drp.PanelResizeHandle(className="panel-resize-handle"),
                # Right Panel
                drp.Panel(
                    html.Div(
                        [
                            html.H3("Transform Details"),
                            html.Div(
                                id="node-info",
                                children=[html.P("Click a transform to see its details"), html.Div(id="node-data")],
                            ),
                        ]
                    ),
                    defaultSizePercentage=20,
                ),
            ],
            direction="horizontal",
        ),
        # Add a dummy div to trigger the reset
        html.Div(id="reset-trigger", style={"display": "none"}),
    ],
    style={"height": "100vh"},
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


# Add the clientside callback for fitting the graph
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


# Update the main graph callback
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
        yaml_content = io.StringIO(decoded.decode("utf-8"))
        G = parse_beam_yaml(yaml_content)

        elements = []

        # Add nodes with styling
        for node in G.nodes():
            node_data = G.nodes[node]
            elements.append(
                {
                    "data": {"id": str(node), "type": node_data["type"]},
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

    return [html.H4(f"Transform: {node_data['id']}"), html.P(f"Type: {node_data['type']}")]


# Update the callback to work with html.Pre
@app.callback(
    Output("yaml-content", "children"),  # Changed from "value" to "children"
    Input("upload-data", "contents"),
)
def update_yaml_content(contents):
    if contents is None:
        return "YAML content will appear here..."

    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)

    try:
        # Parse YAML to ensure it's valid and format it
        yaml_dict = yaml.safe_load(decoded)
        formatted_yaml = yaml.dump(yaml_dict, default_flow_style=False, sort_keys=False)
        return formatted_yaml
    except Exception as e:
        return f"Error processing YAML file: {str(e)}"


if __name__ == "__main__":
    app.run_server(debug=True)
