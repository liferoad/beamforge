# third party libraries
import dash_resizable_panels as drp
from dash import html

from beamforge.layouts.left_panel import create_left_panel
from beamforge.layouts.middle_panel import create_middle_panel
from beamforge.layouts.right_panel import create_right_panel


def create_layout():
    return html.Div(
        [
            drp.PanelGroup(
                [
                    create_left_panel(),
                    drp.PanelResizeHandle(className="panel-resize-handle"),
                    create_middle_panel(),
                    drp.PanelResizeHandle(className="panel-resize-handle"),
                    create_right_panel(),
                ],
                direction="horizontal",
            ),
            html.Div(id="reset-trigger", style={"display": "none"}),
        ],
        style={"height": "100vh"},
    )
