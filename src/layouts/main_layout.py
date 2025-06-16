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
                # Header and Description Section Combined
                dbc.Row(
                    dbc.Col(
                        html.Div(
                            [
                                html.Img(
                                    src="/assets/logo.svg",
                                    height="70px",
                                    className="me-3",
                                ),
                                html.Span(
                                    "AF-XRAY",
                                    style={
                                        "font-weight": "bold",
                                        "color": "#333333",
                                        "font-size": "2rem",
                                    },
                                    className="me-3",
                                ),
                                html.Span(
                                    "Argumentation Framework eXplanation, Reasoning, and AnalYsis",
                                    style={
                                        "color": "#333333",
                                        "font-size": "1.3rem",
                                    },
                                    className="lead",
                                ),
                            ],
                            className="d-flex align-items-center text-start ms-3",  # Added ms-3 for left spacing
                        ),
                        width=12,
                    ),
                    className="mb-4",
                ),
                # Main Content Section
                dbc.Row(
                    [
                        dbc.Col(
                            layout_abstract,
                            width=12,
                            className="shadow p-4 bg-light rounded flex-grow-1",
                            style={"height": "750px"},  # Adjust the height as needed
                        )
                    ]
                ),
            ],
            fluid=True,
            className="p-4 d-flex flex-column flex-grow-1",
        ),
        # Footer Section
        html.Footer(
            dbc.Container(
                dbc.Row(
                    dbc.Col(
                        html.P(
                            [
                                "Released under MIT License and built upon PyArg. Copyright © 2025-Present. University of Illinois Urbana-Champaign ",
                                html.A(
                                    "CIRSS.",
                                    href="https://cirss.ischool.illinois.edu/",
                                    target="_blank",
                                    className="text-decoration-underline text-muted",
                                ),
                            ],
                            className="text-center text-muted small",
                        ),
                    )
                ),
                fluid=True,
            ),
            className="py-3 mt-auto bg-white",
        ),
    ],
    className="d-flex flex-column min-vh-100",
)
