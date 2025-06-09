# layouts/visualization_layout.py

import dash_bootstrap_components as dbc
from dash import html, dcc
import dash_interactive_graphviz
import dash_daq as daq

# Add legend for node colors
legend_container = html.Div([
    # Store component to persist legend state
    dcc.Store(id='legend-state-store', data={'is_visible': True}),
    # Toggle button
    html.Button(
        "◀",  # Left arrow when legend is visible
        id="legend-toggle-button",
        style={
            "position": "absolute",
            "left": "-35px",  # Move slightly more to the left
            "bottom": "20px",
            "zIndex": 2000,  # Increase z-index to ensure it's above other elements
            "backgroundColor": "white",
            "border": "1px solid #ccc",
            "borderRadius": "4px",
            "width": "30px",
            "height": "30px",
            "cursor": "pointer",
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "center",
            "fontSize": "16px",
            "padding": "0",
            "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
            "opacity": "0.9",  # Make it slightly transparent
            "pointerEvents": "auto"  # Use camelCase for React
        }
    ),
    # Legend card
    dbc.Card(
        dbc.CardBody(
            html.Div(id="node-colors-legend")
        ),
        id="legend-card",
        style={
            "position": "absolute",
            "bottom": "20px",
            "left": "20px",
            "zIndex": 1999,  # Just below the button
            "backgroundColor": "rgba(255, 255, 255, 0.9)",
            "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
            "borderRadius": "8px",
            "padding": "15px",  # Increased padding
            "minWidth": "300px",  # Increased width
            "maxWidth": "350px",  # Added max width
            "display": "none",  # Start with display none
            "pointerEvents": "auto"  # Use camelCase for React
        }
    )
], style={
    "position": "absolute",  # Change to absolute positioning
    "bottom": "20px",
    "left": "20px",
    "zIndex": 1999,
    "width": "auto",
    "height": "auto",
    "pointerEvents": "auto"  # Use camelCase for React
})

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
                                                                    dbc.Select(
                                                                        options=[
                                                                            {"label": "BT", "value": "BT"},
                                                                            {"label": "LR", "value": "LR"},
                                                                            {"label": "TB", "value": "TB"},
                                                                            {"label": "RL", "value": "RL"},
                                                                        ],
                                                                        value="BT",
                                                                        id="21-abstract-graph-layout",
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
                                                            style={
                                                                "line-height": "40px",
                                                                "font-size": "16px",
                                                            },
                                                        ),
                                                        dbc.Switch(
                                                            id="layout-freeze-switch",
                                                            value=False,
                                                            style={
                                                                "transform": "scale(1.5)",
                                                                "margin-top": "3px",
                                                            },
                                                        ),
                                                    ],
                                                    className="d-flex justify-content-center align-items-center gap-2",
                                                    width=3,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Label(
                                                            "Local View",
                                                            id="global-view-label",
                                                            className="me-2 fw-bold mb-0",
                                                            style={
                                                                "line-height": "40px",
                                                                "font-size": "16px",
                                                            },
                                                        ),
                                                        dbc.Switch(
                                                            id="global-local-switch",
                                                            value=False,
                                                            style={
                                                                "transform": "scale(1.5)",
                                                                "margin-top": "3px",
                                                            },
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
                                                "maxWidth": "98%",
                                                "overflow": "hidden",
                                                "position": "relative",
                                                "pointerEvents": "auto"  # Use camelCase for React
                                            },
                                        ),
                                        legend_container,  # Use the new legend container instead of just the legend
                                        # Add node details side panel
                                        html.Div([
                                            # Store component to persist panel state
                                            dcc.Store(id='node-panel-state-store', data={'is_visible': False}),
                                            # Toggle button
                                            html.Button(
                                                "▶",  # Right arrow when panel is hidden
                                                id="node-panel-toggle-button",
                                                style={
                                                    "position": "absolute",
                                                    "right": "-35px",  # Position on the right side
                                                    "bottom": "20px",
                                                    "zIndex": 2000,
                                                    "backgroundColor": "white",
                                                    "border": "1px solid #ccc",
                                                    "borderRadius": "4px",
                                                    "width": "30px",
                                                    "height": "30px",
                                                    "cursor": "pointer",
                                                    "display": "none",  # Hide initially
                                                    "alignItems": "center",
                                                    "justifyContent": "center",
                                                    "fontSize": "16px",
                                                    "padding": "0",
                                                    "boxShadow": "0 2px 4px rgba(0,0,0,0.1)"
                                                }
                                            ),
                                            # Node details panel
                                            dbc.Card(
                                                dbc.CardBody(
                                                    html.Div(id="node-details-content")
                                                ),
                                                id="node-details-panel",
                                                style={
                                                    "position": "absolute",
                                                    "bottom": "20px",
                                                    "right": "20px",
                                                    "zIndex": 1999,
                                                    "backgroundColor": "rgba(255, 255, 255, 0.9)",
                                                    "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
                                                    "borderRadius": "8px",
                                                    "padding": "15px",
                                                    "minWidth": "300px",
                                                    "maxWidth": "350px",
                                                    "display": "none",  # Start hidden
                                                    "pointerEvents": "auto"
                                                }
                                            )
                                        ]),
                                        dcc.Store(id="selected-node-store"),  # Store for selected node data
                                    ],
                                    style={
                                        "height": "550px",
                                        "maxWidth": "98%",
                                        "overflow": "visible",  # Change to visible to ensure the button is not cut off
                                        "position": "relative",  # Add position relative for absolute positioning of legend
                                        "pointerEvents": "auto"  # Use camelCase for React
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
