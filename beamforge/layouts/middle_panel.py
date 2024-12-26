# third party libraries
import dash_cytoscape as cyto
import dash_resizable_panels as drp
from dash import html


def get_stylesheet():
    return [
        {
            "selector": "node",
            "style": {
                "shape": "roundrectangle",
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
                # Toolbar for zoom controls
                html.Div(
                    [
                        html.Button(
                            "Zoom In",
                            id="zoom-in",
                            n_clicks=0,
                            style={
                                "margin": "5px",
                                "padding": "10px",
                                "backgroundColor": "#007BFF",
                                "color": "white",
                                "border": "none",
                                "borderRadius": "4px",
                            },
                            className="hover-button",
                        ),
                        html.Button(
                            "Zoom Out",
                            id="zoom-out",
                            n_clicks=0,
                            style={
                                "margin": "5px",
                                "padding": "10px",
                                "backgroundColor": "#007BFF",
                                "color": "white",
                                "border": "none",
                                "borderRadius": "4px",
                            },
                            className="hover-button",
                        ),
                        html.Button(
                            "Reset View",
                            id="reset-view",
                            n_clicks=0,
                            style={
                                "margin": "5px",
                                "padding": "10px",
                                "backgroundColor": "#007BFF",
                                "color": "white",
                                "border": "none",
                                "borderRadius": "4px",
                            },
                            className="hover-button",
                        ),
                    ],
                    style={"margin-bottom": "10px", "position": "relative", "zIndex": 10},
                ),
                html.Div(
                    [
                        cyto.Cytoscape(
                            id="network-graph",
                            layout={"name": "dagre", "rankDir": "TB", "rankSep": 30, "nodeSep": 50, "padding": 10},
                            style={
                                "width": "100%",
                                "height": "calc(100vh - 120px)",
                                "position": "absolute",
                                "border": "1px solid #FFA500",
                                "borderRadius": "4px",
                                "backgroundColor": "#fff",
                            },
                            stylesheet=get_stylesheet(),
                            elements=[],
                            zoom=1.0,
                        ),
                    ]
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
