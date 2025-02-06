# layout.py

import dash_bootstrap_components as dbc
from dash import html, dcc
import dash_interactive_graphviz
import visdcc
import os

# Abstract Argumentation Framework Layout
def get_abstract_setting_specification_div():
    return html.Div(
        children=[
            dcc.Store(id="selected-argument-store-abstract"),
            dcc.Store(id="selected_arguments_changed", data=None),
            dbc.Col(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Button(
                                    "Generate",
                                    id="generate-random-af-button",
                                    n_clicks=0,
                                    className="w-100",
                                )
                            ),
                            dbc.Col(
                                dcc.Upload(
                                    dbc.Button("Open File", className="w-100"),
                                    id="upload-af",
                                )
                            ),
                            dbc.Col(
                                dcc.Dropdown(
                                    id="examples-dropdown",
                                    className="w-100",
                                    placeholder="Select an example",
                                )
                            ),
                        ],
                        className="mt-2",
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.B("Arguments"),
                                    dbc.Textarea(
                                        id="abstract-arguments",
                                        placeholder="Add one argument per line. "
                                        "For example:\n A\n B\n C",
                                        value="",
                                        style={"height": "300px"},
                                    ),
                                ]
                            ),
                            dbc.Col(
                                [
                                    html.B("Attacks"),
                                    dbc.Textarea(
                                        id="abstract-attacks",
                                        placeholder="Add one attack per line. "
                                        "For example: \n (A,B) \n (A,C) \n (C,B)",
                                        value="",
                                        style={"height": "300px"},
                                    ),
                                ]
                            ),
                        ],
                        className="mt-2",
                    ),
                    dbc.Row(
                        [
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("Filename"),
                                    dbc.Input(value="edited_af", id="21-af-filename"),
                                    dbc.InputGroupText("."),
                                    dbc.Select(
                                        options=[
                                            {"label": extension, "value": extension}
                                            for extension in [
                                                "JSON",
                                                "TGF",
                                                "APX",
                                                "ICCMA23",
                                            ]
                                        ],
                                        value="JSON",
                                        id="21-af-extension",
                                    ),
                                    dbc.Button("Download", id="21-af-download-button"),
                                ],
                                className="mt-2",
                            ),
                            dcc.Download(id="21-af-download"),
                        ]
                    ),
                ]
            ),
        ]
    )

# Evaluation Layout
def get_abstract_evaluation_div():
    return html.Div(
        [
            html.Div(
                [
                    dbc.Row(
                        [
                            dbc.Col(html.B("Semantics")),
                            dbc.Col(
                                dbc.Select(
                                    options=[
                                        # {'label': 'Admissible', 'value': 'Admissible'},
                                        {"label": "Complete", "value": "Complete"},
                                        {"label": "Grounded", "value": "Grounded"},
                                        {"label": "Preferred", "value": "Preferred"},
                                        # {'label': 'Ideal', 'value': 'Ideal'},
                                        # {'label': 'Stage', 'value': 'Stage'},
                                        {"label": "Stable", "value": "Stable"},
                                        # {'label': 'Semi-stable', 'value': 'SemiStable'},
                                        # {'label': 'Eager', 'value': 'Eager'},
                                        # {'label': 'Conflict-free', 'value': 'ConflictFree'},
                                        # {'label': 'Naive', 'value': 'Naive'}
                                    ],
                                    value="Complete",
                                    id="abstract-evaluation-semantics",
                                )
                            ),
                        ]
                    ),
                    dbc.Row(id="21-abstract-evaluation-semantics"),
                    dbc.Row(
                        [
                            dbc.Col(html.B("Evaluation strategy")),
                            dbc.Col(
                                dbc.Select(
                                    options=[
                                        {"label": "Credulous", "value": "Credulous"},
                                        {"label": "Skeptical", "value": "Skeptical"},
                                    ],
                                    value="Credulous",
                                    id="abstract-evaluation-strategy",
                                )
                            ),
                        ]
                    ),
                    dbc.Row(id="21-abstract-evaluation-accepted"),
                ]
            ),
        ]
    )

# Explanation Layout
def get_abstract_explanation_div():
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(html.B("Type")),
                    dbc.Col(
                        dbc.Select(
                            options=[
                                {"label": "Acceptance", "value": "Acceptance"},
                                {"label": "Non-Acceptance", "value": "NonAcceptance"},
                            ],
                            value="Acceptance",
                            id="abstract-explanation-type",
                        )
                    ),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(html.B("Explanation function")),
                    dbc.Col(dbc.Select(id="abstract-explanation-function")),
                ]
            ),
            dbc.Row(id="abstract-explanation"),
        ]
    )


