# standard libraries
import base64
import io

# third party libraries
import dash
from dash import Input, Output, State
from utils.graph_utils import format_log_with_timestamp, generate_yaml_content
from utils.yaml_parser import parse_beam_yaml


def register_graph_callbacks(app):
    @app.callback(
        Output("network-graph", "elements", allow_duplicate=True),
        Output("yaml-content", "value", allow_duplicate=True),
        Input("upload-data", "contents"),
        State("upload-data", "filename"),
        prevent_initial_call=True,
    )
    def update_graph(contents, filename):
        if contents is None:
            return [], ""

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

            return elements, decoded.decode("utf-8")
        except Exception as e:
            print(e)
            return [], ""

    @app.callback(
        Output("network-graph", "zoom"),
        Output("network-graph", "layout"),
        Input("zoom-in", "n_clicks"),
        Input("zoom-out", "n_clicks"),
        Input("reset-view", "n_clicks"),
        Input("network-graph", "zoom"),
        prevent_initial_call=True,
    )
    def zoom_graph(zoom_in_clicks, zoom_out_clicks, reset_view_clicks, current_zoom):
        ctx = dash.callback_context

        if not ctx.triggered:
            return dash.no_update, dash.no_update

        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

        # Use the current zoom level as the base
        zoom_level = current_zoom if current_zoom is not None else 1.0  # Default to 1.0 if None
        layout = None

        if triggered_id == "zoom-in":
            zoom_level += 0.1  # Increase zoom level
        elif triggered_id == "zoom-out":
            zoom_level -= 0.1  # Decrease zoom level
            zoom_level = max(0.1, zoom_level)  # Prevent zooming out too much
        elif triggered_id == "reset-view":
            zoom_level = 1.0  # Reset zoom to default
            layout = {
                "name": "dagre",
                "rankDir": "TB",
                "rankSep": 30,
                "nodeSep": 50,
                "padding": 10,
                "animate": True,
                "fit": True,
                "spacingFactor": 1.5,
            }

        return zoom_level, layout

    @app.callback(
        Output("delete-selected", "disabled"),
        Input("network-graph", "selectedNodeData"),
        Input("network-graph", "selectedEdgeData"),
    )
    def enable_delete_button(selected_nodes, selected_edges):
        return not (selected_nodes or selected_edges)

    @app.callback(
        Output("network-graph", "elements", allow_duplicate=True),
        Output("graph-log-table", "data", allow_duplicate=True),
        Output("yaml-content", "value", allow_duplicate=True),
        Input("delete-selected", "n_clicks"),
        State("network-graph", "elements"),
        State("network-graph", "selectedNodeData"),
        State("network-graph", "selectedEdgeData"),
        State("graph-log-table", "data"),
        prevent_initial_call=True,
    )
    def remove_selected_elements(n_clicks, elements, selected_nodes, selected_edges, table_data):
        if n_clicks > 0:
            node_ids_to_remove = {node["id"] for node in selected_nodes} if selected_nodes else set()
            edge_ids_to_remove = (
                {(edge["source"], edge["target"]) for edge in selected_edges} if selected_edges else set()
            )

            deleted_nodes = [node["id"] for node in selected_nodes] if selected_nodes else []
            deleted_edges = (
                ["(%s, %s)" % (edge["source"], edge["target"]) for edge in selected_edges] if selected_edges else []
            )

            formatted_logs = []
            if deleted_nodes:
                formatted_logs.extend(format_log_with_timestamp("Deleted nodes: %s\n" % ", ".join(deleted_nodes)))
            if deleted_edges:
                formatted_logs.extend(format_log_with_timestamp("Deleted edges: %s\n" % ", ".join(deleted_edges)))

            new_elements = []
            for element in elements:
                if "source" in element["data"]:  # It's an edge
                    if (
                        element["data"]["source"],
                        element["data"]["target"],
                    ) not in edge_ids_to_remove and (
                        element["data"]["target"],
                        element["data"]["source"],
                    ) not in edge_ids_to_remove:
                        new_elements.append(element)
                elif "id" in element["data"]:  # It's a node
                    if element["data"]["id"] not in node_ids_to_remove:
                        new_elements.append(element)

            # Generate YAML content
            yaml_string = generate_yaml_content(new_elements)

            return new_elements, table_data + formatted_logs, yaml_string
        return elements, table_data, dash.no_update

    @app.callback(
        Output("network-graph", "elements", allow_duplicate=True),
        Output("graph-log-table", "data", allow_duplicate=True),
        Output("yaml-content", "value", allow_duplicate=True),
        Input("add-node-button", "n_clicks"),
        State("network-graph", "elements"),
        State("graph-log-table", "data"),
        prevent_initial_call=True,
    )
    def add_new_node(n_clicks, elements, table_data):
        if n_clicks > 0:
            # Initialize table_data as an empty list if it's None
            if table_data is None:
                table_data = []

            new_node_id = "node-%s" % (len([el for el in elements if "source" not in el["data"]]) + 1)
            new_node = {"data": {"id": new_node_id, "type": "UNKNOWN", "config": {}}}
            elements.append(new_node)
            formatted_logs = format_log_with_timestamp(f"Added node: {new_node_id}\n")

            yaml_string = generate_yaml_content(elements)
            return elements, table_data + formatted_logs, yaml_string

        return elements, table_data, dash.no_update

    @app.callback(
        Output("add-edge-button", "disabled"),
        Input("network-graph", "selectedNodeData"),
    )
    def enable_add_edge_button(selected_nodes):
        return not selected_nodes or len(selected_nodes) != 2

    @app.callback(
        Output("network-graph", "elements", allow_duplicate=True),
        Output("graph-log-table", "data", allow_duplicate=True),
        Output("yaml-content", "value", allow_duplicate=True),
        Input("add-edge-button", "n_clicks"),
        State("network-graph", "elements"),
        State("network-graph", "selectedNodeData"),
        State("graph-log-table", "data"),
        State("yaml-content", "value"),
        prevent_initial_call=True,
    )
    def add_edge_between_nodes(n_clicks, elements, selected_nodes, table_data, yaml_string):
        if n_clicks > 0 and selected_nodes and len(selected_nodes) == 2:
            source_id = selected_nodes[0]["id"]
            target_id = selected_nodes[1]["id"]

            # Check if the edge already exists (undirected graph)
            edge_exists = any(
                (el["data"].get("source") == source_id and el["data"].get("target") == target_id)
                or (el["data"].get("source") == target_id and el["data"].get("target") == source_id)
                for el in elements
                if "source" in el["data"]
            )

            if not edge_exists:
                new_edge = {"data": {"source": source_id, "target": target_id}}
                elements.append(new_edge)
                formatted_logs = format_log_with_timestamp(f"Added edge between {source_id} and {target_id}\n")
            else:
                formatted_logs = format_log_with_timestamp(f"Edge already exists between {source_id} and {target_id}\n")

            yaml_string = generate_yaml_content(elements)
            return elements, table_data + formatted_logs, yaml_string

        return elements, table_data, dash.no_update
