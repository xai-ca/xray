# callbacks/solution_callbacks.py

from dash import html, callback, Input, Output, State, callback_context, exceptions
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

# Import PyArg semantic functions and readers
from py_arg.abstract_argumentation.semantics.get_argumentation_framework_extensions import (
    get_argumentation_framework_extensions,
)
from py_arg_visualisation.functions.import_functions.read_argumentation_framework_functions import (
    read_argumentation_framework,
)


# -- Callback for evaluating the abstract argumentation framework --
@callback(
    Output("21-abstract-evaluation-semantics", "children"),
    Output("grounded-extension-long-str-store", "data"),
    State("abstract-arguments", "value"),
    State("abstract-attacks", "value"),
    Input("abstract-evaluation-accordion", "active_item"),
    Input("abstract-evaluation-semantics", "value"),
    prevent_initial_call=True,
)
def evaluate_abstract_argumentation_framework(
    arguments, attacks, active_item, semantics
):
    if active_item != "Evaluation":
        raise PreventUpdate

    arg_framework = read_argumentation_framework(arguments, attacks)
    frozen_extensions = get_argumentation_framework_extensions(
        arg_framework, "Complete"
    )
    extensions = [set(frozen_ext) for frozen_ext in frozen_extensions]

    extension_dict = {}
    for extension in sorted(extensions):
        out_arguments = {
            attacked
            for attacked in arg_framework.arguments
            if any(
                arg in arg_framework.get_incoming_defeat_arguments(attacked)
                for arg in extension
            )
        }
        undecided_arguments = {
            argument
            for argument in arg_framework.arguments
            if argument not in extension and argument not in out_arguments
        }
        extension_readable_str = (
            "{" + ", ".join(arg.name for arg in sorted(extension)) + "}"
        )
        extension_in_str = "+".join(arg.name for arg in sorted(extension))
        extension_out_str = "+".join(arg.name for arg in sorted(out_arguments))
        extension_undecided_str = "+".join(
            arg.name for arg in sorted(undecided_arguments)
        )
        extension_long_str = "|".join(
            [extension_in_str, extension_undecided_str, extension_out_str]
        )
        extension_dict[extension_readable_str] = extension_long_str

    grounded_extensions = get_argumentation_framework_extensions(
        arg_framework, "Grounded"
    )
    stable_extensions = get_argumentation_framework_extensions(arg_framework, "Stable")
    preferred_extensions = get_argumentation_framework_extensions(
        arg_framework, "Preferred"
    )
    complete_extensions = get_argumentation_framework_extensions(
        arg_framework, "Complete"
    )

    # Create radio items for each semantic group
    grounded_extension_radioitems = dbc.RadioItems(
        options=[
            {"label": label, "value": value}
            for label, value in extension_dict.items()
            if label
            in [
                f"{{{', '.join(arg.name for arg in sorted(ext))}}}"
                for ext in grounded_extensions
            ]
        ],
        id="extension-radioitems-grounded",
        inline=True,
    )
    stable_extension_radioitems = dbc.RadioItems(
        options=[
            {"label": label, "value": value}
            for label, value in extension_dict.items()
            if label
            in [
                f"{{{', '.join(arg.name for arg in sorted(ext))}}}"
                for ext in stable_extensions
            ]
        ],
        id="extension-radioitems-stable",
        inline=True,
    )
    preferred_non_stable_extension_radioitems = dbc.RadioItems(
        options=[
            {"label": label, "value": value}
            for label, value in extension_dict.items()
            if label
            in [
                f"{{{', '.join(arg.name for arg in sorted(ext))}}}"
                for ext in preferred_extensions - stable_extensions
            ]
        ],
        id="extension-radioitems-preferred",
        inline=True,
    )
    other_complete_extension_radioitems = dbc.RadioItems(
        options=[
            {"label": label, "value": value}
            for label, value in extension_dict.items()
            if label
            in [
                f"{{{', '.join(arg.name for arg in sorted(ext))}}}"
                for ext in complete_extensions
                - grounded_extensions
                - stable_extensions
                - preferred_extensions
            ]
        ],
        id="extension-radioitems-other",
        inline=True,
    )

    semantics_div = html.Div(children=[])
    if semantics == "Grounded":
        semantics_div.children.extend(
            [
                html.Br(),
                html.B("Grounded Extension:"),
                html.Div(
                    grounded_extension_radioitems,
                    style={
                        "border": "2px dotted lightblue",
                        "border-radius": "10px",
                        "padding": "10px",
                    },
                ),
                html.Br(),
                html.Div(
                    [
                        dbc.RadioItems(id="extension-radioitems-stable"),
                        dbc.RadioItems(id="extension-radioitems-preferred"),
                        dbc.RadioItems(id="extension-radioitems-other"),
                    ]
                ),
            ]
        )
    elif semantics == "Stable":
        semantics_div.children.extend(
            [
                html.Br(),
                html.B("Stable Extensions:"),
                html.Div(
                    stable_extension_radioitems,
                    style={
                        "border": "2px dotted lightblue",
                        "border-radius": "10px",
                        "padding": "10px",
                    },
                ),
                html.Br(),
                html.Div(
                    [
                        dbc.RadioItems(id="extension-radioitems-grounded"),
                        dbc.RadioItems(id="extension-radioitems-preferred"),
                        dbc.RadioItems(id="extension-radioitems-other"),
                    ]
                ),
            ]
        )
    elif semantics == "Preferred":
        semantics_div.children.extend(
            [
                html.Br(),
                html.B("Stable Extensions:"),
                html.Div(
                    stable_extension_radioitems,
                    style={
                        "border": "2px dotted lightblue",
                        "border-radius": "10px",
                        "padding": "10px",
                    },
                ),
                html.Br(),
                html.B("Preferred Non-Stable Extensions:"),
                html.Div(
                    preferred_non_stable_extension_radioitems,
                    style={
                        "border": "2px dotted lightblue",
                        "border-radius": "10px",
                        "padding": "10px",
                    },
                ),
                html.Br(),
                html.Div(
                    [
                        dbc.RadioItems(id="extension-radioitems-grounded"),
                        dbc.RadioItems(id="extension-radioitems-other"),
                    ]
                ),
            ]
        )
    elif semantics == "Complete":
        semantics_div.children.extend(
            [
                html.Br(),
                html.B("Grounded Extension:"),
                html.Div(
                    grounded_extension_radioitems,
                    style={
                        "border": "2px dotted lightblue",
                        "border-radius": "10px",
                        "padding": "10px",
                    },
                ),
                html.Br(),
                html.B("Stable Extensions:"),
                html.Div(
                    stable_extension_radioitems,
                    style={
                        "border": "2px dotted lightblue",
                        "border-radius": "10px",
                        "padding": "10px",
                    },
                ),
                html.Br(),
                html.B("Preferred Non-Stable Extensions:"),
                html.Div(
                    preferred_non_stable_extension_radioitems,
                    style={
                        "border": "2px dotted lightblue",
                        "border-radius": "10px",
                        "padding": "10px",
                    },
                ),
                html.Br(),
                html.B("Other Complete Extensions:"),
                html.Div(
                    other_complete_extension_radioitems,
                    style={
                        "border": "2px dotted lightblue",
                        "border-radius": "10px",
                        "padding": "10px",
                    },
                ),
            ]
        )

    grounded_long_str = ""
    grounded_extensions_list = list(grounded_extensions)
    if grounded_extensions_list:
        grounded_long_str = extension_dict.get(
            f"{{{', '.join(arg.name for arg in sorted(grounded_extensions_list[0]))}}}",
            "",
        )
    return semantics_div, grounded_long_str


