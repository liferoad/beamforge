# third party libraries
import dash_cytoscape as cyto
import dash_resizable_panels as drp
from dash import dcc, html


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
            "selector": "edge:selected",
            "style": {
                "line-color": "black",
                "target-arrow-color": "black",
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
                            className="beam-button",
                        ),
                        html.Button(
                            "Zoom Out",
                            id="zoom-out",
                            n_clicks=0,
                            className="beam-button",
                        ),
                        html.Button(
                            "Reset View",
                            id="reset-view",
                            n_clicks=0,
                            className="beam-button",
                        ),
                        html.Button(
                            "Delete Selected",
                            id="delete-selected",
                            n_clicks=0,
                            className="beam-button",
                            disabled=True,
                        ),
                        html.Button(
                            "Add Node",
                            id="add-node-button",
                            className="beam-button",
                        ),
                        html.Button(
                            "Add Edge",
                            id="add-edge-button",
                            n_clicks=0,
                            className="beam-button",
                            disabled=True,
                        ),
                    ],
                    style={"margin-bottom": "10px", "position": "relative", "zIndex": 10},
                ),
                html.Div(
                    [
                        cyto.Cytoscape(
                            id="network-graph",
                            layout={
                                "name": "dagre",
                                "rankDir": "TB",
                                "rankSep": 30,
                                "nodeSep": 50,
                                "padding": 10,
                                "animate": True,
                            },
                            style={
                                "width": "100%",
                                "height": "calc(80vh - 120px)",
                                "overflow": "auto",
                                "borderRadius": "4px",
                                "backgroundColor": "#F5F5F5",
                            },
                            stylesheet=get_stylesheet(),
                            elements=[],
                            zoom=1.0,
                            pan={"x": 0, "y": 0},
                        ),
                    ]
                ),
                html.Div(
                    [
                        dcc.Textarea(
                            id="graph-log",
                            value="",
                            readOnly=True,
                            style={
                                "width": "100%",
                                "height": "200px",
                                "overflow": "auto",
                                "fontFamily": "monospace",
                                "border": "1px solid #ccc",
                                "resize": "vertical",
                            },
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
