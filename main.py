# standard libraries
from typing import Dict

# third party libraries
import mesop as me
import networkx as nx
import yaml

yaml_content = None


@me.stateclass
class State:
    file: me.UploadedFile
    yaml_content: dict = None


def handle_upload(event: me.UploadEvent):
    state = me.state(State)
    state.file = event.file
    # Parse YAML content
    # state.yaml_content = yaml.safe_load(event.file.getvalue().decode())
    global yaml_content
    yaml_content = yaml.safe_load(event.file.getvalue().decode())


def build_dag_from_yaml(yaml_content: Dict) -> nx.DiGraph:
    """
    Build a DAG from YAML pipeline content.

    Args:
        yaml_content: Parsed YAML dictionary containing pipeline configuration

    Returns:
        nx.DiGraph: A directed acyclic graph representing the pipeline
    """
    G = nx.DiGraph()

    # Get the pipeline section
    pipeline = yaml_content.get("pipeline", {})

    if pipeline.get("type") == "chain" or pipeline.get("type") is None:
        transforms = pipeline.get("transforms", [])
        # For chain type, create nodes for each transform and connect them sequentially
        prev_node = None
        for i, transform in enumerate(transforms):
            node_id = f"{transform.get('type')}_{i}"
            node_attrs = {
                "type": transform.get("type"),
                "name": transform.get("name", ""),
                "config": transform.get("config", {}),
            }
            # Add node to graph
            G.add_node(node_id, **node_attrs)

            # If there's a previous node, connect it to current node
            if prev_node is not None:
                G.add_edge(prev_node, node_id)

            prev_node = node_id

    return G


def process_yaml_pipeline(yaml_content):
    if yaml_content:
        dag = build_dag_from_yaml(yaml_content)

        # Print DAG information
        me.text("DAG Nodes:")
        for node in dag.nodes(data=True):
            me.text(f"Node: {node[0]}")
            me.text(f"Attributes: {node[1]}")

        me.text("\nDAG Edges:")
        for edge in dag.edges():
            me.text(f"{edge[0]} -> {edge[1]}")


@me.page(path="/")
def app():
    global yaml_content

    with me.box(style=me.Style(display="grid", grid_template_columns="1fr 2fr 1fr", height="100%")):
        # Left Sidebar
        with me.box(style=me.Style(background="#f0f0f0", padding=me.Padding.all(24), overflow_y="auto")):
            me.text("Upload YAML")
            with me.content_uploader(
                accepted_file_types=["text/yaml"],
                on_upload=handle_upload,
                type="icon",
                style=me.Style(font_weight="bold"),
            ):
                me.icon("upload")
            me.divider()
            if yaml_content:
                # Display the parsed YAML content
                me.textarea(
                    value=yaml.dump(yaml_content, default_flow_style=False, sort_keys=False),
                    appearance="outline",
                    style=me.Style(width="100%"),
                    autosize=True,
                )
        # Main content
        with me.box(style=me.Style(padding=me.Padding.all(24), overflow_y="auto")):
            me.text("YAML Content:")
            if yaml_content:
                me.text("\nPipeline DAG Analysis:")
                process_yaml_pipeline(yaml_content)

        # Right Sidebar
        with me.box(style=me.Style(background="#f0f0f0", padding=me.Padding.all(24), overflow_y="auto")):
            me.text("Right Sidebar")
