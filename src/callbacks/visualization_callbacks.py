# callbacks/visualization_callbacks.py

import os
import subprocess
from dash import callback, Input, Output, State, ctx
from dash.exceptions import PreventUpdate
from py_arg_visualisation.functions.graph_data_functions.get_af_dot_string import (
    generate_plain_dot_string,
    generate_dot_string,
)
from py_arg_visualisation.functions.import_functions.read_argumentation_framework_functions import (
    read_argumentation_framework,
)


# -- Callback for generating and downloading the visualization (DOT graph) --
@callback(
    Output("21-dot-download", "data"),
    Output("explanation-graph", "dot_source"),
    Output("selected_arguments_changed", "data"),
    Input("21-dot-download-button", "n_clicks"),
    Input("abstract-arguments", "value"),
    Input("abstract-attacks", "value"),
    Input("selected-argument-store-abstract", "data"),
    Input("21-abstract-graph-layout", "value"),
    Input("21-abstract-graph-rank", "value"),
    Input("21-abstract-graph-special-handling", "value"),
    Input("abstract-evaluation-accordion", "active_item"),
    Input("layout-freeze-switch", "value"),
    Input("21-af-filename", "value"),
    State("selected_arguments_changed", "data"),
    State("explanation-graph", "dot_source"),
    prevent_initial_call=True,
)
def create_visualization(
    _nr_clicks,
    arguments,
    attacks,
    selected_arguments,
    dot_layout,
    dot_rank,
    special_handling,
    active_item,
    layout_freeze,
    selected_file_name,
    selected_arguments_changed,
    current_dot_source,
):
    if not arguments or not attacks:
        raise PreventUpdate

    if not isinstance(selected_arguments, dict):
        selected_arguments = {}

    if selected_arguments_changed is None:
        selected_arguments_changed = False

    dot_source = None
    arg_framework = read_argumentation_framework(arguments, attacks)
    triggered_id = ctx.triggered_id

    # Determine whether Tab "ArgumentationFramework" is active
    if active_item == "ArgumentationFramework":
        dot_source = generate_plain_dot_string(arg_framework, dot_layout)
        selected_arguments_changed = False
    # Determine whether Tab "Explanation" is active
    elif active_item == "Explanation":
        dot_source = current_dot_source
    # Determine whether Tab "Solution" is active
    else:
        # if triggered_id == "abstract-evaluation-accordion":
        #     dot_source = generate_plain_dot_string(arg_framework, dot_layout)
            
        if (
            triggered_id == "selected-argument-store-abstract"
            and selected_arguments == {}
        ):
            dot_source = generate_plain_dot_string(arg_framework, dot_layout)
        else:
            if (
                triggered_id == "selected-argument-store-abstract"
                and not selected_arguments_changed
            ):
                dot_source = generate_dot_string(
                    arg_framework,
                    selected_arguments,
                    True,
                    dot_layout,
                    dot_rank,
                    special_handling,
                    layout_freeze,
                )
                selected_arguments_changed = True
                os.makedirs("temp", exist_ok=True)
                with open("temp/layout.dot", "w") as dot_file:
                    dot_file.write(dot_source)
                subprocess.run(
                    ["dot", "-Tplain", "temp/layout.dot", "-o", "temp/layout.txt"],
                    check=True,
                )
            elif (
                triggered_id == "selected-argument-store-abstract"
                and selected_arguments_changed
            ):
                dot_source = generate_dot_string(
                    arg_framework,
                    selected_arguments,
                    True,
                    dot_layout,
                    dot_rank,
                    special_handling,
                    layout_freeze,
                    layout_file="temp/layout.txt",
                )
            elif triggered_id in [
                "21-abstract-graph-layout",
                "21-abstract-graph-rank",
                "21-abstract-graph-special-handling",
            ]:
                dot_source = generate_dot_string(
                    arg_framework,
                    selected_arguments,
                    True,
                    dot_layout,
                    dot_rank,
                    special_handling,
                    layout_freeze,
                )
                os.makedirs("temp", exist_ok=True)
                with open("temp/layout.dot", "w") as dot_file:
                    dot_file.write(dot_source)
                subprocess.run(
                    ["dot", "-Tplain", "temp/layout.dot", "-o", "temp/layout.txt"],
                    check=True,
                )

        # Determine whether Download button is pressed
        if triggered_id == "21-dot-download-button":
            rank_dict = {
                "NR": "Attacks",
                "MR": "Unchallenged Arguments",
                "AR": "Length of Arguments",
            }
            settings = f"""
            // Input AF: {str(arg_framework)}
            // Layer by: {rank_dict.get(dot_rank, "Unknown")}
            // Use Blunders: {"Yes" if "BU" in special_handling else "No"}
            // Use Re-Derivations: {"Yes" if "RD" in special_handling else "No"}
            """.strip()
            return (
                dict(
                    content=settings + "\n" + current_dot_source,
                    filename="{}.gv".format(selected_file_name.split(".")[0]),
                ),
                dot_source,
                selected_arguments_changed,
            )

    return None, dot_source, selected_arguments_changed
