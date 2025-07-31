# callbacks/visualization_callbacks.py

import os
import subprocess
from dash import callback, Input, Output, State, ctx, html, dcc, no_update, callback_context
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
import dash_bootstrap_components as dbc


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
                # When freezing, use current dot source or generate a new one if none exists
                if current_dot_source is None:
                    dot_source = generate_plain_dot_string(arg_framework, dot_layout, raw_json)
                else:
                    dot_source = current_dot_source
                os.makedirs("temp", exist_ok=True)
                with open("temp/layout.dot", "w") as dot_file:
                    dot_file.write(dot_source)
                # Generate position information
                subprocess.run(
                    ["dot", "-Tplain", "temp/layout.dot", "-o", "temp/layout.txt"],
                    check=True,
                )
                # Immediately update dot source with position information
                dot_source = generate_plain_dot_string(arg_framework, dot_layout, raw_json, layout_file="temp/layout.txt")
            else:
                # When unfreezing, generate new layout without saving
                dot_source = generate_plain_dot_string(arg_framework, dot_layout, raw_json)
        elif triggered_id in ["21-abstract-graph-layout"]:
            if layout_freeze:
                # If layout is frozen, use the existing dot source with saved positions
                dot_source = generate_plain_dot_string(arg_framework, dot_layout, raw_json, layout_file="temp/layout.txt")
            else:
                # If not frozen, generate new layout without saving
                dot_source = generate_plain_dot_string(arg_framework, dot_layout, raw_json)
        else:
            if layout_freeze:
                # If layout is frozen, use the existing dot source with saved positions
                dot_source = generate_plain_dot_string(arg_framework, dot_layout, raw_json, layout_file="temp/layout.txt")
            else:
                # If not frozen, generate new layout without saving
                dot_source = generate_plain_dot_string(arg_framework, dot_layout, raw_json)
        selected_arguments_changed = False
    # ========================== Provenance Session ==========================
    elif active_item == "Provenance":
        # Always use generate_dot_string but adjust dot_rank based on selection
        if selected_arguments:
            if triggered_id == "layout-freeze-switch":
                if layout_freeze:
                    # When freezing, use current dot source or generate a new one if none exists
                    if current_dot_source is None:
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
                    else:
                        dot_source = current_dot_source
                    # Save the current layout
                    os.makedirs("temp", exist_ok=True)
                    with open("temp/layout.dot", "w") as dot_file:
                        dot_file.write(dot_source)
                    # Generate position information
                    subprocess.run(
                        ["dot", "-Tplain", "temp/layout.dot", "-o", "temp/layout.txt"],
                        check=True,
                    )
                    # Immediately update dot source with position information
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
                    # When unfreezing, generate new layout without saving
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
            elif layout_freeze:
                # If layout is frozen, use the saved positions but update highlighting
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
        else:
            if triggered_id == "layout-freeze-switch":
                if layout_freeze:
                    # When freezing, use current dot source or generate a new one if none exists
                    if current_dot_source is None:
                        dot_source = generate_plain_dot_string(arg_framework, dot_layout, raw_json)
                    else:
                        dot_source = current_dot_source
                    # Save the current layout
                    os.makedirs("temp", exist_ok=True)
                    with open("temp/layout.dot", "w") as dot_file:
                        dot_file.write(dot_source)
                    # Generate position information
                    subprocess.run(
                        ["dot", "-Tplain", "temp/layout.dot", "-o", "temp/layout.txt"],
                        check=True,
                    )
                    # Immediately update dot source with position information
                    dot_source = generate_plain_dot_string(arg_framework, dot_layout, raw_json, layout_file="temp/layout.txt")
                else:
                    # When unfreezing, generate new layout without saving
                    dot_source = generate_plain_dot_string(arg_framework, dot_layout, raw_json)
            elif layout_freeze:
                # If layout is frozen, use the saved positions
                dot_source = generate_plain_dot_string(arg_framework, dot_layout, raw_json, layout_file="temp/layout.txt")
            else:
                dot_source = generate_plain_dot_string(arg_framework, dot_layout, raw_json)

        if prov_arg:
            # Only allow local view if layout is not frozen
            if local_view and not layout_freeze:
                hl_edges, hl_nodes = get_provenance(arg_framework, prov_type, prov_arg)
                local_view_rank = get_local_view_rank(arg_framework, prov_arg)
                dot_source = highlight_dot_source(dot_source, hl_nodes, prov_arg, prov_type, local_view, local_view_rank)
            else:
                # Force global view if layout is frozen
                hl_edges, hl_nodes = get_provenance(arg_framework, prov_type, prov_arg)
                # Always use global view (False) when layout is frozen
                dot_source = highlight_dot_source(dot_source, hl_nodes, prov_arg, prov_type, False)
    # ========================== Critical Attacks Session ==========================
    elif active_item == "CriticalAttacks":
        if triggered_id == "layout-freeze-switch":
            if layout_freeze:
                # When freezing, use current dot source or generate a new one if none exists
                if current_dot_source is None:
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
                else:
                    dot_source = current_dot_source
                # Save the current layout
                os.makedirs("temp", exist_ok=True)
                with open("temp/layout.dot", "w") as dot_file:
                    dot_file.write(dot_source)
                # Generate position information
                subprocess.run(
                    ["dot", "-Tplain", "temp/layout.dot", "-o", "temp/layout.txt"],
                    check=True,
                )
                # Immediately update dot source with position information
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
                # When unfreezing, generate new layout without saving
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
        elif layout_freeze:
            # If layout is frozen, generate a new dot source with the saved positions
            # but with Critical Attacks specific styling and highlighting
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
            # Only generate new layout when not frozen
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
        
        # Add highlighting for selected fixes
        # print(attacks)
        if selected_fix:
            dot_source = highlight_critical_edges(dot_source, selected_fix)
            
            if apply_fix_switch:  # Switch is turned ON
                # Convert selected_fix from list of lists to the format "(A,B)"
                selected_fix_strings = {f"({fix[0]},{fix[1]})" for fix in selected_fix}
                
                # Parse attacks string properly - split by lines and filter out selected fixes
                import re
                attack_lines = attacks.strip().split('\n')
                fixed_attacks_lines = []
                
                for line in attack_lines:
                    line = line.strip()
                    if line and line not in selected_fix_strings:
                        fixed_attacks_lines.append(line)
                
                # Join the remaining attacks with newlines
                fixed_attacks_str = '\n'.join(fixed_attacks_lines)
                
                # print(fixed_attacks_str)
                try:
                    fixed_arg_framework = read_argumentation_framework(arguments, fixed_attacks_str)
                    dot_source = recalculate_fixed_args(fixed_arg_framework, dot_source)
                except ValueError as e:
                    # If there's an error creating the fixed framework (e.g., invalid attacks),
                    # fall back to using the original framework
                    print(f"Warning: Could not create fixed framework: {e}")
                    # Continue with the original dot_source without applying fixes
                    pass
    # ========================== Semantics Session ==========================
    else:
        if selected_arguments == {}:
            if triggered_id == "layout-freeze-switch":
                if layout_freeze:
                    # When freezing, use current dot source or generate a new one if none exists
                    if current_dot_source is None:
                        dot_source = generate_plain_dot_string(arg_framework, dot_layout, raw_json)
                    else:
                        dot_source = current_dot_source
                    os.makedirs("temp", exist_ok=True)
                    with open("temp/layout.dot", "w") as dot_file:
                        dot_file.write(dot_source)
                    # Generate position information
                    subprocess.run(
                        ["dot", "-Tplain", "temp/layout.dot", "-o", "temp/layout.txt"],
                        check=True,
                    )
                    # Immediately update dot source with position information
                    dot_source = generate_plain_dot_string(arg_framework, dot_layout, raw_json, layout_file="temp/layout.txt")
                else:
                    # When unfreezing, generate new layout without saving
                    dot_source = generate_plain_dot_string(arg_framework, dot_layout, raw_json)
            elif layout_freeze:
                # If layout is frozen, use the existing dot source with saved positions
                dot_source = generate_plain_dot_string(arg_framework, dot_layout, raw_json, layout_file="temp/layout.txt")
            else:
                # If not frozen, generate new layout without saving
                dot_source = generate_plain_dot_string(arg_framework, dot_layout, raw_json)
        else:
            if triggered_id == "layout-freeze-switch":
                if layout_freeze:
                    # When freezing, use current dot source or generate a new one if none exists
                    if current_dot_source is None:
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
                    else:
                        dot_source = current_dot_source
                    os.makedirs("temp", exist_ok=True)
                    with open("temp/layout.dot", "w") as dot_file:
                        dot_file.write(dot_source)
                    # Generate position information
                    subprocess.run(
                        ["dot", "-Tplain", "temp/layout.dot", "-o", "temp/layout.txt"],
                        check=True,
                    )
                    # Immediately update dot source with position information
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
                    # When unfreezing, generate new layout without saving
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
            elif (
                triggered_id == "selected-argument-store-abstract"
                and not selected_arguments_changed
            ):
                if layout_freeze:
                    # If layout is frozen, use the existing dot source with saved positions
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
                    # If not frozen, generate new layout without saving
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
            elif (
                triggered_id == "selected-argument-store-abstract"
                and selected_arguments_changed
            ):
                if layout_freeze:
                    # If layout is frozen, use the existing dot source with saved positions
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
                    # If not frozen, generate new layout without saving
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
            elif triggered_id in [
                "21-abstract-graph-layout",
                "21-abstract-graph-rank",
                "21-abstract-graph-special-handling",
            ]:
                if layout_freeze:
                    # If layout is frozen, use the existing dot source with saved positions
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
                    # If not frozen, generate new layout without saving
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
    Output("global-local-switch", "style"),
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
    hidden_style = {"display": "none"}  # Style for hiding elements
    switch_base_style = {
        "transform": "scale(1.5)",
        "margin-top": "3px",
    }  # Base style for switches

    # If no graph data, disable all controls
    if not (arguments and attacks):
        return (
            disabled_style,  # direction label style
            disabled_style,  # layout control style
            disabled_style,  # layout freeze label style
            True,  # layout freeze switch (disabled)
            hidden_style,  # view label style (hidden)
            hidden_style,  # global-local switch style (hidden)
            disabled_style,  # download button
        )

    # Handle different tabs
    if active_item == "ArgumentationFramework":
        # In ArgumentationFramework tab, layout direction is disabled when frozen
        if layout_freeze:
            return (
                disabled_style,  # direction label style
                disabled_style,  # layout control style
                enabled_style,  # layout freeze label style
                False,  # layout freeze switch
                hidden_style,  # view label style (hidden)
                hidden_style,  # global-local switch style (hidden)
                enabled_style,  # download button
            )
        return (
            enabled_style,  # direction label style
            enabled_style,  # layout control style
            enabled_style,  # layout freeze label style
            False,  # layout freeze switch
            hidden_style,  # view label style (hidden)
            hidden_style,  # global-local switch style (hidden)
            enabled_style,  # download button
        )
    
    elif active_item == "CriticalAttacks":
        # In CriticalAttacks tab, layout direction is enabled only when not frozen
        if layout_freeze:
            return (
                disabled_style,  # direction label style
                disabled_style,  # layout control style
                enabled_style,  # layout freeze label style
                False,  # layout freeze switch (disabled)
                hidden_style,  # view label style (hidden)
                hidden_style,  # global-local switch style (hidden)
                enabled_style,  # download button
            )
        return (
            enabled_style,  # direction label style
            enabled_style,  # layout control style
            enabled_style,  # layout freeze label style
            False,  # layout freeze switch (enabled)
            hidden_style,  # view label style (hidden)
            hidden_style,  # global-local switch style (hidden)
            enabled_style,  # download button
        )
    
    elif active_item == "Provenance":
        # In Provenance tab, layout direction is enabled only when not frozen
        if layout_freeze:
            return (
                disabled_style,  # direction label style
                disabled_style,  # layout control style
                enabled_style,  # layout freeze label style
                False,  # layout freeze switch (enabled)
                disabled_style,  # view label style (grayed out)
                switch_base_style,  # global-local switch style (visible but disabled)
                enabled_style,  # download button
            )
        return (
            enabled_style,  # direction label style
            enabled_style,  # layout control style
            enabled_style,  # layout freeze label style
            False,  # layout freeze switch (enabled)
            enabled_style,  # view label style (visible)
            switch_base_style,  # global-local switch style (visible)
            enabled_style,  # download button
        )
    
    elif active_item == "Evaluation":
        # In Evaluation tab, layout direction is disabled when frozen, regardless of selected_extensions
        if layout_freeze:
            return (
                disabled_style,  # direction label style
                disabled_style,  # layout control style
                enabled_style,  # layout freeze label style
                False,  # layout freeze switch
                hidden_style,  # view label style (hidden)
                hidden_style,  # global-local switch style (hidden)
                enabled_style,  # download button
            )
        
        # When not frozen, enable layout direction if there are selected extensions
        if not selected_extensions:
            return (
                enabled_style,  # direction label style
                enabled_style,  # layout control style
                enabled_style,  # layout freeze label style
                False,  # layout freeze switch
                hidden_style,  # view label style (hidden)
                hidden_style,  # global-local switch style (hidden)
                enabled_style,  # download button
            )
        
        return (
            enabled_style,  # direction label style
            enabled_style,  # layout control style
            enabled_style,  # layout freeze label style
            False,  # layout freeze switch
            hidden_style,  # view label style (hidden)
            hidden_style,  # global-local switch style (hidden)
            enabled_style,  # download button
        )

    # Default case - all controls enabled except local view
    return (
        enabled_style,  # direction label style
        enabled_style,  # layout control style
        enabled_style,  # layout freeze label style
        False,  # layout freeze switch
        hidden_style,  # view label style (hidden)
        hidden_style,  # global-local switch style (hidden)
        enabled_style,  # download button
    )

