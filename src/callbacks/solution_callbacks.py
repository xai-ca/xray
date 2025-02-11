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
def evaluate_abstract_argumentation_framework(arguments, attacks, active_item, semantics):
    if active_item != "Evaluation":
        raise PreventUpdate

    arg_framework = read_argumentation_framework(arguments, attacks)
    frozen_extensions = get_argumentation_framework_extensions(arg_framework, "Complete")
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

    grounded_extensions = get_argumentation_framework_extensions(arg_framework, "Grounded")
    stable_extensions = get_argumentation_framework_extensions(arg_framework, "Stable")
    preferred_extensions = get_argumentation_framework_extensions(arg_framework, "Preferred")
    complete_extensions = get_argumentation_framework_extensions(arg_framework, "Complete")

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
        semantics_div.children.extend([
            html.Br(),
            html.B("Grounded Extension:"),
            html.Div(
                grounded_extension_radioitems,
                style={"border": "2px dotted lightblue", "border-radius": "10px", "padding": "10px"},
            ),
            html.Br(),
            html.Div([
                dbc.RadioItems(id="extension-radioitems-stable"),
                dbc.RadioItems(id="extension-radioitems-preferred"),
                dbc.RadioItems(id="extension-radioitems-other"),
            ]),
        ])
    elif semantics == "Stable":
        semantics_div.children.extend([
            html.Br(),
            html.B("Stable Extensions:"),
            html.Div(
                stable_extension_radioitems,
                style={"border": "2px dotted lightblue", "border-radius": "10px", "padding": "10px"},
            ),
            html.Br(),
            html.Div([
                dbc.RadioItems(id="extension-radioitems-grounded"),
                dbc.RadioItems(id="extension-radioitems-preferred"),
                dbc.RadioItems(id="extension-radioitems-other"),
            ]),
        ])
    elif semantics == "Preferred":
        semantics_div.children.extend([
            html.Br(),
            html.B("Stable Extensions:"),
            html.Div(
                stable_extension_radioitems,
                style={"border": "2px dotted lightblue", "border-radius": "10px", "padding": "10px"},
            ),
            html.Br(),
            html.B("Preferred Non-Stable Extensions:"),
            html.Div(
                preferred_non_stable_extension_radioitems,
                style={"border": "2px dotted lightblue", "border-radius": "10px", "padding": "10px"},
            ),
            html.Br(),
            html.Div([
                dbc.RadioItems(id="extension-radioitems-grounded"),
                dbc.RadioItems(id="extension-radioitems-other"),
            ]),
        ])
    elif semantics == "Complete":
        semantics_div.children.extend([
            html.Br(),
            html.B("Grounded Extension:"),
            html.Div(
                grounded_extension_radioitems,
                style={"border": "2px dotted lightblue", "border-radius": "10px", "padding": "10px"},
            ),
            html.Br(),
            html.B("Stable Extensions:"),
            html.Div(
                stable_extension_radioitems,
                style={"border": "2px dotted lightblue", "border-radius": "10px", "padding": "10px"},
            ),
            html.Br(),
            html.B("Preferred Non-Stable Extensions:"),
            html.Div(
                preferred_non_stable_extension_radioitems,
                style={"border": "2px dotted lightblue", "border-radius": "10px", "padding": "10px"},
            ),
            html.Br(),
            html.B("Other Complete Extensions:"),
            html.Div(
                other_complete_extension_radioitems,
                style={"border": "2px dotted lightblue", "border-radius": "10px", "padding": "10px"},
            ),
        ])

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
    ],
    [
        Input("extension-radioitems-grounded", "value"),
        Input("extension-radioitems-stable", "value"),
        Input("extension-radioitems-preferred", "value"),
        Input("extension-radioitems-other", "value"),
        Input("grounded-extension-long-str-store", "data"),
    ],
)
def sync_radioitems(grounded_val, stable_val, preferred_val, other_val, grounded_long_str):
    ctx = callback_context
    if not ctx.triggered:
        raise exceptions.PreventUpdate

    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
    new_value = None

    if triggered_id == "extension-radioitems-grounded":
        new_value = grounded_val
    elif triggered_id == "extension-radioitems-stable":
        new_value = stable_val
    elif triggered_id == "extension-radioitems-preferred":
        new_value = preferred_val
    elif triggered_id == "extension-radioitems-other":
        new_value = other_val

    if new_value is not None:
        in_part, undecided_part, out_part = new_value.split("|", 3)
        selected_arguments = {
            "green": in_part.split("+") if in_part else [],
            "yellow": undecided_part.split("+") if undecided_part else [],
            "red": out_part.split("+") if out_part else [],
        }
    else:
        selected_arguments = {}

    return (
        new_value if triggered_id == "extension-radioitems-grounded" else None,
        new_value if triggered_id == "extension-radioitems-stable" else None,
        new_value if triggered_id == "extension-radioitems-preferred" else None,
        new_value if triggered_id == "extension-radioitems-other" else None,
        selected_arguments,
    )
