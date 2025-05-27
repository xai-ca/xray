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
    get_local_view_rank,
    highlight_critical_edges,
    recalculate_fixed_args
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
    Input("global-local-switch", "value"),
    Input("available-fixes-store", "data"),
    Input("apply-fix-switch", "value"),
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
    local_view,
    selected_fix,
    apply_fix_switch,
    selected_arguments_changed,
    current_dot_source,
    raw_json,

):
    if not arguments or not attacks:
        raise PreventUpdate

    if raw_json is None:
        raw_json = {"arguments": []}
    elif isinstance(raw_json, str):
        try:
            import json
            raw_json = json.loads(raw_json)
        except json.JSONDecodeError:
            raw_json = {"arguments": []}

    if not isinstance(selected_arguments, dict):
        selected_arguments = {}

    if selected_arguments_changed is None:
        selected_arguments_changed = False

    dot_source = None
    arg_framework = read_argumentation_framework(arguments, attacks)
    triggered_id = ctx.triggered_id

    # print(triggered_id)
    # print(active_item)

    # If it's a download request, ensure we have a dot_source first
    if triggered_id == "21-dot-download-button":
        
        # If we don't have a current dot source, generate a plain one
        if current_dot_source is None:
            dot_source = generate_plain_dot_string(arg_framework, dot_layout, raw_json)
        else:
            dot_source = current_dot_source
        # print(current_dot_source)
        # rank_dict = {
        #     "NR": "Attacks",
        #     "MR": "Unchallenged Arguments",
        #     "AR": "Length of Arguments",
        # }
        settings = f"""
        // Input AF: {str(arg_framework)}
        """.strip()

        # // Layer by: {rank_dict.get(dot_rank, "Unknown")}
        # // Use Blunders: {"Yes" if "BU" in special_handling else "No"}
        # // Use Re-Derivations: {"Yes" if "RD" in special_handling else "No"}
        # print(dot_source)
        return (
            dict(
                content=settings + "\n" + dot_source,
                filename="{}.gv".format(selected_file_name.split(".")[0]),
            ),
            dot_source,
            selected_arguments_changed,
        )

    # ========================== Argumentation Framework Session ==========================
    if active_item == "ArgumentationFramework":
        if triggered_id == "layout-freeze-switch":
            if layout_freeze:
                # When freezing, generate new layout and save it
                dot_source = generate_plain_dot_string(arg_framework, dot_layout, raw_json)
                os.makedirs("temp", exist_ok=True)
                with open("temp/layout.dot", "w") as dot_file:
                    dot_file.write(dot_source)
                subprocess.run(
                    ["dot", "-Tplain", "temp/layout.dot", "-o", "temp/layout.txt"],
                    check=True,
                )
            else:
                # When unfreezing, generate new layout
                dot_source = generate_plain_dot_string(arg_framework, dot_layout, raw_json)
        elif triggered_id in ["21-abstract-graph-layout"]:
            if layout_freeze:
                # If layout is frozen, use the existing dot source
                if current_dot_source:
                    dot_source = current_dot_source
                else:
                    dot_source = generate_plain_dot_string(arg_framework, dot_layout, raw_json)
            else:
                # If not frozen, generate new layout
                dot_source = generate_plain_dot_string(arg_framework, dot_layout, raw_json)
                os.makedirs("temp", exist_ok=True)
                with open("temp/layout.dot", "w") as dot_file:
                    dot_file.write(dot_source)
                subprocess.run(
                    ["dot", "-Tplain", "temp/layout.dot", "-o", "temp/layout.txt"],
                    check=True,
                )
        else:
            if layout_freeze:
                # If layout is frozen, use the existing dot source
                if current_dot_source:
                    dot_source = current_dot_source
                else:
                    dot_source = generate_plain_dot_string(arg_framework, dot_layout, raw_json)
            else:
                # If not frozen, generate new layout
                dot_source = generate_plain_dot_string(arg_framework, dot_layout, raw_json)
        selected_arguments_changed = False
    # ========================== Provenance Session ==========================
    elif active_item == "Provenance":
        # Always use generate_dot_string but adjust dot_rank based on selection
        if selected_arguments:
            dot_source = generate_dot_string(
                arg_framework,
                selected_arguments,  # Use empty dict if no selection
                True,
                dot_layout,
                dot_rank,  # Set rank to None if no selection
                special_handling,
                layout_freeze,
                raw_json=raw_json,
            )
        else:
            dot_source = generate_plain_dot_string(arg_framework, dot_layout, raw_json)
        if prov_arg:
            #local view information calculation
            if local_view:
                hl_edges, hl_nodes = get_provenance(arg_framework, prov_type, prov_arg)
                local_view_rank = get_local_view_rank(arg_framework, prov_arg)
                dot_source = highlight_dot_source(dot_source, hl_nodes, prov_arg, prov_type, local_view, local_view_rank)
            else:
                hl_edges, hl_nodes = get_provenance(arg_framework, prov_type, prov_arg)
                dot_source = highlight_dot_source(dot_source, hl_nodes, prov_arg, prov_type, local_view)
        # else:
        #     raise PreventUpdate
    # ========================== Critical Attacks Session ==========================
    elif active_item == "CriticalAttacks":
        # Generate fresh dot source
        dot_source = generate_dot_string(
                    arg_framework,
                    selected_arguments,
                    True,
                    dot_layout,
                    dot_rank,
                    special_handling,
                    layout_freeze,
                    raw_json=raw_json,
                )
        temp_dot_source = dot_source
        
        # Add highlighting for selected fixes
        if selected_fix:
            dot_source = highlight_critical_edges(dot_source, selected_fix)
            # print(triggered_id, apply_fix_switch)
            if apply_fix_switch:  # Switch is turned ON
                # Convert selected_fix from list of lists to the format "(A,B)"
                selected_fix_strings = {f"({fix[0]},{fix[1]})" for fix in selected_fix}
                # Remove the selected critical edges from attacks by reconstructing each attack string
                fixed_attacks = []
                i = 0
                while i < len(attacks):
                    # Each attack is in format ['(', 'A', ',', 'B', ')', '\n', ...]
                    if i + 4 < len(attacks):  # Make sure we have enough characters
                        attack_str = ''.join(attacks[i:i+5])  # Join '(', 'A', ',', 'B', ')'
                        if attack_str not in selected_fix_strings:
                            # Keep the original character-by-character format
                            fixed_attacks.extend([c for c in attack_str])
                            if i + 5 < len(attacks) and attacks[i + 5] == '\n':
                                fixed_attacks.append('\n')
                        i += 6  # Skip to next attack (including '\n')
                    else:
                        fixed_attacks.extend(attacks[i:])
                        break
                
                # Convert fixed_attacks list to string before passing to read_argumentation_framework
                fixed_attacks_str = ''.join(fixed_attacks)
                fixed_arg_framework = read_argumentation_framework(arguments, fixed_attacks_str)
                dot_source = recalculate_fixed_args(fixed_arg_framework, dot_source)
            else:  # Switch is OFF
                dot_source = highlight_critical_edges(temp_dot_source, selected_fix)
    # ========================== Semantics Session ==========================
    else:
        if (
            selected_arguments == {}
            # or triggered_id == "21-abstract-graph-layout"
        ):
            dot_source = generate_plain_dot_string(arg_framework, dot_layout, raw_json)
        else:
            if triggered_id == "layout-freeze-switch":
                if layout_freeze:
                    # When freezing, use existing layout file if it exists
                    dot_source = generate_dot_string(
                        arg_framework,
                        selected_arguments,
                        True,
                        dot_layout,
                        dot_rank,
                        special_handling,
                        layout_freeze,
                        layout_file="temp/layout.txt",
                        raw_json=raw_json,
                    )
                else:
                    # When unfreezing, generate new layout
                    dot_source = generate_dot_string(
                        arg_framework,
                        selected_arguments,
                        True,
                        dot_layout,
                        dot_rank,
                        special_handling,
                        layout_freeze,
                        raw_json=raw_json,
                    )
                    os.makedirs("temp", exist_ok=True)
                    with open("temp/layout.dot", "w") as dot_file:
                        dot_file.write(dot_source)
                    subprocess.run(
                        ["dot", "-Tplain", "temp/layout.dot", "-o", "temp/layout.txt"],
                        check=True,
                    )
            elif (
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
                    raw_json=raw_json,
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
                    raw_json=raw_json,
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
                    raw_json=raw_json,
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
    # Layout direction controls
    Output("layout-direction-label", "style"),
    Output("21-abstract-graph-layout", "style"),
    # Freeze layout controls
    Output("layout-freeze-label", "style"),
    Output("layout-freeze-switch", "disabled"),
    # Global view controls
    Output("global-view-label", "style"),
    Output("global-local-switch", "disabled"),
    # Download button
    Output("21-dot-download-button", "style"),
    Input("layout-freeze-switch", "value"),
    Input("abstract-evaluation-accordion", "active_item"),
    Input("abstract-arguments", "value"),
    Input("abstract-attacks", "value"),
    Input("selected-argument-store-abstract", "data"),
)
def toggle_controls_state(layout_freeze, active_item, arguments, attacks, selected_extensions):
    """
    Controls the disabled state and styling of layout-related controls based on:
    1. Whether the layout is frozen (affects all controls except in ArgumentationFramework tab)
    2. Active tab (ArgumentationFramework, Evaluation, Provenance, or CriticalAttacks)
    3. Whether there's any graph data
    """
    disabled_style = {"pointer-events": "none", "opacity": "0.5"}
    enabled_style = {}

    # If no graph data, disable all controls
    if not (arguments and attacks):
        return (disabled_style,) * 6 + (disabled_style,)

    # Handle different tabs
    if active_item == "ArgumentationFramework":
        return (
            enabled_style,  # direction label style
            enabled_style,  # layout control style
            enabled_style,  # layout freeze label style
            False,  # layout freeze switch
            disabled_style,  # view label style
            True,  # global-local switch
            enabled_style,  # download button
        )
    
    elif active_item == "CriticalAttacks":
        if layout_freeze:
            return (
                disabled_style,  # direction label style
                disabled_style,  # layout control style
                enabled_style,  # layout freeze label style
                False,  # layout freeze switch
                disabled_style,  # view label style
                True,  # global-local switch
                enabled_style,  # download button
            )
        return (
            enabled_style,  # direction label style
            enabled_style,  # layout control style
            enabled_style,  # layout freeze label style
            False,  # layout freeze switch
            disabled_style,  # view label style
            True,  # global-local switch
            enabled_style,  # download button
        )
    
    elif active_item == "Provenance":
        if layout_freeze:
            return (
                disabled_style,  # direction label style
                disabled_style,  # layout control style
                enabled_style,  # layout freeze label style
                False,  # layout freeze switch
                disabled_style,  # view label style
                True,  # global-local switch
                enabled_style,  # download button
            )
        return (
            disabled_style,  # direction label style
            disabled_style,  # layout control style
            disabled_style,  # layout freeze label style
            True,  # layout freeze switch
            enabled_style,  # view label style
            False,  # global-local switch
            enabled_style,  # download button
        )
    
    elif active_item == "Evaluation":
        if not selected_extensions:
            return (
                enabled_style,  # direction label style
                enabled_style,  # layout control style
                enabled_style,  # layout freeze label style
                False,  # layout freeze switch
                disabled_style,  # view label style
                True,  # global-local switch
                enabled_style,  # download button
            )
        
        # Controls are disabled if layout is frozen
        if layout_freeze:
            return (
                disabled_style,  # direction label style
                disabled_style,  # layout control style
                enabled_style,  # layout freeze label style
                False,  # layout freeze switch
                disabled_style,  # view label style
                True,  # global-local switch
                enabled_style,  # download button
            )
        else:
            return (
                enabled_style,  # direction label style
                enabled_style,  # layout control style
                enabled_style,  # layout freeze label style
                False,  # layout freeze switch
                disabled_style,  # view label style
                True,  # global-local switch
                enabled_style,  # download button
            )

    return (enabled_style,) * 6 + (enabled_style,)