@callback(
    Output("layout-freeze-switch", "value"),
    Output("global-local-switch", "value"),
    Input("abstract-evaluation-accordion", "active_item"),
    Input("21-af-filename", "value"),
    Input("examples-dropdown", "value"),
    State("layout-freeze-switch", "value"),
)
def reset_switches(active_item, filename, example_value, current_freeze_value):
    """
    Reset switches based on:
    1. Active tab (ArgumentationFramework, Evaluation, Provenance, or CriticalAttacks)
    2. File selection (turns off freeze layout when switching files)
    3. Example selection (turns off freeze layout when switching examples)
    """
    # Get the trigger that caused the callback
    trigger = ctx.triggered_id if ctx.triggered_id else None
    
    # If triggered by file or example selection, turn off freeze layout
    if trigger in ["21-af-filename", "examples-dropdown"]:
        return False, False
    
    # Handle tab changes
    if active_item == "ArgumentationFramework":
        return False, False
    elif active_item == "Evaluation":
        return current_freeze_value, False
    elif active_item == "Provenance":
        return current_freeze_value, None  # Keep both freeze layout and local/global as is
    elif active_item == "CriticalAttacks":
        return current_freeze_value, False  # Keep freeze layout, reset local view
    
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


# Add new callback for dynamic legend
@callback(
    [Output("legend-card", "style"),
     Output("legend-toggle-button", "children"),
     Output("legend-toggle-button", "style"),
     Output("legend-state-store", "data")],  # Add output for store
    [Input("legend-toggle-button", "n_clicks"),
     Input("explanation-graph", "dot_source"),
     Input("abstract-evaluation-accordion", "active_item")],  # Add active_item as input
    [State("legend-card", "style"),
     State("legend-state-store", "data")],  # Add state for store
    prevent_initial_call=False
)
def toggle_legend(n_clicks, dot_source, active_item, current_style, stored_state):
    # Get the trigger that caused the callback
    trigger = ctx.triggered_id if ctx.triggered_id else None
    
    if not dot_source:
        # If there's no graph, hide both the legend and the button
        button_style = {
            "position": "absolute",
            "left": "-35px",
            "bottom": "20px",
            "zIndex": 2000,
            "backgroundColor": "white",
            "border": "1px solid #ccc",
            "borderRadius": "4px",
            "width": "30px",
            "height": "30px",
            "cursor": "pointer",
            "display": "none",  # Hide the button when no graph
            "alignItems": "center",
            "justifyContent": "center",
            "fontSize": "16px",
            "padding": "0",
            "boxShadow": "0 2px 4px rgba(0,0,0,0.1)"
        }
        return {"display": "none"}, "▶", button_style, stored_state

    # Initialize the display state from stored state
    is_visible = stored_state.get('is_visible', True) if stored_state else True
    
    # Only toggle if the button was clicked
    if trigger == "legend-toggle-button":
        is_visible = not is_visible
    
    # Set the new display state
    new_display = "block" if is_visible else "none"
    button_text = "◀" if is_visible else "▶"  # Left arrow when visible, right arrow when hidden
    
    # Update the legend style
    legend_style = {
        "position": "absolute",
        "bottom": "20px",
        "left": "20px",
        "zIndex": 1999,
        "backgroundColor": "rgba(255, 255, 255, 0.95)",  # More opaque background
        "boxShadow": "0 2px 4px rgba(0,0,0,0.2)",  # Stronger shadow
        "borderRadius": "8px",
        "padding": "15px",
        "minWidth": "300px",
        "maxWidth": "350px",
        "display": new_display,
        "border": "1px solid #dee2e6"  # Add border for better visibility
    }
    
    # Update the button style
    button_style = {
        "position": "absolute",
        "left": "-35px",
        "bottom": "20px",
        "zIndex": 2000,
        "backgroundColor": "white",
        "border": "1px solid #ccc",
        "borderRadius": "4px",
        "width": "30px",
        "height": "30px",
        "cursor": "pointer",
        "display": "flex",  # Always show the button when there's a graph
        "alignItems": "center",
        "justifyContent": "center",
        "fontSize": "16px",
        "padding": "0",
        "boxShadow": "0 2px 4px rgba(0,0,0,0.1)"
    }
    
    # Update the stored state
    new_stored_state = {'is_visible': is_visible}
    
    return legend_style, button_text, button_style, new_stored_state


