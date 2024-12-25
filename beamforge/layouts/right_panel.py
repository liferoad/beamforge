# third party libraries
import dash_resizable_panels as drp
from dash import html


def create_right_panel():
    return drp.Panel(
        html.Div(
            [
                html.H3("Transform Details"),
                html.Div(
                    id="node-info",
                    children=[html.P("Click a transform to see its details"), html.Div(id="node-data")],
                ),
            ]
        ),
        defaultSizePercentage=20,
    )
