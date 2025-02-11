# layouts/main_layout.py

import dash_bootstrap_components as dbc
from dash import html
from layouts.accordian_layout import left_column
from layouts.visualization_layout import right_column

# Compose the main content row (left and right columns)
layout_abstract = dbc.Row([left_column, right_column])

# Main Layout with header, description, content, and footer
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
                                    ),
                                    html.Span(
                                        "WESE",
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
                # Main Content Section
                dbc.Row(
                    [
                        dbc.Col(
                            layout_abstract,
                            width=12,
                            className="shadow p-4 bg-light rounded flex-grow-1",
                        )
                    ]
                ),
                # Footer Section
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
