# standard libraries
import re
from datetime import datetime

# third party libraries
import yaml


def generate_yaml_content(elements):
    yaml_data = {"pipeline": {}}
    nodes_data = {}
    for elem in elements:
        if "source" in elem["data"]:
            continue  # Edges are handled separately
        else:
            node_id = elem["data"]["id"]
            nodes_data[node_id] = {
                "type": elem["data"].get("type", "Unknown"),
                "name": node_id,
                "config": elem["data"].get("config", {}),
            }
    for elem in elements:
        if "source" in elem["data"]:
            target_node_id = elem["data"]["target"]
            source_node_id = elem["data"]["source"]
            if target_node_id in nodes_data:
                # Let's assume the edge 'source' corresponds to the input name
                if "input" not in nodes_data[target_node_id]:
                    nodes_data[target_node_id]["input"] = {}
                nodes_data[target_node_id]["input"][elem["data"]["source"]] = source_node_id

    yaml_data["pipeline"]["transforms"] = list(nodes_data.values())

    yaml_string = yaml.dump(yaml_data, default_flow_style=False, sort_keys=False)
    return yaml_string


def format_log_with_timestamp(log_message):
    if not log_message:
        return []

    table_data = []
    for log in log_message.splitlines():
        match = re.search(r"\*\*`\[(.*?)\]`\*\*", log)
        if match:
            timestamp = match.group(1)
            message = log[match.end() :].strip()
        else:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = log

        table_data.append({"Timestamp": timestamp, "Log Message": message})

    # Sort logs by timestamp (latest to oldest)
    table_data.sort(
        key=lambda item: datetime.strptime(item["Timestamp"], "%Y-%m-%d %H:%M:%S"),
        reverse=True,
    )

    return table_data