@callback(
    Output("node-colors-legend", "children"),
    Input("explanation-graph", "dot_source"),
    Input("prov-type-dropdown", "value"),
    Input("abstract-evaluation-accordion", "active_item"),
    Input("layout-freeze-switch", "value"),
    prevent_initial_call=False
)
def update_legend(dot_source, prov_type, active_item, layout_freeze):
    if not dot_source:
        return html.Div()
    
    used_colors = set()
    total_nodes = 0
    nodes_with_fillcolor = 0
    
    for line in dot_source.split('\n'):
        if '->' not in line and '[' in line:
            if 'fillcolor=' in line:
                nodes_with_fillcolor += 1
                if 'fillcolor="white"' in line:
                    used_colors.add("#ffffff")
                else:
                    parts = line.split('fillcolor="')
                    for part in parts[1:]:
                        color = part.split('"')[0].lower()
                        if color.startswith('#'):
                            used_colors.add(color)
            if 'label=' in line:
                total_nodes += 1
    
    legend_items = []
    
    # Add a title to the legend
    # legend_items.append(
    #     html.H6("Node Colors", className="mb-3 text-primary", style={"fontWeight": "bold"})
    # )
    
    # Define all possible color labels
    all_color_labels = {
        # Evaluation colors
        "#40cfff": "IN (skeptical)",
        "#a6e9ff": "IN (credulous)",
        "#ffb763": "OUT (skeptical)",
        "#ffe6c9": "OUT (credulous)",
        "#fefe62": "UNDEC",
        # Provenance colors
        "#ffffff": "Cannot reach target",
        "#bebebe": "Can reach target"
    }
    
    # For actual provenance (AC) or primary provenance (PR), show all colors present in the dot source
    if active_item == "Provenance" and prov_type in ["AC", "PR"]:
        # Create a list of colors in a specific order, prioritizing evaluation colors
        ordered_colors = [
            "#40cfff", "#a6e9ff", "#ffb763", "#ffe6c9", "#fefe62",  # Evaluation colors
            "#ffffff", "#bebebe"  # Provenance colors
        ]
        # Filter to only include colors that are actually present
        legend_order = [color for color in ordered_colors if color in used_colors]
    # For potential provenance (PO), show only provenance colors if present
    elif "#ffffff" in used_colors or "#bebebe" in used_colors:
        legend_order = []
        if "#ffffff" in used_colors:
            legend_order.append("#ffffff")
        if "#bebebe" in used_colors:
            legend_order.append("#bebebe")
    # For all other cases, show evaluation colors
    else:
        legend_order = [
            "#40cfff",
            "#a6e9ff",
            "#ffb763",
            "#ffe6c9",
            "#fefe62",
        ]
        if nodes_with_fillcolor < total_nodes:
            legend_items.append(
                html.Div([
                    html.Div(style={
                        "width": "20px",
                        "height": "20px",
                        "backgroundColor": "#FFFFFF",
                        "border": "1px solid #666",
                        "borderRadius": "50%",
                        "display": "inline-block",
                        "marginRight": "8px",
                        "verticalAlign": "middle"
                    }),
                    html.Span("Unlabeled", style={"verticalAlign": "middle"})
                ], className="mb-2")
            )

    # Add colors that are actually present in the dot source
    for color in legend_order:
        if color in used_colors and color in all_color_labels:
            legend_items.append(
                html.Div([
                    html.Div(style={
                        "width": "20px",
                        "height": "20px",
                        "backgroundColor": color,
                        "border": "1px solid #666",
                        "borderRadius": "50%",
                        "display": "inline-block",
                        "marginRight": "8px",
                        "verticalAlign": "middle"
                    }),
                    html.Span(all_color_labels[color], style={"verticalAlign": "middle"})
                ], className="mb-2")
            )

    # Add a note about layout freeze if active
    if layout_freeze:
        legend_items.append(
            html.Div([
                html.I(className="fas fa-lock me-2"),
                html.Span("Layout is frozen", style={"color": "#666", "fontStyle": "italic"})
            ], className="mt-3 pt-2 border-top")
        )

    return html.Div([
        html.Div(legend_items, style={"fontSize": "14px"})
    ])