@callback(
    Output("layout-freeze-switch", "value"),
    Output("global-local-switch", "value"),
    Input("abstract-evaluation-accordion", "active_item"),
    State("layout-freeze-switch", "value"),
)
def reset_switches(active_item, current_freeze_value):
    """
    Reset switches based on tab:
    - ArgumentationFramework: both switches False
    - Evaluation: only local view False, freeze layout keeps current value
    - Provenance: keep existing values
    """
    if active_item == "ArgumentationFramework":
        return False, False
    elif active_item == "Evaluation":
        return current_freeze_value, False
    elif active_item == "Provenance":
        return current_freeze_value, False
    # Keep existing values in Provenance tab
    raise PreventUpdate


@callback(
    Output("prov-type-dropdown", "options"),
    Output("prov-type-dropdown", "value"),
    Input("selected-argument-store-abstract", "data"),
)
def update_provenance_dropdown_options(selected_arguments):
    """
    Updates the provenance dropdown options based on argument selection:
    - If no arguments are selected: only show 'Potential Provenance'
    - If arguments are selected: show all provenance types
    """
    if not selected_arguments:
        return [{"label": "Potential Provenance", "value": "PO"}], "PO"
    
    # Return all options when arguments are selected
    return [
        {"label": "Potential Provenance", "value": "PO"},
        {"label": "Actual Provenance", "value": "AC"},
        {"label": "Primary Provenance", "value": "PR"}
    ], "PO"
