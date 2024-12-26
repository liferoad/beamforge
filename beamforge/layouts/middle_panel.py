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
                "background-color": "rgba(255, 165, 32, 0.5)",
                "border-color": "#B0B0B0",
                "border-width": "1px",
                "padding": "8px",
                "font-family": "Roboto, Arial, sans-serif",
                "font-size": "12px",
                "font-weight": "500",
                "text-wrap": "wrap",
                "color": "#FFFFFF",
            },
        },
        {
            "selector": "edge",
            "style": {
                "curve-style": "bezier",
                "target-arrow-shape": "triangle",
                "line-color": "#B0B0B0",
                "target-arrow-color": "#B0B0B0",
                "width": 1,
                "arrow-scale": 1.2,
            },
        },
        {
            "selector": "node:selected",
            "style": {
                "background-color": "rgba(255, 111, 32, 0.8)",
                "border-color": "#000000",
                "border-width": "1px",
            },
        },
    ]


def create_middle_panel():
    return drp.Panel(
        html.Div(
            [
                cyto.Cytoscape(
                    id="network-graph",
                    layout={"name": "dagre", "rankDir": "TB", "rankSep": 30, "nodeSep": 50, "padding": 10},
                    style={
                        "width": "100%",
                        "height": "calc(100vh - 100px)",
                        "position": "absolute",
                        "border": "1px solid #ddd",
                        "borderRadius": "4px",
                        "backgroundColor": "#fff",
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
