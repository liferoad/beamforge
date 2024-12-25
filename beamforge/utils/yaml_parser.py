# third party libraries
import networkx as nx
import yaml


def parse_beam_yaml(yaml_content):
    """Parse Beam YAML and create a NetworkX graph."""
    G = nx.DiGraph()
    data = yaml.safe_load(yaml_content)

    if "pipeline" not in data:
        raise ValueError("No pipeline section found in YAML")

    pipeline = data["pipeline"]
    transforms = pipeline.get("transforms", [])
    pipeline_type = pipeline.get("type", None)

    if pipeline_type == "chain" or pipeline_type is None:
        prev_node = None
        for idx, transform in enumerate(transforms):
            node_id = transform.get("name", f"transform_{idx}")
            transform_type = transform.get("type", "Unknown")
            G.add_node(node_id, type=transform_type, config=transform.get("config", {}))
            if prev_node is not None:
                G.add_edge(prev_node, node_id)
            prev_node = node_id

    return G
