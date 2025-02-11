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
                                                                    width=5,
                                                                ),
                                                                dbc.Col(
                                                                    dbc.Select(
                                                                        options=[
                                                                            {
                                                                                "label": "Left to right",
                                                                                "value": "LR",
                                                                            },
                                                                            {
                                                                                "label": "Right to left",
                                                                                "value": "RL",
                                                                            },
                                                                            {
                                                                                "label": "Bottom to top",
                                                                                "value": "BT",
                                                                            },
                                                                            {
                                                                                "label": "Top to bottom",
                                                                                "value": "TB",
                                                                            },
                                                                        ],
                                                                        value="BT",
                                                                        id="21-abstract-graph-layout",
                                                                    ),
                                                                ),
                                                            ]
                                                        ),
                                                        html.Div(style={"height": "5px"}),
                                                        dbc.Row(
                                                            [
                                                                dbc.Col(
                                                                    html.B("Layer By"),
                                                                    width=5,
                                                                ),
                                                                dbc.Col(
                                                                    dbc.Select(
                                                                        options=[
                                                                            {"label": "Attacks", "value": "NR"},
                                                                            {"label": "Unattacked Arguments", "value": "MR"},
                                                                            {"label": "Length of Arguments", "value": "AR"},
                                                                        ],
                                                                        value="NR",
                                                                        id="21-abstract-graph-rank",
                                                                    ),
                                                                ),
                                                            ]
                                                        ),
                                                        html.Div(style={"height": "5px"}),
                                                        dbc.Row(
                                                            [
                                                                dbc.Col(
                                                                    html.B("Special Handling"),
                                                                    width=5,
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
                                                            ]
                                                        ),
                                                    ],
                                                    width=7,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Button(
                                                            "Download DOT File",
                                                            id="21-dot-download-button",
                                                            style={
                                                                "width": "140px",
                                                                "marginTop": "-15px",
                                                                "marginLeft": "30px",
                                                            },
                                                        ),
                                                        dcc.Download(id="21-dot-download"),
                                                    ],
                                                    className="d-flex flex-column justify-content-center align-items-center",
                                                    width=2,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Freeze Layout", className="me-2 fw-bold"),
                                                        daq.ToggleSwitch(
                                                            id="layout-freeze-switch",
                                                            value=False,
                                                            color="#007BFF",
                                                        ),
                                                    ],
                                                    className="d-flex flex-column justify-content-center align-items-center",
                                                    width=2,
                                                    style={"marginTop": "-15px"},
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
