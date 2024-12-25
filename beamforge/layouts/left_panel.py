# third party libraries
import dash_resizable_panels as drp
from dash import dcc, html


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
                        html.Pre(
                            id="yaml-content",
                            style={
                                "width": "95%",
                                "margin": "10px",
                                "fontFamily": "monospace",
                                "whiteSpace": "pre-wrap",
                                "wordWrap": "break-word",
                                "backgroundColor": "#f5f5f5",
                                "padding": "10px",
                                "border": "1px solid #ddd",
                                "borderRadius": "4px",
                                "overflow": "auto",
                                "maxHeight": "calc(100vh - 150px)",
                            },
                        ),
                    ],
                    style={"height": "calc(100% - 100px)", "overflow": "auto"},
                ),
            ]
        ),
        defaultSizePercentage=20,
    )
