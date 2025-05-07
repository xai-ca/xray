# callbacks/visualization_callbacks.py

import os
import subprocess
from dash import callback, Input, Output, State, ctx
from dash.exceptions import PreventUpdate
from py_arg_visualisation.functions.graph_data_functions.get_af_dot_string import (
    generate_plain_dot_string,
    generate_dot_string,
    get_provenance,
    highlight_dot_source,
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
    Input("prov-button-value-output", "data"),
    Input("prov-type-dropdown", "value"),
    State("selected_arguments_changed", "data"),
    State("explanation-graph", "dot_source"),
    State("raw-json", "data"),
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
    prov_arg,
    prov_type,
    selected_arguments_changed,
    current_dot_source,
    raw_json
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

    # If it's a download request, ensure we have a dot_source first
    if triggered_id == "21-dot-download-button":
        # If we don't have a current dot source, generate a plain one
        if current_dot_source is None:
            dot_source = generate_plain_dot_string(arg_framework, dot_layout, raw_json)
        else:
            dot_source = current_dot_source

        rank_dict = {
            "NR": "Attacks",
            "MR": "Unchallenged Arguments",
            "AR": "Length of Arguments",
        }
        settings = f"""
        // Input AF: {str(arg_framework)}
        """.strip()

        # // Layer by: {rank_dict.get(dot_rank, "Unknown")}
        # // Use Blunders: {"Yes" if "BU" in special_handling else "No"}
        # // Use Re-Derivations: {"Yes" if "RD" in special_handling else "No"}
        
        return (
            dict(
                content=settings + "\n" + dot_source,
                filename="{}.gv".format(selected_file_name.split(".")[0]),
            ),
            dot_source,
            selected_arguments_changed,
        )

    # Regular visualization logic continues here
    if active_item == "ArgumentationFramework":
        dot_source = generate_plain_dot_string(arg_framework, dot_layout, raw_json)
        selected_arguments_changed = False
    # Determine whether Tab "Explanation" is active
    elif active_item == "Provenance":
        if selected_arguments:
            dot_source = generate_dot_string(
                    arg_framework,
                    selected_arguments,
                    True,
                    dot_layout,
                    dot_rank,
                    special_handling,
                    layout_freeze,
                    raw_json = raw_json
            )
            if prov_arg:
                hl_edges, hl_nodes = get_provenance(arg_framework, prov_type, prov_arg)
                # print(hl_edges)
                dot_source = highlight_dot_source(dot_source, hl_nodes, prov_arg)
                print(dot_source)
            else:
                raise PreventUpdate
        else:
            dot_source = current_dot_source
        
    # Determine whether Tab "Solution" is active
    else:
        # if triggered_id == "abstract-evaluation-accordion":
        #     dot_source = generate_plain_dot_string(arg_framework, dot_layout)

        if (
            triggered_id == "selected-argument-store-abstract"
            and selected_arguments == {}
        ):
            dot_source = generate_plain_dot_string(arg_framework, dot_layout, raw_json)
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
                    raw_json = raw_json
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
                    raw_json = raw_json
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
                    raw_json= raw_json
                )
                os.makedirs("temp", exist_ok=True)
                with open("temp/layout.dot", "w") as dot_file:
                    dot_file.write(dot_source)
                subprocess.run(
                    ["dot", "-Tplain", "temp/layout.dot", "-o", "temp/layout.txt"],
                    check=True,
                )

    return None, dot_source, selected_arguments_changed


@callback(
    Output("21-abstract-graph-layout", "style"),
    Output("global-local-switch", "disabled"),
    Output("layout-direction-label", "style"),
    Output("global-view-label", "style"),
    Output("layout-freeze-switch", "disabled"),
    Output("layout-freeze-label", "style"),
    Input("layout-freeze-switch", "value"),
    Input("abstract-evaluation-accordion", "active_item"),
)
def toggle_controls_state(layout_freeze, active_item):
    """
    Controls the disabled state and styling of layout-related controls based on:
    1. Whether the layout is frozen (affects all controls except in ArgumentationFramework tab)
    2. Whether we're in the ArgumentationFramework tab (only disables freeze layout and global view)
    """
    disabled_style = {"pointer-events": "none", "opacity": "0.5"}
    enabled_style = {}
    
    # In ArgumentationFramework tab
    if active_item == "ArgumentationFramework":
        return (
            enabled_style,     # layout control style (enabled)
            True,             # global-local switch (disabled)
            enabled_style,    # direction label style (enabled)
            disabled_style,   # view label style (disabled)
            True,            # layout freeze switch (disabled)
            disabled_style   # layout freeze label style (disabled)
        )
    
    # Otherwise, controls are disabled only if layout is frozen
    return (
        disabled_style if layout_freeze else enabled_style,  # layout control style
        layout_freeze,                                       # global-local switch disabled
        disabled_style if layout_freeze else enabled_style,  # direction label style
        disabled_style if layout_freeze else enabled_style,  # view label style
        False,                                              # layout freeze switch disabled
        disabled_style if layout_freeze else enabled_style   # layout freeze label style
    )

