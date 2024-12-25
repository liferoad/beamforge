# third party libraries
import dash_resizable_panels as drp
from dash import dcc, html
from dash_ace import DashAceEditor


def create_left_panel():
    return drp.Panel(
        html.Div(
            [
                html.H3("Upload Beam YAML"),
                dcc.Upload(
                    id="upload-data",
                    children=html.Div(["Drag and Drop or ", html.A("Select Beam YAML File")]),
                    style={
                        "width": "80%",
                        "height": "60px",
                        "lineHeight": "60px",
                        "borderWidth": "1px",
                        "borderStyle": "dashed",
                        "borderRadius": "5px",
                        "textAlign": "center",
                        "margin": "10px",
                    },
                    multiple=False,
                    accept=".yaml,.yml",
                ),
                html.Div(
                    [
                        DashAceEditor(
                            id="yaml-content",
                            value="",
                            mode="yaml",
                            theme="tomorrow",
                            tabSize=2,
                            enableLiveAutocompletion=True,
                            showGutter=True,
                            style={
                                "width": "95%",
                                "height": "calc(100vh - 150px)",
                                "margin": "10px",
                            },
                        ),
                    ],
                    style={"height": "calc(100% - 100px)", "overflow": "auto"},
                ),
            ]
        ),
        defaultSizePercentage=20,
    )
