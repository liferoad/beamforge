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
                        "color": "#FF6F20",
                        "fontFamily": "Roboto, sans-serif",
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