@callback(
    Output("node-details-panel", "style"),
    Output("node-panel-toggle-button", "children"),
    Output("node-panel-toggle-button", "style"),
    Output("node-panel-state-store", "data"),
    Input("node-panel-toggle-button", "n_clicks"),
    Input("explanation-graph", "selected_node"),
    Input("explanation-graph", "selected_edge"),
    State("node-panel-state-store", "data"),
    prevent_initial_call=True
)
def toggle_node_panel(n_clicks, selected_node, selected_edge, stored_state):
    """Toggle the visibility of the node details panel."""
    ctx = callback_context
    if not ctx.triggered:
        return no_update, no_update, no_update, no_update
    
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    # Initialize the display state from stored state
    is_visible = stored_state.get('is_visible', False) if stored_state else False
    
    # If a node or edge was selected, show the panel
    if trigger_id == "explanation-graph" and (selected_node or selected_edge):
        is_visible = True
    # If the toggle button was clicked, toggle the visibility
    elif trigger_id == "node-panel-toggle-button":
        is_visible = not is_visible
    
    # Set the new display state
    new_display = "block" if is_visible else "none"
    button_text = "◀" if is_visible else "▶"  # Left arrow when visible, right arrow when hidden
    
    # Update the panel style
    panel_style = {
        "position": "absolute",
        "top": "40px",  # Move down from top to give more space
        "right": "20px",
        "zIndex": 1999,
        "backgroundColor": "rgba(255, 255, 255, 0.9)",
        "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
        "borderRadius": "8px",
        "padding": "15px",
        "minWidth": "300px",
        "maxWidth": "350px",
        "maxHeight": "470px",  # Reduced from 550px to fit within visualization
        "overflowY": "auto",  # Enable vertical scrolling
        "display": new_display,
        "pointerEvents": "auto",
        "marginBottom": "40px"  # Add space at the bottom
    }
    
    # Update the button style
    button_style = {
        "position": "absolute",
        "right": "-35px",
        "top": "50%",  # Center vertically
        "transform": "translateY(-50%)",  # Center vertically
        "zIndex": 2000,
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
        "boxShadow": "0 2px 4px rgba(0,0,0,0.1)"
    }
    
    # Update the stored state
    new_stored_state = {'is_visible': is_visible}
    
    return panel_style, button_text, button_style, new_stored_state


