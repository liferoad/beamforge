# third party libraries
import dash_cytoscape as cyto
import dash_resizable_panels as drp
from dash import dash_table, dcc, html


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
        [
            drp.PanelGroup(
                [
                    drp.Panel(
                        [
                            # Toolbar for zoom/graph controls
                            html.Div(
                                [
                                    html.Div(
                                        [
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
                                            html.Button(
                                                "Delete Selected",
                                                id="delete-selected",
                                                n_clicks=0,
                                                className="beam-button",
                                                disabled=True,
                                            ),
                                        ],
                                        style={"float": "left"},
                                    ),  # Added float left to put other buttons to the left
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
                                        ],
                                        style={"float": "right"},
                                    ),  # Added float right to put zoom buttons to the right
                                ],
                                style={
                                    "margin-bottom": "10px",
                                    "display": "flex",
                                    "justifyContent": "space-between",
                                    "width": "100%",
                                },
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
                                            "fit": True,
                                            "spacingFactor": 1.5,
                                        },
                                        style={
                                            "width": "100%",
                                            "height": "100%",
                                            "position": "absolute",
                                            "top": 0,
                                            "left": 0,
                                            "borderRadius": "4px",
                                            "backgroundColor": "white",
                                        },
                                        stylesheet=get_stylesheet(),
                                        elements=[],
                                        zoom=1,
                                        pan={"x": 50, "y": 50},
                                    ),
                                ],
                                style={
                                    "width": "100%",
                                    "height": "calc(75vh)",
                                    "position": "relative",
                                    "overflow": "hidden",
                                },
                            ),
                        ],
                        defaultSizePercentage=80,
                    ),
                    drp.PanelResizeHandle(html.Div(className="resize-handle-vertical")),
                    drp.Panel(
                        html.Div(
                            [
                                dcc.Loading(
                                    id="graph-log-table-loading",
                                    type="default",
                                    color="#FF6F20",
                                    children=[
                                        dash_table.DataTable(
                                            id="graph-log-table",
                                            columns=[
                                                {
                                                    "name": "Timestamp",
                                                    "id": "Timestamp",
                                                },
                                                {
                                                    "name": "Log Message",
                                                    "id": "Log Message",
                                                },
                                            ],
                                            style_table={
                                                "width": "100%",
                                                "height": "100%",
                                                "overflowY": "auto",
                                                "overflowX": "auto",
                                                "resize": "vertical",
                                                "minHeight": "10vh",
                                                "maxHeight": "50vh",
                                                "backgroundColor": "white",
                                                "borderRadius": "4px",
                                                "boxShadow": "0 2px 6px rgba(0, 0, 0, 0.1)",
                                            },
                                            style_data={
                                                "whiteSpace": "normal",
                                                "height": "auto",
                                                "textAlign": "left",
                                                "fontFamily": "Roboto, Arial, sans-serif",
                                                "fontSize": "14px",
                                                "border": "0px solid #B0B0B0",
                                                "padding": "10px",
                                            },
                                            style_header={
                                                "backgroundColor": "#F5F5F5",
                                                "fontFamily": "Roboto, Arial, sans-serif",
                                                "fontSize": "14px",
                                                "fontWeight": "500",
                                                "padding": "10px",
                                                "border": "none",
                                            },
                                            style_cell={
                                                "padding": "10px",
                                                "width": "180px",
                                                "fontFamily": "Roboto, Arial, sans-serif",
                                            },
                                            style_data_conditional=[
                                                {
                                                    "if": {"row_index": "odd"},
                                                    "backgroundColor": "rgb(240, 240, 240)",
                                                },
                                            ],
                                            style_cell_conditional=[
                                                {
                                                    "if": {"column_id": "Timestamp"},
                                                    "width": "200px",
                                                },
                                                {
                                                    "if": {"column_id": "Log Message"},
                                                    "width": "auto",
                                                },
                                            ],
                                            sort_action="native",
                                            sort_by=[
                                                {
                                                    "column_id": "Timestamp",
                                                    "direction": "desc",
                                                }
                                            ],
                                        )
                                    ],
                                ),
                            ]
                        ),
                        defaultSizePercentage=20,
                    ),
                ],
                direction="vertical",
            ),
        ],
    )
