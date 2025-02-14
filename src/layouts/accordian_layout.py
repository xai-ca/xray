# layouts/abstract_layout.py

import dash_bootstrap_components as dbc
from dash import html, dcc


# --- Abstract Argumentation Framework Setting ---
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
                                    placeholder="Example",
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
                                    dbc.Input(value="edited_af", id="21-af-filename"),
                                    dbc.InputGroupText("."),
                                    dbc.Select(
                                        options=[
                                            {"label": ext, "value": ext}
                                            for ext in ["JSON", "TGF", "APX", "ICCMA23"]
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
        dbc.Row(id="21-abstract-evaluation-all-args"),
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
                get_abstract_evaluation_div(), title="Extensions (Solutions)", item_id="Evaluation"
            ),
            dbc.AccordionItem(
                get_abstract_explanation_div(),
                title="Argument Provenance",
                item_id="Explanation",
            ),
        ],
        id="abstract-evaluation-accordion",
    ),
    style={"width": "30%", "maxWidth": "30%"},
)