left_column = dbc.Col(
    dbc.Accordion(
        [
            dbc.AccordionItem(
                get_abstract_setting_specification_div(),
                title="Abstract Argumentation Framework",
                item_id="ArgumentationFramework",
            ),
            dbc.AccordionItem(
                get_abstract_evaluation_div(), title="Evaluation", item_id="Evaluation"
            ),
            dbc.AccordionItem(
                get_abstract_explanation_div(),
                title="Explanation",
                item_id="Explanation",
            ),
        ],
        id="abstract-evaluation-accordion",
    ),
    style={"width": "30%", "maxWidth": "30%"},
)

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
                                                                    html.B(
                                                                        "Layout Direction"
                                                                    ),
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
                                                        html.Div(
                                                            style={"height": "5px"}
                                                        ),
                                                        dbc.Row(
                                                            [
                                                                dbc.Col(
                                                                    html.B("Layer By"),
                                                                    width=5,
                                                                ),
                                                                dbc.Col(
                                                                    dbc.Select(
                                                                        options=[
                                                                            {
                                                                                "label": "Attacks",
                                                                                "value": "NR",
                                                                            },
                                                                            {
                                                                                "label": "Unattacked Arguments",
                                                                                "value": "MR",
                                                                            },
                                                                            {
                                                                                "label": "Length of Arguments",
                                                                                "value": "AR",
                                                                            },
                                                                        ],
                                                                        value="NR",
                                                                        id="21-abstract-graph-rank",
                                                                    ),
                                                                ),
                                                            ]
                                                        ),
                                                        html.Div(
                                                            style={"height": "5px"}
                                                        ),
                                                        dbc.Row(
                                                            [
                                                                dbc.Col(
                                                                    html.B(
                                                                        "Special Handling"
                                                                    ),
                                                                    width=5,
                                                                ),
                                                                dbc.Col(
                                                                    dbc.Checklist(
                                                                        options=[
                                                                            {
                                                                                "label": "Use Blunders",
                                                                                "value": "BU",
                                                                            },
                                                                            {
                                                                                "label": "Use Re-Derivations",
                                                                                "value": "RD",
                                                                            },
                                                                            {
                                                                                "label": "Use Neato",
                                                                                "value": "NO",
                                                                            },
                                                                        ],
                                                                        value=[
                                                                            "BU",
                                                                            "RD",
                                                                        ],
                                                                        inline=True,
                                                                        id="21-abstract-graph-special-handling",
                                                                    ),
                                                                ),
                                                            ]
                                                        ),
                                                    ],
                                                    width=8,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Button(
                                                            "Download DOT File",
                                                            id="21-dot-download-button",
                                                            style={
                                                                "width": "150px",
                                                                "marginTop": "-15px",
                                                                "marginLeft": "30px",
                                                            },
                                                        ),
                                                        dcc.Download(
                                                            id="21-dot-download"
                                                        ),
                                                    ],
                                                    className="d-flex flex-column justify-content-center align-items-center",
                                                    width=3,
                                                ),
                                                # dbc.Col(
                                                #     [
                                                #         dbc.Button(
                                                #             " Layout",
                                                #             id="21-dot-layout-button",
                                                #             style={
                                                #                 "width": "120px",
                                                #                 "marginTop": "-15px",
                                                #             },
                                                #         ),
                                                #         dcc.Download(
                                                #             id="21-dot-layout"
                                                #         ),
                                                #     ],
                                                #     className="d-flex flex-column justify-content-center align-items-center",
                                                #     width=2,
                                                # ),
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


layout_abstract = dbc.Row([left_column, right_column])
layout = html.Div(
    [
        dbc.Container(
            [
                # Header Section
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div(
                                [
                                    html.Img(
                                        src="/assets/logo.png",
                                        height="60px",
                                        className="me-3",
                                    ),  # Logo Placeholder
                                    html.Span(
                                        "WESE(new web)",
                                        style={
                                            "font-weight": "bold",
                                            "color": "#333333",
                                            "font-size": "2rem",
                                        },
                                    ),
                                ],
                                className="d-flex align-items-center justify-content-center mt-1",
                            ),
                            width=12,
                        )
                    ]
                ),
                # Description Section
                dbc.Row(
                    [
                        dbc.Col(
                            html.P(
                                "Well-founded Explanations for Stable Extensions in Abstract Argumentation Framework",
                                className="lead text-center",
                            ),
                            width=10,
                            className="mx-auto",
                        )
                    ],
                    className="mb-4",
                ),
                # Main Content Section (Takes up space to push the footer down)
                dbc.Row(
                    [
                        dbc.Col(
                            layout_abstract,
                            width=12,
                            className="shadow p-4 bg-light rounded flex-grow-1",
                        )
                    ]
                ),
                # Footer Section (Now positioned lower)
                dbc.Row(
                    dbc.Col(
                        html.Footer(
                            [
                                html.P(
                                    "WESE is built upon PyArg",
                                    className="mb-0 text-center text-muted",
                                ),
                                html.P(
                                    "Released under MIT License. Copyright © 2025 - Present UIUC CIRSS",
                                    className="text-center text-muted small",
                                ),
                            ],
                            className="py-3",
                        ),
                        width=12,
                    ),
                ),
            ],
            fluid=True,
            className="p-4 d-flex flex-column min-vh-100",
        )
    ]
)
