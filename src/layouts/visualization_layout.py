# layouts/visualization_layout.py

import dash_bootstrap_components as dbc
from dash import html, dcc
import dash_interactive_graphviz
import dash_daq as daq

right_column = dbc.Col(
    [
        dbc.Row(
            [
                dbc.Card(
                    [
                        dbc.CardBody(
                            [
                                html.Div(style={"height": "5px"}),
                                html.Div(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Row(
                                                            [
                                                                dbc.Col(
                                                                    html.B("Layout Direction"),
                                                                    id="layout-direction-label",
                                                                    className="d-flex align-items-center",
                                                                ),
                                                                dbc.Col(
                                                                    dbc.RadioItems(
                                                                        options=[
                                                                            {"label": "BT", "value": "BT"},
                                                                            {"label": "LR", "value": "LR"},
                                                                        ],
                                                                        value="BT",
                                                                        id="21-abstract-graph-layout",
                                                                        inline=True,
                                                                        className="d-flex align-items-center",
                                                                    ),
                                                                    className="d-flex align-items-center",
                                                                ),
                                                            ],
                                                            className="h-100 align-items-center",
                                                        ),
                                                    ],
                                                    width=3,
                                                ),
                                                
                                                dbc.Col(
                                                    [
                                                        dbc.Label(
                                                            "Freeze Layout",
                                                            id="layout-freeze-label",
                                                            className="me-2 fw-bold mb-0",
                                                            style={"line-height": "40px"},
                                                        ),
                                                        daq.ToggleSwitch(
                                                            id="layout-freeze-switch",
                                                            value=False,
                                                            color="#007BFF",
                                                        ),
                                                    ],
                                                    className="d-flex justify-content-center align-items-center gap-2",
                                                    width=3,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Label(
                                                            "Global View",
                                                            id="global-view-label",
                                                            className="me-2 fw-bold mb-0",
                                                            style={"line-height": "40px"},
                                                        ),
                                                        daq.ToggleSwitch(
                                                            id="global-local-switch",
                                                            value=False,
                                                            color="#007BFF",
                                                        ),
                                                    ],
                                                    className="d-flex justify-content-center align-items-center gap-2",
                                                    width=3,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Button(
                                                            "Download DOT",
                                                            id="21-dot-download-button",
                                                            style={"width": "150px","height": "40px"},
                                                        ),
                                                        dcc.Download(id="21-dot-download"),
                                                    ],
                                                    className="d-flex justify-content-center align-items-center",
                                                    width=3,
                                                ),

                                                # html.Div(style={"height": "5px"}),
                                                        dbc.Row(
                                                            [
                                                                dbc.Col(
                                                                    html.B("Layer By"),
                                                                    # width=5,
                                                                ),
                                                                dbc.Col(
                                                                    dbc.Select(
                                                                        options=[
                                                                            {"label": "Attacks", "value": "NR"},
                                                                            {"label": "Unattacked Arguments", "value": "MR"},
                                                                            {"label": "Length of Arguments", "value": "AR"},
                                                                        ],
                                                                        value="AR",
                                                                        id="21-abstract-graph-rank",
                                                                    ),
                                                                ),
                                                            ],
                                                        style={"display": "none"},
                                                        ),
                                                        # html.Div(style={"height": "5px"}),
                                                        dbc.Row(
                                                            [
                                                                dbc.Col(
                                                                    html.B("Special Handling"),
                                                                    # width=5,
                                                                ),
                                                                dbc.Col(
                                                                    dbc.Checklist(
                                                                        options=[
                                                                            {"label": "Use Blunders", "value": "BU"},
                                                                            {"label": "Use Re-Derivations", "value": "RD"},
                                                                        ],
                                                                        value=["BU", "RD"],
                                                                        inline=True,
                                                                        id="21-abstract-graph-special-handling",
                                                                    ),
                                                                ),
                                                            ],
                                                            style={"display": "none"}
                                                        ),
                                                        
                                                
                                            ]
                                        ),
                                    ],
                                    id="layered-vis-param",
                                    style={"display": "block"},
                                ),
                                html.Div(
                                    [
                                        dash_interactive_graphviz.DashInteractiveGraphviz(
                                            id="explanation-graph",
                                            persisted_props={"engine": "neato"},
                                            style={
                                                "height": "550px",
                                                "max-width": "98%",
                                                "overflow": "hidden",
                                            },
                                        ),
                                    ],
                                    style={
                                        "height": "550px",
                                        "max-width": "98%",
                                        "overflow": "hidden",
                                    },
                                ),
                            ]
                        ),
                    ]
                ),
            ]
        ),
    ],
    style={"width": "70%", "maxWidth": "70%"},
)
