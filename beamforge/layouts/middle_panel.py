# third party libraries
import dash_cytoscape as cyto
import dash_resizable_panels as drp
from dash import html


def get_stylesheet():
    return [
        {
            "selector": "node",
            "style": {
                "shape": "rectangle",
                "content": "data(id)",
                "text-valign": "center",
                "text-halign": "center",
                "width": "150px",
                "height": "40px",
                "background-color": "#e3f2fd",
                "border-color": "#1976d2",
                "border-width": "2px",
                "padding": "8px",
                "font-family": "Roboto, Arial, sans-serif",
                "font-size": "12px",
                "font-weight": "500",
                "text-wrap": "wrap",
                "color": "#1565c0",
            },
        },
        {
            "selector": "edge",
            "style": {
                "curve-style": "bezier",
                "target-arrow-shape": "triangle",
                "line-color": "#90caf9",
                "target-arrow-color": "#90caf9",
                "width": 1.5,
                "arrow-scale": 1.2,
            },
        },
        {
            "selector": "node:selected",
            "style": {
                "background-color": "#bbdefb",
                "border-color": "#0d47a1",
                "border-width": "3px",
            },
        },
    ]


def create_middle_panel():
    return drp.Panel(
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
                    stylesheet=get_stylesheet(),
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
    )
