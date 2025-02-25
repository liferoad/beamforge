# third party libraries
import dash_bootstrap_components as dbc
import dash_resizable_panels as drp
from dash import dcc, html


def create_right_panel():
    return drp.Panel(
        html.Div(
            [
                html.Div(
                    [
                        html.H3(
                            "Transform Details",
                            style={
                                "width": "auto",
                                "textAlign": "center",
                                "fontSize": "28px",
                                "fontWeight": "bold",
                                "color": "#FF6F20",  # Primary orange color from the logo
                                "margin": "5px 5px",
                                "padding": "10px",
                                "paddingBottom": "8px",
                                "fontFamily": "Roboto, sans-serif",
                                "borderRadius": "5px",
                            },
                        ),
                        html.Div(
                            id="node-info",
                            children=[
                                dbc.Card(
                                    children=[
                                        dbc.CardBody(
                                            [
                                                html.Div(id="node-data"),
                                            ]
                                        )
                                    ]
                                )
                            ],
                        ),
                    ]
                ),
                html.Div(
                    [
                        html.H3(
                            "Pipeline Options",
                            style={
                                "textAlign": "center",
                                "fontSize": "28px",
                                "fontWeight": "bold",
                                "color": "#FF6F20",
                                "margin": "5px 5px",
                                "padding": "10px",
                                "paddingBottom": "8px",
                                "fontFamily": "Roboto, sans-serif",
                                "borderRadius": "5px",
                            },
                        ),
                        dbc.Card(
                            children=[
                                dbc.CardBody(
                                    [
                                        html.Div(
                                            [
                                                html.H6(
                                                    "Runner:",
                                                    className="mb-2",
                                                    style={"fontSize": "16px", "fontWeight": "500"},
                                                ),
                                                dcc.Dropdown(
                                                    id="pipeline-runner-dropdown",
                                                    options=[
                                                        {
                                                            "label": "Prism",
                                                            "value": "PrismRunner",
                                                        },
                                                        {
                                                            "label": "Dataflow",
                                                            "value": "DataflowRunner",
                                                        },
                                                    ],
                                                    value="PrismRunner",
                                                    style={
                                                        "border": "1px solid #ced4da",
                                                        "borderRadius": "6px",
                                                        "fontSize": "14px",
                                                        "backgroundColor": "#ffffff",
                                                        "boxShadow": "inset 0 1px 2px rgba(0,0,0,.05)",
                                                    },
                                                ),
                                            ],
                                            style={"marginBottom": "20px"},
                                        ),
                                        html.Div(
                                            [
                                                html.H6(
                                                    "Options:",
                                                    className="mb-2",
                                                    style={"fontSize": "16px", "fontWeight": "500"},
                                                ),
                                                dcc.Textarea(
                                                    id="pipeline-options-input",
                                                    placeholder="Enter other pipeline options. \n"
                                                    "Examples: --project your_gcp_project --region us-central1",
                                                    style={
                                                        "width": "100%",
                                                        "height": "80px",
                                                        "padding": "10px",
                                                        "border": "1px solid #ced4da",
                                                        "borderRadius": "6px",
                                                        "fontSize": "14px",
                                                        "backgroundColor": "#ffffff",
                                                        "boxShadow": "inset 0 1px 2px rgba(0,0,0,.05)",
                                                        "resize": "vertical",
                                                    },
                                                ),
                                            ],
                                            style={"marginBottom": "10px"},
                                        ),
                                    ]
                                )
                            ]
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Button(
                                            "Run Pipeline",
                                            id="run-pipeline-button",
                                            className="beam-button",
                                            style={
                                                "marginRight": "10px",
                                            },
                                        ),
                                        html.Button(
                                            "Clear Logs",
                                            id="clear-graph-logs",
                                            className="beam-button",
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                        "justifyContent": "center",
                                        "marginTop": "10px",
                                    },
                                ),
                            ]
                        ),
                    ]
                ),
            ],
            style={"height": "100%", "overflowY": "auto", "padding": "10px"},
        ),
        defaultSizePercentage=20,
    )