# -- Callback for synchronizing the radio items across different groups --
@callback(
    [
        Output("extension-radioitems-grounded", "value"),
        Output("extension-radioitems-stable", "value"),
        Output("extension-radioitems-preferred", "value"),
        Output("extension-radioitems-other", "value"),
        Output("selected-argument-store-abstract", "data"),
        Output("store-extension-grounded", "data"),
        Output("store-extension-stable", "data"),
        Output("store-extension-preferred", "data"),
        Output("store-extension-other", "data"),
    ],
    [
        Input("extension-radioitems-grounded", "value"),
        Input("extension-radioitems-stable", "value"),
        Input("extension-radioitems-preferred", "value"),
        Input("extension-radioitems-other", "value"),
        Input("abstract-evaluation-accordion", "active_item"),
    ],
    [
        State("store-extension-grounded", "data"),
        State("store-extension-stable", "data"),
        State("store-extension-preferred", "data"),
        State("store-extension-other", "data"),
    ],
    prevent_initial_call=True,
)
def sync_radioitems(
    grounded_val,
    stable_val,
    preferred_val,
    other_val,
    active_item,
    stored_grounded,
    stored_stable,
    stored_preferred,
    stored_other,
):
    ctx = callback_context
    if not ctx.triggered:
        raise exceptions.PreventUpdate

    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

    # **Reset everything when switching semantics**
    if triggered_id == "abstract-evaluation-semantics":
        return (None, None, None, None, None, None, None, None, None)

    # **Handle switching back from Explanation to Evaluation**
    if active_item == "ArgumentationFramework":
        return (None, None, None, None, None, None, None, None, None)

    # **Handle individual radio item selection updates**
    radioitems_mapping = {
        "extension-radioitems-grounded": (grounded_val, stored_grounded),
        "extension-radioitems-stable": (stable_val, stored_stable),
        "extension-radioitems-preferred": (preferred_val, stored_preferred),
        "extension-radioitems-other": (other_val, stored_other),
    }

    if any([grounded_val, stable_val, preferred_val, other_val]):
        if triggered_id in radioitems_mapping:
            current_val, stored_val = radioitems_mapping[triggered_id]
            new_value = current_val if current_val is not None else stored_val

            if new_value is None:
                raise exceptions.PreventUpdate

            # Parse the selected arguments
            parts = new_value.split("|") if "|" in new_value else ("", "", "")
            selected_arguments = {
                "green": parts[0].split("+") if parts[0] else [],
                "yellow": parts[1].split("+") if parts[1] else [],
                "red": parts[2].split("+") if parts[2] else [],
            }

            return (
                new_value if triggered_id == "extension-radioitems-grounded" else None,
                new_value if triggered_id == "extension-radioitems-stable" else None,
                new_value if triggered_id == "extension-radioitems-preferred" else None,
                new_value if triggered_id == "extension-radioitems-other" else None,
                selected_arguments,
                new_value if triggered_id == "extension-radioitems-grounded" else None,
                new_value if triggered_id == "extension-radioitems-stable" else None,
                new_value if triggered_id == "extension-radioitems-preferred" else None,
                new_value if triggered_id == "extension-radioitems-other" else None,
            )

        # **If no valid trigger is found, prevent update**
        raise exceptions.PreventUpdate
    else:
        if (
            stored_grounded is None
            and stored_stable is None
            and stored_preferred is None
            and stored_other is None
        ):
            raise exceptions.PreventUpdate
        # if the selection is empty, we need to restore the last selected value
        non_none_values = {
            "grounded": stored_grounded,
            "stable": stored_stable,
            "preferred": stored_preferred,
            "other": stored_other,
        }

        # Keep only non-None values
        non_none_values = {k: v for k, v in non_none_values.items() if v is not None}

        # Determine which value to use (pick the first available one)
        selected_key = next(iter(non_none_values), None)
        selected_value = non_none_values[selected_key] if selected_key else None

        # Map the selected key to the correct output position
        output_values = {
            "grounded": (selected_value, None, None, None),
            "stable": (None, selected_value, None, None),
            "preferred": (None, None, selected_value, None),
            "other": (None, None, None, selected_value),
        }.get(selected_key, (None, None, None, None))

        # Extract selected arguments
        parts = selected_value.split("|") if "|" in selected_value else ("", "", "")
        selected_arguments = {
            "green": parts[0].split("+") if parts[0] else [],
            "yellow": parts[1].split("+") if parts[1] else [],
            "red": parts[2].split("+") if parts[2] else [],
        }

        # Return values matching the Output order
        return (
            *output_values,  # Assigns value to the correct radio item, others remain None
            selected_arguments,  # Assign selected arguments
            *output_values,  # Store the selected value in the corresponding store
        )
