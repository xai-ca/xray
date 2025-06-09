from dash import Input, Output, State, callback, callback_context, no_update
from dash.exceptions import PreventUpdate
import html
import clingo
from py_arg_visualisation.functions.import_functions.read_argumentation_framework_functions import (
    read_argumentation_framework,
)


@callback(
    [
        Output("selected-extension-display", "children"),
        Output("possible-fixes-radio", "value", allow_duplicate=True),  # Add radio reset output
        Output("apply-fix-switch", "value", allow_duplicate=True),  # Add switch reset output
    ],
    [
        Input("selected-argument-store-abstract", "data"),
        Input("abstract-evaluation-accordion", "active_item"),
    ],
    prevent_initial_call=True
)
def update_selected_extension_display(selected_arguments, active_item):
    
    if not active_item:  # Check if active_item is None or empty
        raise PreventUpdate
        
    if active_item != "CriticalAttacks":
        raise PreventUpdate
        
    if not selected_arguments:
        print("No arguments selected")  # Debug print
        return "No extension selected", None, False  # Return False to reset switch
    
    try:
        # Ensure selected_arguments is a dictionary
        if not isinstance(selected_arguments, dict):
            return "Invalid extension data", None, False
            
        # Get only the green arguments
        green_arguments = selected_arguments.get('green', [])
        if not green_arguments:  # Check if green arguments list is empty
            return "No green arguments selected", None, False
            
        result = f"{{ {', '.join(green_arguments)} }}"
        # print(f"Returning result: {result}")  # Debug print
        return result, None, False  # Return False to reset switch
    except Exception as e:
        print(f"Error occurred: {e}")  # Debug print
        return "Invalid extension data", None, False

