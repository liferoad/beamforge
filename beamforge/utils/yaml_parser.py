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

    # Check if pipeline_type is None and input is not specified
    if pipeline_type is None:
        # If no input is specified, treat it as a chain
        if all("input" not in transform for transform in transforms):
            pipeline_type = "chain"

    if pipeline_type == "chain":
        prev_node = None
        for idx, transform in enumerate(transforms):
            transform_type = transform.get("type", "Unknown")
            node_id = transform.get("name", transform_type)
            if node_id in G:
                node_id = f"{node_id}_{idx}"
            G.add_node(node_id, type=transform_type, config=transform.get("config", {}))
            if prev_node is not None:
                G.add_edge(prev_node, node_id)
            prev_node = node_id

    else:
        for idx, transform in enumerate(transforms):
            transform_type = transform.get("type", "Unknown")
            node_id = transform.get("name", transform_type)
            if node_id in G:
                node_id = f"{node_id}_{idx}"
            G.add_node(node_id, type=transform_type, config=transform.get("config", {}))

            # Handle input connections for non-linear pipelines
            inputs = transform.get("input", None)
            if inputs:
                if isinstance(inputs, dict):
                    for key, value in inputs.items():
                        G.add_edge(value, node_id)
                else:
                    G.add_edge(inputs, node_id)

    return G
