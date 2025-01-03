# third party libraries
import dash_bootstrap_components as dbc
import dash_resizable_panels as drp
from dash import dcc, html


def create_right_panel():
    return drp.Panel(
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
                                            html.H6("Runner:"),
                                            dcc.Dropdown(
                                                id="pipeline-runner-dropdown",
                                                options=[
                                                    {
                                                        "label": "Prism",
                                                        "value": "prism",
                                                    },
                                                    {
                                                        "label": "Dataflow",
                                                        "value": "dataflow",
                                                    },
                                                ],
                                                value="prism",
                                            ),
                                        ],
                                        style={"margin-bottom": "5px"},
                                    ),
                                    html.Div(
                                        [
                                            html.H6("Options:"),
                                            dcc.Textarea(
                                                id="pipeline-options-input",
                                                placeholder="Enter pipeline options. Examples: --project "
                                                "your_gcp_project.",
                                                style={
                                                    "width": "100%",
                                                    "height": "100px",
                                                },
                                            ),
                                        ]
                                    ),
                                ]
                            )
                        ]
                    ),
                ]
            ),
        ],
        defaultSizePercentage=20,
    )
