from dash import Input, Output, State, callback, dash, no_update
from dash.exceptions import PreventUpdate
import html
import clingo
from py_arg_visualisation.functions.import_functions.read_argumentation_framework_functions import (
    read_argumentation_framework,
)


@callback(
    Output("selected-extension-display", "children"),
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
        return "No extension selected"
    
    try:
        # Ensure selected_arguments is a dictionary
        if not isinstance(selected_arguments, dict):
            return "Invalid extension data"
            
        # Get only the green arguments
        green_arguments = selected_arguments.get('green', [])
        if not green_arguments:  # Check if green arguments list is empty
            return "No green arguments selected"
            
        result = f"{{ {', '.join(green_arguments)} }}"
        # print(f"Returning result: {result}")  # Debug print
        return result
    except Exception as e:
        print(f"Error occurred: {e}")  # Debug print
        return "Invalid extension data"

@callback(
    Output("possible-fixes-radio", "options"),
    [
        Input("abstract-arguments", "value"),
        Input("abstract-attacks", "value"),
        Input("selected-argument-store-abstract", "data")
    ],
    prevent_initial_call=True
)
def calculate_critical_attacks_clingo(arguments, attacks, selected_extension):
    """
    Calculates possible fixes using Clingo ASP solver.
    
    Args:
        arguments (list): List of arguments in the framework
        attacks (list): List of attack dictionaries with 'source' and 'target' keys
        selected_extension (str): String representation of selected extension "{ arg1, arg2, ... }"
        
    Returns:
        list: List of dictionaries containing fix options for radio buttons
    """
    if not all([arguments, attacks, selected_extension]):
        raise PreventUpdate
    
    arg_framework = read_argumentation_framework(arguments, attacks)

    # Generate attack facts
    attack_facts = "\n".join(
        [f'attacks("{attack.from_argument}","{attack.to_argument}").'
         for attack in arg_framework.defeats]
    )
    
    # Parse selected extension and generate in/1, out/1, and undec/1 facts
    accepted_args = selected_extension.get('green', [])
    rejected_args = selected_extension.get('red', [])
    # Get undecided arguments (those that are neither accepted nor rejected)
    undec_args = selected_extension.get('yellow', [])
    
    extension_facts = "\n".join([
        f'in("{arg}").' for arg in accepted_args
    ] + [
        f'out("{arg}").' for arg in rejected_args
    ] + [
        f'undec("{arg}").' for arg in undec_args
    ])
    
    # Combine all facts
    facts = attack_facts + "\n" + extension_facts
    print(facts)
    try:
        # Initialize Clingo control
        ctl = clingo.Control(["--warn=none"])
        
        # Add combined facts to Clingo
        ctl.add("base", [], facts)
        
        # Add ASP rules (to be implemented in separate file)
        ctl.load("encodings/critical_cal.dl")  # TODO: Implement this encoding
        
        # Ground and solve
        ctl.ground([("base", [])])
        models = []
        ctl.solve(on_model=lambda m: models.append(m.symbols(shown=True)))
        
        if not models:
            return [{"label": "No critical attacks under the selected extension", "value": "none"}]
            
        # Process the model to extract fixes
        fixes = []
        for atom in models[0]:
            if atom.name == "critical":
                attacked_arg = str(atom.arguments[0]).strip('"')
                attacker = str(atom.arguments[1]).strip('"')
                fixes.append({
                    "label": f"Critical({attacker}, {attacked_arg})", 
                    "value": f"{attacked_arg}_{attacker}"
                })
                
        return fixes if fixes else [{"label": "No critical attacks under the selected extension", "value": "none"}]
        
    except Exception as e:
        print(f"Error calculating fixes with Clingo: {e}")
        return [{"label": "Error occurred", "value": "error"}] 

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