@callback(
    Output("node-details-content", "children"),
    Output("selected-node-store", "data"),
    Input("explanation-graph", "selected_node"),
    Input("explanation-graph", "selected_edge"),
    State("abstract-arguments", "value"),
    State("abstract-attacks", "value"),
    State("raw-json", "data"),
    prevent_initial_call=True
)
def update_node_details(selected_node, selected_edge, arguments, attacks, raw_json):
    """Update the node details content when a node or edge is selected."""
    ctx = callback_context
    if not ctx.triggered:
        return None, None
    
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    # Handle edge selection
    if trigger_id == "explanation-graph" and selected_edge:
        # Parse the edge string (format: "from->to")
        from_arg, to_arg = selected_edge.split("->")
        
        # Get edge metadata and argument names from raw_json
        edge_meta = None
        from_arg_name = None
        to_arg_name = None
        if raw_json and isinstance(raw_json, dict):
            # Get edge metadata
            for defeat in raw_json.get("defeats", []):
                if defeat.get("from") == from_arg and defeat.get("to") == to_arg:
                    edge_meta = defeat
                    break
            
            # Get argument names
            for arg in raw_json.get("arguments", []):
                if arg.get("id") == from_arg:
                    from_arg_name = arg.get("name")
                elif arg.get("id") == to_arg:
                    to_arg_name = arg.get("name")
                if from_arg_name and to_arg_name:  # Stop searching if we found both names
                    break
        
        # Create edge details content
        content = []
        
        # Add edge relationship header (simple format)
        content.append(html.H4(f"Attack: {from_arg} → {to_arg}", className="mb-2 text-primary"))
        
        # Add argument information
        content.append(html.Div([
            # Attacking argument
            html.Div([
                html.H6(f"Argument {from_arg}", className="mb-2 text-secondary"),
                html.P(from_arg_name if from_arg_name else "No name available", 
                      className="mb-3 p-2 bg-light rounded")
            ], className="mb-3"),
            # Attacked argument
            html.Div([
                html.H6(f"Argument {to_arg}", className="mb-2 text-secondary"),
                html.P(to_arg_name if to_arg_name else "No name available", 
                      className="mb-3 p-2 bg-light rounded")
            ], className="mb-3")
        ]))
        
        # Add annotation if available
        if edge_meta and edge_meta.get("annotation"):
            content.append(html.Div([
                html.H6("Annotation", className="mb-2 text-secondary"),
                html.P(edge_meta["annotation"], className="mb-3 p-2 bg-light rounded")
            ], className="mb-3"))
        else:
            # If no annotation, show a message
            content.append(html.Div([
                html.I("No annotation available for this attack", className="text-muted")
            ], className="mb-3"))
        
        # Store selected edge data
        edge_data = {
            "from": from_arg,
            "to": to_arg,
            "from_name": from_arg_name,
            "to_name": to_arg_name,
            "metadata": edge_meta
        }
        
        return content, edge_data
    
    # Handle node selection
    if not selected_node:
        return None, None
    
    # Get node metadata from raw_json
    node_meta = None
    if raw_json and isinstance(raw_json, dict):
        for arg in raw_json.get("arguments", []):
            if arg.get("id") == selected_node:
                node_meta = arg
                break
    
    # Create node details content
    content = []
    
    # Add node ID (mandatory)
    content.append(html.H4(f"Argument {selected_node}", className="mb-2 text-primary"))
    
    # Add name if available (mandatory)
    if node_meta and node_meta.get("name"):
        content.append(html.Div([
            html.H6("Name", className="mb-2 text-secondary"),
            html.P(node_meta["name"], className="mb-3 p-2 bg-light rounded")
        ], className="mb-3"))
    else:
        # If name is missing, show a warning
        content.append(html.Div([
            html.I("Warning: Argument name is missing", className="text-warning")
        ], className="mb-3"))
    
    # Optional fields - only add sections if the field exists in metadata
    if node_meta:
        # Case information (if either case_name or case_year exists)
        if node_meta.get("case_name") or node_meta.get("case_year"):
            case_info = []
            if node_meta.get("case_name"):
                case_info.append(node_meta["case_name"])
            if node_meta.get("case_year"):
                case_info.append(str(node_meta["case_year"]))
            if node_meta.get("citation"):
                case_info.append(f"({node_meta['citation']})")
            content.append(html.Div([
                html.H6("Case", className="mb-2 text-secondary"),
                html.P(" ".join(case_info), className="mb-3 p-2 bg-light rounded")
            ], className="mb-3"))
        
        # Argument type
        if node_meta.get("type"):
            content.append(html.Div([
                html.H6("Type", className="mb-2 text-secondary"),
                html.P(node_meta["type"].replace("_", " ").title(), className="mb-3 p-2 bg-light rounded")
            ], className="mb-3"))
        
        # Context
        if node_meta.get("context"):
            content.append(html.Div([
                html.H6("Context", className="mb-2 text-secondary"),
                html.P(node_meta["context"], className="mb-3 p-2 bg-light rounded")
            ], className="mb-3"))
        
        # URL (if exists)
        if node_meta.get("url"):
            content.append(html.Div([
                html.H6("Reference", className="mb-2 text-secondary"),
                html.A(
                    node_meta["url"],
                    href=node_meta["url"],
                    target="_blank",
                    className="text-primary text-decoration-none",
                    style={"wordBreak": "break-all"}
                )
            ], className="mb-3"))
    
    # Store selected node data
    node_data = {
        "id": selected_node,
        "metadata": node_meta
    }
    
    return content, node_data


@callback(
    Output("filename-display", "children"),
    Input("21-af-filename", "value"),
    prevent_initial_call=False
)
def update_filename_display(filename):
    """Update the filename display when a file is selected."""
    if not filename:
        return ""
    return f"File: {filename}"

