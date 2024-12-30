# third party libraries
import yaml


def generate_yaml_content(elements):
    yaml_data = {"nodes": [], "edges": []}
    for elem in elements:
        if "source" in elem["data"]:
            yaml_data["edges"].append({"source": elem["data"]["source"], "target": elem["data"]["target"]})
        else:
            yaml_data["nodes"].append(
                {
                    "id": elem["data"]["id"],
                    "type": elem["data"].get("type", "Unknown"),
                    "config": elem["data"].get("config", {}),
                }
            )
    yaml_string = yaml.dump(yaml_data, default_flow_style=False, sort_keys=False)
    return yaml_string