@callback(
    [
        Output("possible-fixes-radio", "options"),
        Output("available-fixes-store", "data")
    ],
    [
        Input("abstract-arguments", "value"),
        Input("abstract-attacks", "value"),
        Input("selected-argument-store-abstract", "data"),
        Input("possible-fixes-radio", "value")
    ],
    State("available-fixes-store", "data"),
    prevent_initial_call=True
)
def handle_critical_attacks(arguments, attacks, selected_extension, selected_radio_value, current_fixes):
    """
    Calculates possible fixes and handles radio selection using Clingo ASP solver.
    """
    ctx = callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

    # Handle radio selection
    if triggered_id == "possible-fixes-radio":
        if not selected_radio_value or selected_radio_value == "none":
            return no_update, []
        # Parse the selected value to get the critical pairs
        # Split by '_' and skip the 'answer_N' prefix
        parts = selected_radio_value.split("_")[2:]
        # Group parts into pairs
        edges = [[parts[i], parts[i+1]] for i in range(0, len(parts), 2)]
        return no_update, edges

    # Handle initial calculation
    if not all([arguments, attacks, selected_extension]):
        raise PreventUpdate
    
    arg_framework = read_argumentation_framework(arguments, attacks)

    # Generate attack facts
    attack_facts = "\n".join(
        [f'attacks("{attack.from_argument}","{attack.to_argument}").'
         for attack in arg_framework.defeats]
    )
    
    # Generate argument facts for all arguments in the framework
    argument_facts = "\n".join(
        [f'arg("{arg}").' for arg in arg_framework.arguments]
    )
    
    # Parse selected extension and generate in/1, out/1, and undec/1 facts
    accepted_args = selected_extension.get('green', [])
    rejected_args = selected_extension.get('red', [])
    undecided_args = selected_extension.get('yellow', [])  # Add yellow arguments
    
    extension_facts = "\n".join([
        f':- not in("{arg}").' for arg in accepted_args
    ] + [
        f':- not out("{arg}").' for arg in rejected_args
    ] + [
        f':- not undec("{arg}").' for arg in undecided_args  # Add constraints for undecided arguments
    ])
    
    # Combine all facts
    facts = argument_facts + "\n" + attack_facts + "\n" + extension_facts
    # print(facts)
    try:
        # Initialize Clingo control
        ctl = clingo.Control(["--opt-mode=optN"])  # we can use quiet=1 get the distinct results but Clingo python doesn't support it
        
        # Add combined facts to Clingo
        ctl.add("base", [], facts)
        # print(facts)
        # Add ASP rules (to be implemented in separate file)
        ctl.load("encodings/critical_cal.dl")  # TODO: Implement this encoding
        
        # Ground and solve
        ctl.ground([("base", [])])
        models = []
        ctl.solve(on_model=lambda m: models.append(m.symbols(shown=True)))
        
        if not models:
            return [{"label": "No critical attacks under the selected extension", "value": "none"}], []
            
        # Process all models to extract fixes
        fixes = []
        seen_critical_sets = set()
        all_critical_sets = []
        
        # First pass: collect all unique critical sets and find minimum size
        for model in models:
            critical_pairs = []
            for atom in model:
                if atom.name == "critical":
                    attacker = str(atom.arguments[0]).strip('"')
                    attacked_arg = str(atom.arguments[1]).strip('"')
                    critical_pairs.append((attacker, attacked_arg))
            
            if critical_pairs:
                critical_set = frozenset(critical_pairs)
                if critical_set not in seen_critical_sets:
                    seen_critical_sets.add(critical_set)
                    all_critical_sets.append(critical_pairs)
        
        # Find minimum size among all sets
        if all_critical_sets:
            min_size = min(len(s) for s in all_critical_sets)
            
            # Second pass: only process sets of minimum size
            for critical_pairs in all_critical_sets:
                if len(critical_pairs) == min_size:
                    # Format the pairs for display
                    formatted_pairs = [f"({a}, {b})" for a, b in critical_pairs]
                    label = f"Set {len(fixes) + 1}: " + ", ".join(formatted_pairs)
                    value = f"answer_{len(fixes) + 1}_" + "_".join(
                        f"{a}_{b}" for a, b in critical_pairs
                    )
                    fixes.append({"label": label, "value": value})

        return (
            fixes if fixes else [{"label": "No critical attacks under the selected extension", "value": "none"}],
            []  # Initialize with empty list since no selection has been made yet
        )
        
    except Exception as e:
        print(f"Error calculating fixes with Clingo: {e}")
        return [{"label": "Error occurred", "value": "error"}], []

@callback(
    [
        Output("possible-fixes-radio", "style"),
        Output("possible-fixes-radio", "className"),
        Output("no-critical-attacks-hint", "style")
    ],
    Input("possible-fixes-radio", "options"),
    prevent_initial_call=True
)
def update_radio_visibility(options):
    """
    Updates the visibility and styling of the radio button based on options.
    Hides the radio when there are no critical attacks and styles the text in dark red.
    Also controls visibility of the no-critical-attacks hint.
    
    Args:
        options (list): List of radio options
        
    Returns:
        tuple: (radio style dict, radio className string, hint style dict)
    """
    if not options or (len(options) == 1 and options[0]["value"] == "none"):
        return (
            {"display": "none"},  # Hide the radio button
            "text-danger fw-bold",  # Bootstrap classes for dark red and bold text
            {"display": "block", "color": "#9f0000"}  # Show the hint
        )
    return (
        {"display": "block"},  # Show the radio button
        "",  # Default styling
        {"display": "none"}  # Hide the hint
    ) 

@callback(
    [
        Output("apply-fix-switch", "disabled"),
        Output("apply-fix-switch", "className"),
    ],
    Input("available-fixes-store", "data"),
    prevent_initial_call=True
)
def update_apply_fix_switch_state(available_fixes):
    """
    Controls the state of the apply fix switch based on available fixes.
    Disables and grays out the switch when no fixes are available.
    
    Args:
        available_fixes (list): List of available fixes
        
    Returns:
        tuple: (disabled state boolean, switch className string)
    """
    if not available_fixes:
        return True, "switch-secondary"  # Disabled and gray
    return False, "switch-primary"  # Enabled and blue

