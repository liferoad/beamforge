# third party libraries
import dash_bootstrap_components as dbc
import dash_resizable_panels as drp
from dash import html


def create_right_panel():
    return drp.Panel(
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
        defaultSizePercentage=20,
    )
