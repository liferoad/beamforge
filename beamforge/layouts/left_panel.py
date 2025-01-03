# third party libraries
import dash_bootstrap_components as dbc
import dash_resizable_panels as drp
from dash import dcc, html
from dash_ace import DashAceEditor


def create_left_panel():
    return drp.Panel(
        html.Div(
            style={
                "display": "flex",
                "flexDirection": "column",
                "height": "100%",
                "backgroundColor": "#F5F5F5",
            },
            children=[
                dbc.Row(
                    [
                        dbc.Col(
                            html.A(
                                href="https://beam.apache.org/",
                                target="_blank",
                                children=[
                                    html.Img(
                                        src="/assets/beam_logo.png",
                                        style={
                                            "width": "100px",
                                            "display": "block",
                                            "cursor": "pointer",
                                            "marginTop": "15px",
                                            "marginRight": "5px",
                                            "marginLeft": "5px",
                                        },
                                    ),
                                ],
                            )
                        ),
                        dbc.Col(
                            html.H3(
                                "BeamForge",
                                style={
                                    "width": "auto",
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
                            )
                        ),
                    ],
                    style={
                        "borderBottom": "2px solid #FF6F20",
                    },
                ),
                dcc.Upload(
                    id="upload-data",
                    children=html.Div(
                        [
                            html.A("Upload Beam YAML File Here", style={"color": "#FF6F20"}),
                        ],
                        style={"display": "flex", "flexDirection": "column", "alignItems": "center"},
                    ),
                    style={
                        "width": "90%",
                        "height": "60px",
                        "borderWidth": "2px",
                        "borderStyle": "dashed",
                        "borderColor": "#FF6F20",
                        "borderRadius": "10px",
                        "textAlign": "center",
                        "margin": "10px auto",
                        "backgroundColor": "#F5F5F5",
                        "display": "flex",
                        "alignItems": "center",
                        "justifyContent": "center",
                        "cursor": "pointer",
                        "boxShadow": "0 2px 6px rgba(0, 0, 0, 0.1)",
                        "transition": "all 0.3s ease",
                        ":hover": {
                            "borderColor": "#D65F00",
                            "backgroundColor": "#EAEAEA",
                            "boxShadow": "0 4px 12px rgba(0, 0, 0, 0.15)",
                        },
                    },
                    multiple=False,
                    accept=".yaml,.yml",
                ),
                html.Div(
                    style={"flexGrow": "1", "overflow": "auto"},
                    children=[
                        DashAceEditor(
                            id="yaml-content",
                            value="Display YAML content here...",
                            mode="yaml",
                            theme="tomorrow",
                            tabSize=2,
                            enableLiveAutocompletion=True,
                            showGutter=True,
                            readOnly=True,
                            maxLines=5000,
                            style={
                                "margin": "10px",
                            },
                        ),
                    ],
                ),
                html.Div(
                    style={
                        "textAlign": "center",
                        "marginTop": "auto",
                        "marginBottom": "10px",
                    },
                    children=[
                        dcc.Download(id="download-yaml"),
                        html.Button(
                            "Download File",
                            id="create-yaml-button",
                            className="beam-button",
                        ),
                    ],
                ),
            ],
        ),
        defaultSizePercentage=20,
    )
