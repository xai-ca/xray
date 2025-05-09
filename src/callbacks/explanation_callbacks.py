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
    
    if selected_extension is None:
        selected_extension = {}

    if active_item != "Provenance":
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
                return "#FFFFFF"  # fallback color
        else:
            if arg in selected_extension.get("green", []):
                return "#40cfff"  # green
            elif arg in selected_extension.get("yellow", []):
                return "#FEFE62"  # yellow
            elif arg in selected_extension.get("red", []):
                return "#ffb763"  # red
            else:
                return "#FFFFFF"  # fallback color

    # Create a button for each argument with colored background and hover border effect
    all_argument_buttons = [
        dbc.Button(
            arg,
            id={"type": "argument-button-abstract", "index": arg},
            className="hover-button",  # Removed btn-secondary
            style={
                "margin": "5px",
                "backgroundColor": determine_hex_color(arg),
                "border": "1px solid gray",
                "color": "black",
            },
        )
        for arg in sorted(arguments.split("\n"))
    ]

    # Build and return the complete Div.
    arguments_div = html.Div(
        [
            html.Br(),
            html.Div(all_argument_buttons),
        ]
    )
    return arguments_div


@callback(
    Output("prov-button-value-output", "data"),
    Input({"type": "argument-button-abstract","index":ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def display_button_value(n_clicks_list):
    # Only proceed if a click has occurred.
    if not any(n_clicks_list):
        raise PreventUpdate

    # Identify which button was clicked
    triggered = callback_context.triggered[0]
    triggered_prop_id = triggered["prop_id"].split(".")[0]
    # The triggered_prop_id is a JSON string of the button's id dictionary
    button_info = json.loads(triggered_prop_id)
    button_value = button_info["index"]

    # Optionally, return a message to update the layout on the UI
    return button_value


@callback(
    [Output({"type": "argument-button-abstract", "index": ALL}, "style")],
    [Input({"type": "argument-button-abstract", "index": ALL}, "n_clicks")],
    [State({"type": "argument-button-abstract", "index": ALL}, "id")],
    [State({"type": "argument-button-abstract", "index": ALL}, "style")],
    prevent_initial_call=True
)
def update_active_button(n_clicks, ids, current_styles):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate
        
    button_id = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])
    clicked_index = button_id['index']
    
    return [[
        {**style, "border": "3px solid black"} if id_dict['index'] == clicked_index 
        else {**style, "border": "1px solid gray"}
        for id_dict, style in zip(ids, current_styles)
    ]]
