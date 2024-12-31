# third party libraries
import dash_resizable_panels as drp
from dash import dcc, html
from dash_ace import DashAceEditor


def create_left_panel():
    return drp.Panel(
        html.Div(
            style={
                "display": "flex",
                "flexDirection": "column",
                "height": "100%",  # Ensure the div takes full height
                "backgroundColor": "#F5F5F5",  # Set background color
            },
            children=[
                html.H3(
                    "BeamForge v0.0.1",
                    style={
                        "fontSize": "28px",
                        "fontWeight": "bold",
                        "color": "#FF6F20",  # Primary orange color from the logo
                        "margin": "20px 15px",
                        "padding": "10px",
                        "borderBottom": "2px solid #FF6F20",  # Matching the header color
                        "paddingBottom": "8px",
                        "fontFamily": "'Segoe UI', Arial, sans-serif",
                        "backgroundColor": "rgba(255, 255, 255, 0.8)",
                        "borderRadius": "5px",
                    },
                ),
                dcc.Upload(
                    id="upload-data",
                    children=html.Div(
                        [
                            html.A("Select Beam YAML File", style={"color": "#FF6F20", "fontWeight": "bold"}),
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
                        "margin": "20px auto",
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
                    [
                        DashAceEditor(
                            id="yaml-content",
                            value="",
                            mode="yaml",
                            theme="tomorrow",
                            tabSize=2,
                            enableLiveAutocompletion=True,
                            showGutter=True,
                            readOnly=True,
                            style={
                                "width": "95%",
                                "height": "calc(100vh - 220px)",
                                "margin": "10px",
                            },
                        ),
                    ],
                    style={"height": "calc(100% - 170px)", "overflow": "auto"},
                ),
                html.Div(
                    style={
                        "textAlign": "center",
                        "marginTop": "auto",
                    },  # Center the logo and push it to the bottom
                    children=[
                        dcc.Download(id="download-yaml"),
                        html.Button(
                            "Download File",
                            id="create-yaml-button",
                            className="beam-button",
                        ),
                    ],
                ),
                # Move the Beam logo to the bottom
                html.Div(
                    style={
                        "textAlign": "center",
                        "margin": "20px 0",
                        "marginTop": "auto",
                    },  # Center the logo and push it to the bottom
                    children=[
                        html.A(
                            href="https://beam.apache.org/",
                            target="_blank",
                            children=[
                                html.Img(
                                    src="/assets/beam_logo.png",  # Ensure the logo is in the assets folder
                                    style={
                                        "width": "80px",  # Adjust size as needed
                                        "display": "block",
                                        "cursor": "pointer",  # Indicate it's clickable
                                    },
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
        defaultSizePercentage=20,
    )
