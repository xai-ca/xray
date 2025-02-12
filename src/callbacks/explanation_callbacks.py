# callbacks/explanation_callbacks.py

from dash import html, callback, Input, Output, State, callback_context, ALL
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import json

# Import any necessary functions
from py_arg_visualisation.functions.import_functions.read_argumentation_framework_functions import (
    read_argumentation_framework,
)
from py_arg_visualisation.functions.graph_data_functions.get_af_dot_string import (
    get_numbered_grounded_extension,
)


# -- Callback for generating explanations --
@callback(
    Output("21-abstract-evaluation-all-args", "children"),
    State("abstract-arguments", "value"),
    State("abstract-attacks", "value"),
    Input("abstract-evaluation-accordion", "active_item"),
    Input("selected-argument-store-abstract", "data"),
    prevent_initial_call=True,
)
def generate_explanations(arguments, attacks, active_item, selected_extension):
    if active_item != "Explanation":
        raise PreventUpdate

    # Read the argumentation framework and compute grounded status.
    arg_framework = read_argumentation_framework(arguments, attacks)
    gr_status_by_arg, number_by_argument = get_numbered_grounded_extension(
        arg_framework
    )

    def determine_hex_color(arg):
        """Return the hex color code based on the argument's status and extension membership."""
        status = gr_status_by_arg.get(arg)
        if status == "undefined":
            if arg in selected_extension.get("green", []):
                return "#a6e9ff"  # light-green
            elif arg in selected_extension.get("red", []):
                return "#ffe6c9"  # light-red
            elif arg in selected_extension.get("yellow", []):
                return "#FEFE62"  # yellow for undefined
            else:
                return "#cccccc"  # fallback color
        else:
            if arg in selected_extension.get("green", []):
                return "#40cfff"  # green
            elif arg in selected_extension.get("yellow", []):
                return "#FEFE62"  # yellow
            elif arg in selected_extension.get("red", []):
                return "#ffb763"  # red
            else:
                return "#cccccc"  # fallback color

    # Create a button for each argument with colored background and hover border effect
    all_argument_buttons = [
        dbc.Button(
            arg,
            id={"type": "argument-button-abstract", "index": arg},
            className="hover-button",  # Custom class for hover effect
            style={
                "margin": "5px",
                "backgroundColor": determine_hex_color(arg),  # Set background color
                "border": "1px solid gray",  # Border matches color
                "color": "black",  # Text color
            },
        )
        for arg in sorted(arguments.split("\n"))
    ]

    # Build and return the complete Div.
    arguments_div = html.Div(
        [
            html.B("Argument Provenance:"),
            html.Br(),
            html.I("Click on an argument to display it in the graph."),
            html.Div(all_argument_buttons),
        ]
    )
    return arguments_div


@callback(
    Output({"type": "argument-button-abstract", "index": ALL}, "className"),
    Input({"type": "argument-button-abstract", "index": ALL}, "n_clicks"),
    State({"type": "argument-button-abstract", "index": ALL}, "id"),
    prevent_initial_call=True,
)
def update_selected_button(n_clicks_list, id_list):
    ctx = callback_context
    # If no button has been clicked yet, return the default class for all buttons.
    if not ctx.triggered:
        return ["hover-button" for _ in id_list]

    # Identify the button that was clicked.
    triggered_prop = ctx.triggered[0]["prop_id"]
    # The triggered id comes in as a JSON string, so decode it.
    triggered_id = json.loads(triggered_prop.split(".")[0])

    # Build the new className list:
    # The clicked button gets "hover-button selected"; all others remain "hover-button".
    new_class_names = []
    for btn_id in id_list:
        if btn_id["index"] == triggered_id["index"]:
            new_class_names.append("hover-button selected")
        else:
            new_class_names.append("hover-button")

    return new_class_names
