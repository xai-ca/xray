# layouts/abstract_layout.py

import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, callback
import json


# --- Abstract Argumentation Framework Setting ---
def get_abstract_setting_specification_div():
    return html.Div(
        children=[
            dcc.Store(id="selected-argument-store-abstract"),
            dcc.Store(id="selected_arguments_changed", data=None),
            dcc.Store(id="raw-json", data=None),
            # Add modal for displaying example content
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("Example Content")),
                    dbc.ModalBody(id="example-content-modal-body"),
                    dbc.ModalFooter(
                        dbc.Button("Close", id="close-example-modal", className="ms-auto", n_clicks=0)
                    ),
                ],
                id="example-content-modal",
                is_open=False,
                size="lg",
                style={"zIndex": 9999},
            ),
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
                                ),
                                width=3,
                            ),
                            dbc.Col(
                                dcc.Upload(
                                    dbc.Button("Open", className="w-100"),
                                    id="upload-af",
                                ),
                                width=3,
                            ),
                            dbc.Col(
                                dcc.Dropdown(
                                    id="examples-dropdown",
                                    className="w-100",
                                    placeholder="Example",
                                ),
                                width=4,
                            ),
                            dbc.Col(
                                dbc.Button(
                                    html.I(className="fas fa-arrow-up-right-from-square"),
                                    id="show-more-button",
                                    n_clicks=0,
                                    color="secondary",
                                    className="w-100",
                                    title="Show More"
                                ),
                                width=2,
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
                                        placeholder="Add one argument per line. For example:\nA\nB\nC",
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
                                        placeholder="Add one attack per line. For example:\n(A,B)\n(A,C)\n(C,B)",
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
                                    dbc.Input(
                                        value="edited_af",
                                        id="21-af-filename",
                                        style={"width": "100px"},
                                    ),
                                    dbc.InputGroupText("."),
                                    dbc.Select(
                                        options=[
                                            {"label": ext, "value": ext}
                                            for ext in ["json"]
                                        ],
                                        value="json",
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


# --- Evaluation Panel ---
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
                                        {"label": "Grounded", "value": "Grounded"},
                                        {"label": "Stable", "value": "Stable"},
                                        {"label": "Preferred", "value": "Preferred"},
                                        {"label": "Complete", "value": "Complete"},
                                    ],
                                    value="Grounded",
                                    id="abstract-evaluation-semantics",
                                )
                            ),
                        ]
                    ),
                    # Hidden radio items (will be populated by callbacks)
                    html.Div(
                        [
                            dbc.RadioItems(id="extension-radioitems-grounded"),
                            dbc.RadioItems(id="extension-radioitems-stable"),
                            dbc.RadioItems(id="extension-radioitems-preferred"),
                            dbc.RadioItems(id="extension-radioitems-other"),
                            dcc.Store(id="store-extension-grounded"),
                            dcc.Store(id="store-extension-stable"),
                            dcc.Store(id="store-extension-preferred"),
                            dcc.Store(id="store-extension-other"),
                            dcc.Store(id="store-radio-trigger-id"),
                        ],
                        style={"display": "none"},
                    ),
                    dbc.Row(id="21-abstract-evaluation-semantics"),
                    dcc.Store(id="grounded-extension-long-str-store"),
                ]
            ),
        ]
    )


# --- Explanation Panel ---
def get_abstract_explanation_div():
    return html.Div(
        [
            html.I("Click on an argument to display its"),
            dcc.Dropdown(
                options=[
                    {"label": "Potential Provenance", "value": "PO"},
                    {"label": "Actual Provenance", "value": "AC"},
                    {"label": "Primary Provenance", "value": "PR"},
                ],
                value="PO",
                id="prov-type-dropdown",
            ),
            dbc.Row(id="21-abstract-evaluation-all-args"),
            dcc.Store(id="prov-button-value-output"),
        ]
    )


# --- Fix Panel ---
def get_critical_div():
    return html.Div(
        [
            html.Div(
                [
                    html.B("Selected Extension:"),
                    html.Div(id="selected-extension-display"),
                    html.Br(),
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.I("Critical Attack Sets:"),
                                    dbc.RadioItems(
                                        id="possible-fixes-radio",
                                        className="mt-2",
                                        style={"marginLeft": "10px"},
                                    ),
                                    # Add hint message that's hidden by default
                                    html.Div(
                                        "No critical attacks under the selected extension",
                                        id="no-critical-attacks-hint",
                                        style={
                                            "display": "none",
                                            "color": "#ff0000",
                                            "font-style": "italic",
                                            "margin-top": "10px",
                                        },
                                    ),
                                ]
                            ),
                        ]
                    ),
                    dbc.Row(
                        [
                            dbc.Col([
                                dbc.Row([
                                    dbc.Col(
                                        html.Label(
                                            "Suspend Critical Attacks",
                                            htmlFor="apply-fix-switch",
                                            style={"marginRight": "10px"}
                                        ),
                                        width="auto"
                                    ),
                                    dbc.Col(
                                        dbc.Switch(
                                            id="apply-fix-switch",
                                            value=False,
                                            style={
                                                "transform": "scale(1.4)",
                                                "transformOrigin": "left center",
                                                "marginTop": "4px"
                                            }
                                        ),
                                        width="auto"
                                    )
                                ], align="center"),
                            ]),
                        ],
                        className="mt-4"
                    ),
                    # Store for keeping track of available fixes
                    dcc.Store(id="available-fixes-store", data=None),
                ]
            ),
        ]
    )


# --- Left Column (Accordion) ---
left_column = dbc.Col(
    dbc.Accordion(
        [
            dbc.AccordionItem(
                get_abstract_setting_specification_div(),
                title="Abstract Argumentation Framework",
                item_id="ArgumentationFramework",
            ),
            dbc.AccordionItem(
                get_abstract_evaluation_div(),
                title="Extensions (Semantics)",
                item_id="Evaluation",
            ),
            dbc.AccordionItem(
                get_abstract_explanation_div(),
                title="Argument Status Provenance",
                item_id="Provenance",
            ),
            dbc.AccordionItem(
                get_critical_div(),
                title="Critical Attack(s) Analysis",
                item_id="CriticalAttacks",
            ),
        ],
        id="abstract-evaluation-accordion",
    ),
    style={"width": "30%", "maxWidth": "30%"},
)
