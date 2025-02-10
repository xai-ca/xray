# callbacks.py

import base64
import json
from typing import List, Dict

import dash
from dash import (
    html,
    callback,
    Input,
    Output,
    State,
    ctx,
    callback_context,
    exceptions,
)
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import os
import subprocess
import shutil

# Check where 'dot' is located
dot_path = shutil.which("dot")

if dot_path is None:
    raise FileNotFoundError(
        "Graphviz 'dot' command not found. Ensure Graphviz is installed."
    )


# -- Your PyArg imports --
from py_arg.abstract_argumentation.generators.abstract_argumentation_framework_generator import (
    AbstractArgumentationFrameworkGenerator,
)
from py_arg.abstract_argumentation.import_export.argumentation_framework_from_aspartix_format_reader import (
    ArgumentationFrameworkFromASPARTIXFormatReader,
)
from py_arg.abstract_argumentation.import_export.argumentation_framework_from_iccma23_format_reader import (
    ArgumentationFrameworkFromICCMA23FormatReader,
)
from py_arg.abstract_argumentation.import_export.argumentation_framework_from_json_reader import (
    ArgumentationFrameworkFromJsonReader,
)
from py_arg.abstract_argumentation.import_export.argumentation_framework_from_trivial_graph_format_reader import (
    ArgumentationFrameworkFromTrivialGraphFormatReader,
)
from py_arg.abstract_argumentation.import_export.argumentation_framework_to_aspartix_format_writer import (
    ArgumentationFrameworkToASPARTIXFormatWriter,
)
from py_arg.abstract_argumentation.import_export.argumentation_framework_to_iccma23_format_writer import (
    ArgumentationFrameworkToICCMA23FormatWriter,
)
from py_arg.abstract_argumentation.import_export.argumentation_framework_to_json_writer import (
    ArgumentationFrameworkToJSONWriter,
)
from py_arg.abstract_argumentation.import_export.argumentation_framework_to_trivial_graph_format_writer import (
    ArgumentationFrameworkToTrivialGraphFormatWriter,
)
from py_arg.abstract_argumentation.semantics.get_argumentation_framework_extensions import (
    get_argumentation_framework_extensions,
)
from py_arg_visualisation.functions.graph_data_functions.get_af_dot_string import (
    generate_plain_dot_string,
    generate_dot_string,
    get_numbered_grounded_extension,
)
from py_arg_visualisation.functions.import_functions.read_argumentation_framework_functions import (
    read_argumentation_framework,
)

# ---------------------------
# Utility or internal functions
# ---------------------------

# (If you prefer, you could place 'read_argumentation_framework' logic here
#  instead of a separate file, but for clarity it's fine as is.)


# ---------------------------
# Callbacks
# ---------------------------
# Section0 :Accordion Item Setup
@callback(
    Output("layered-vis-param", "style"),
    Input("abstract-evaluation-accordion", "active_item"),
)
def show_hide_element(accordion_value):
    if accordion_value == "Evaluation":
        return {"display": "block"}
    else:
        return {"display": "none"}


# Section1 : Abstract Argumentation Framework
# 1.1 : Upload or generate an AF


@callback(
    Output("21-af-download", "data"),
    Input("21-af-download-button", "n_clicks"),
    State("abstract-arguments", "value"),
    State("abstract-attacks", "value"),
    State("21-af-filename", "value"),
    State("21-af-extension", "value"),
    prevent_initial_call=True,
)
def download_generated_abstract_argumentation_framework(
    _nr_clicks: int,
    arguments_text: str,
    defeats_text: str,
    filename: str,
    extension: str,
):
    argumentation_framework = read_argumentation_framework(arguments_text, defeats_text)

    if extension == "JSON":
        argumentation_framework_json = ArgumentationFrameworkToJSONWriter().to_dict(
            argumentation_framework
        )
        argumentation_framework_str = json.dumps(argumentation_framework_json)
    elif extension == "TGF":
        argumentation_framework_str = (
            ArgumentationFrameworkToTrivialGraphFormatWriter.write_to_str(
                argumentation_framework
            )
        )
    elif extension == "APX":
        argumentation_framework_str = (
            ArgumentationFrameworkToASPARTIXFormatWriter.write_to_str(
                argumentation_framework
            )
        )
    elif extension == "ICCMA23":
        argumentation_framework_str = (
            ArgumentationFrameworkToICCMA23FormatWriter.write_to_str(
                argumentation_framework
            )
        )
    else:
        raise NotImplementedError

    return {
        "content": argumentation_framework_str,
        "filename": f"{filename}.{extension}",
    }


## 1.2 : Choose from Examples
EXAMPLES_FOLDER = "examples"


def get_example_files():
    if os.path.exists(EXAMPLES_FOLDER):
        return [
            {"label": f[:-5], "value": f}  # Remove '.json' from label
            for f in os.listdir(EXAMPLES_FOLDER)
            if os.path.isfile(os.path.join(EXAMPLES_FOLDER, f))
            and f.lower().endswith(".json")
        ]
    return []


@callback(
    Output("examples-dropdown", "options"),
    Input("examples-dropdown", "id"),  # Triggers once on page load
    prevent_initial_call=False,
)
def update_examples_dropdown(_):
    return get_example_files()


# 1.3 : Text Field Interaction
@callback(
    Output("abstract-arguments", "value"),
    Output("abstract-attacks", "value"),
    Input("generate-random-af-button", "n_clicks"),
    Input("upload-af", "contents"),
    Input("examples-dropdown", "value"),  # New: User-selected example
    State("upload-af", "filename"),
)
def load_argumentation_framework(
    _nr_of_clicks_random: int, af_content: str, selected_example: str, af_filename: str
):
    """
    Generate a random AF after clicking the button or upload an existing AF.
    """
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate

    if ctx.triggered_id == "generate-random-af-button":
        random_af = AbstractArgumentationFrameworkGenerator(8, 8, True).generate()
        abstract_arguments_value = "\n".join(str(arg) for arg in random_af.arguments)
        abstract_attacks_value = "\n".join(
            f"({str(defeat.from_argument)},{str(defeat.to_argument)})"
            for defeat in random_af.defeats
        )
        return abstract_arguments_value, abstract_attacks_value

    elif ctx.triggered_id == "upload-af":
        # Reading from uploaded file
        content_type, content_str = af_content.split(",")
        decoded = base64.b64decode(content_str)
        name = af_filename.split(".")[0]

        if af_filename.upper().endswith(".JSON"):
            opened_af = ArgumentationFrameworkFromJsonReader().from_json(
                json.loads(decoded)
            )
        elif af_filename.upper().endswith(".TGF"):
            opened_af = ArgumentationFrameworkFromTrivialGraphFormatReader.from_tgf(
                decoded.decode(), name
            )
        elif af_filename.upper().endswith(".APX"):
            opened_af = ArgumentationFrameworkFromASPARTIXFormatReader.from_apx(
                decoded.decode(), name
            )
        elif af_filename.upper().endswith(".ICCMA23"):
            opened_af = ArgumentationFrameworkFromICCMA23FormatReader.from_iccma23(
                decoded.decode(), name
            )
        else:
            raise NotImplementedError("Unsupported file format.")

        abstract_arguments_value = "\n".join(str(arg) for arg in opened_af.arguments)
        abstract_attacks_value = "\n".join(
            f"({str(defeat.from_argument)},{str(defeat.to_argument)})"
            for defeat in opened_af.defeats
        )
        return abstract_arguments_value, abstract_attacks_value
    elif ctx.triggered_id == "examples-dropdown" and selected_example:
        # Reading from selected example file
        example_path = os.path.join(EXAMPLES_FOLDER, selected_example)  # Add .json back

        try:
            with open(example_path, "r", encoding="utf-8") as file:
                file_content = file.read()

            opened_af = ArgumentationFrameworkFromJsonReader().from_json(
                json.loads(file_content)
            )

            abstract_arguments_value = "\n".join(
                str(arg) for arg in opened_af.arguments
            )
            abstract_attacks_value = "\n".join(
                f"({str(defeat.from_argument)},{str(defeat.to_argument)})"
                for defeat in opened_af.defeats
            )
            return abstract_arguments_value, abstract_attacks_value

        except Exception as e:
            print(f"Error reading example file {selected_example}: {e}")
            return "", ""

    return "", ""


# Section 2: Solutions
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
    arguments: str, attacks: str, active_item: str, semantics: str
):
    if active_item != "Evaluation":
        raise PreventUpdate

    arg_framework = read_argumentation_framework(arguments, attacks)
    frozen_extensions = get_argumentation_framework_extensions(
        arg_framework, "Complete"
    )
    extensions = [set(frozen_ext) for frozen_ext in frozen_extensions]

    # Store all the extensions and three status
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

    # Grounded extensions radio items
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
        id="extension-radioitems-grounded",  # <-- Unique ID
        inline=True,
    )

    # Stable extensions radio items
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
        id="extension-radioitems-stable",  # <-- Unique ID
        inline=True,
    )

    # Preferred (non-stable) extensions radio items
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
        id="extension-radioitems-preferred",  # <-- Unique ID
        inline=True,
    )

    # Other complete extensions radio items
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
        id="extension-radioitems-other",  # <-- Unique ID
        inline=True,
    )
    semantics_div = html.Div(children=[])

    if semantics == "Grounded":
        semantics_div.children.append(html.Br())
        semantics_div.children.append(html.B("Grounded Extension:"))
        semantics_div.children.append(
            html.Div(
                grounded_extension_radioitems,
                style={
                    "border": "2px dotted lightblue",
                    "border-radius": "10px",
                    "padding": "10px",
                },
            )
        )
        semantics_div.children.append(html.Br())
        semantics_div.children.append(
            html.Div(
                [
                    dbc.RadioItems(id="extension-radioitems-stable"),
                    dbc.RadioItems(id="extension-radioitems-preferred"),
                    dbc.RadioItems(id="extension-radioitems-other"),
                ],
            )
        )
    elif semantics == "Stable":
        semantics_div.children.append(html.Br())
        semantics_div.children.append(html.B("Stable Extensions:"))
        semantics_div.children.append(
            html.Div(
                stable_extension_radioitems,
                style={
                    "border": "2px dotted lightblue",
                    "border-radius": "10px",
                    "padding": "10px",
                },
            )
        )
        semantics_div.children.append(html.Br())
        semantics_div.children.append(
            html.Div(
                [
                    dbc.RadioItems(id="extension-radioitems-grounded"),
                    dbc.RadioItems(id="extension-radioitems-preferred"),
                    dbc.RadioItems(id="extension-radioitems-other"),
                ],
            )
        )
    elif semantics == "Preferred":
        semantics_div.children.append(html.Br())
        semantics_div.children.append(html.B("Stable Extensions:"))
        semantics_div.children.append(
            html.Div(
                stable_extension_radioitems,
                style={
                    "border": "2px dotted lightblue",
                    "border-radius": "10px",
                    "padding": "10px",
                },
            )
        )
        semantics_div.children.append(html.Br())
        semantics_div.children.append(html.B("Preferred Non-Stable Extensions:"))
        semantics_div.children.append(
            html.Div(
                preferred_non_stable_extension_radioitems,
                style={
                    "border": "2px dotted lightblue",
                    "border-radius": "10px",
                    "padding": "10px",
                },
            )
        )
        semantics_div.children.append(html.Br())
        semantics_div.children.append(
            html.Div(
                [
                    dbc.RadioItems(id="extension-radioitems-grounded"),
                    dbc.RadioItems(id="extension-radioitems-other"),
                ],
            )
        )
    elif semantics == "Complete":
        semantics_div.children.append(html.Br())
        semantics_div.children.append(html.B("Grounded Extension:"))
        semantics_div.children.append(
            html.Div(
                grounded_extension_radioitems,
                style={
                    "border": "2px dotted lightblue",
                    "border-radius": "10px",
                    "padding": "10px",
                },
            )
        )
        semantics_div.children.append(html.Br())
        semantics_div.children.append(html.B("Stable Extensions:"))
        semantics_div.children.append(
            html.Div(
                stable_extension_radioitems,
                style={
                    "border": "2px dotted lightblue",
                    "border-radius": "10px",
                    "padding": "10px",
                },
            )
        )
        semantics_div.children.append(html.Br())
        semantics_div.children.append(html.B("Preferred Non-Stable Extensions:"))
        semantics_div.children.append(
            html.Div(
                preferred_non_stable_extension_radioitems,
                style={
                    "border": "2px dotted lightblue",
                    "border-radius": "10px",
                    "padding": "10px",
                },
            )
        )
        semantics_div.children.append(html.Br())
        semantics_div.children.append(html.B("Other Complete Extensions:"))
        semantics_div.children.append(
            html.Div(
                other_complete_extension_radioitems,
                style={
                    "border": "2px dotted lightblue",
                    "border-radius": "10px",
                    "padding": "10px",
                },
            )
        )

    grounded_long_str = ""
    grounded_extensions_list = list(grounded_extensions)
    if grounded_extensions_list:
        grounded_long_str = extension_dict.get(
            f"{{{', '.join(arg.name for arg in sorted(grounded_extensions_list[0]))}}}",
            "",
        )
    return semantics_div, grounded_long_str


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
def sync_radioitems(
    grounded_val, stable_val, preferred_val, other_val, grounded_long_str
):
    ctx = callback_context

    # If no input triggered the callback, do nothing.
    if not ctx.triggered:
        raise exceptions.PreventUpdate

    # Identify which radio group triggered the callback.
    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

    # Capture the new value from the triggering group.
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
        # in_part, undecided_part, out_part = grounded_long_str.split("|", 3)
        # selected_arguments = {
        #         "green": in_part.split("+") if in_part else [],
        #         "yellow": undecided_part.split("+") if undecided_part else [],
        #         "red": out_part.split("+") if out_part else [],
        #     }
        selected_arguments = {}

    return (
        new_value if triggered_id == "extension-radioitems-grounded" else None,
        new_value if triggered_id == "extension-radioitems-stable" else None,
        new_value if triggered_id == "extension-radioitems-preferred" else None,
        new_value if triggered_id == "extension-radioitems-other" else None,
        selected_arguments,
    )


# Section 3: Explanations
@callback(
    Output("21-abstract-evaluation-all-args", "children"),
    State("abstract-arguments", "value"),
    State("abstract-attacks", "value"),
    Input("abstract-evaluation-accordion", "active_item"),
    Input("abstract-evaluation-semantics", "value"),
    prevent_initial_call=True,
)
def evaluate_abstract_argumentation_framework(
    arguments: str, attacks: str, active_item: str, semantics: str
):
    if active_item != "Evaluation":
        raise PreventUpdate

    arg_framework = read_argumentation_framework(arguments, attacks)

    # Compute accepted arguments
    gr_status_by_arg, number_by_argument = get_numbered_grounded_extension(
        arg_framework
    )

    # Build accepted argument buttons
    all_argument_buttons = [
        dbc.Button(
            arg,
            outline=True,
            color=(
                "danger"
                if gr_status_by_arg[arg] == "defeated"
                else "primary"
                if gr_status_by_arg[arg] == "accepted"
                else "warning"
            ),
            id={"type": "argument-button-abstract", "index": arg},
            style={"margin": "5px"},  # Add margin to make buttons sparse
        )
        for arg in sorted(arguments.split("\n"))
    ]

    arguments_div = html.Div(
        [
            html.B("Argument Provenance:"),
            html.Br(),
            html.I("Click on an argument to display it in the graph."),
            html.Div(all_argument_buttons),
        ]
    )
    return arguments_div


# Viz Section : Visualization
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
    State("selected_arguments_changed", "data"),
    prevent_initial_call=True,
)
def create_abstract_argumentation_framework(
    _nr_clicks: int,
    arguments: str,
    attacks: str,
    selected_arguments: Dict[str, List[str]],
    dot_layout: str,
    dot_rank: str,
    special_handling: List[str],
    active_item: str,
    layout_freeze: bool,
    selected_arguments_changed,
):
    if not arguments or not attacks:
        raise PreventUpdate
    else:
        if selected_arguments == {}:
            selected_arguments = None
        else:
            pass

        if not isinstance(selected_arguments, dict):
            selected_arguments = {}

        # Ensure `selected_arguments_changed` is initialized properly
        if selected_arguments_changed is None:
            selected_arguments_changed = False

        # Set `dot_source` to None so we can update it properly
        dot_source = None
        arg_framework = read_argumentation_framework(arguments, attacks)
        triggered_id = ctx.triggered_id  # Get which input triggered the callback

        # Only set `dot_source` to default if no valid user interaction is detected
        if not triggered_id or active_item == "ArgumentationFramework":
            dot_source = generate_plain_dot_string(arg_framework, dot_layout)
            selected_arguments_changed = False  # Reset state
        else:
            if triggered_id == "abstract-evaluation-accordion":
                dot_source = generate_plain_dot_string(arg_framework, dot_layout) # only switch accordion will trigger
            if triggered_id == "selected-argument-store-abstract" and selected_arguments == {}:
                dot_source = generate_plain_dot_string(arg_framework, dot_layout) # only switch accordion will trigger
            else:

                # Correctly detect when `selected-argument-store-abstract` is triggered
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
                    selected_arguments_changed = True  # Set flag so it doesn't re-trigger
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
                    with open("temp/layout.dot", "w") as dot_file:
                        dot_file.write(dot_source)
                    subprocess.run(
                        ["dot", "-Tplain", "temp/layout.dot", "-o", "temp/layout.txt"],
                        check=True,
                    )
                # download_dot_source = generate_dot_string(
                #     arg_framework,
                #     selected_arguments,
                #     True,
                #     dot_layout,
                #     dot_rank,
                #     special_handling,
                #     layout_freeze,
                # )
                # Define graph settings for output
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

            # Ensure function always returns three outputs
            if triggered_id == "21-dot-download-button":
                return (
                    dict(
                        content=settings + "\n" + dot_source,
                        filename="output.gv",
                    ),
                    dot_source,
                    selected_arguments_changed,
                )

        return None, dot_source, selected_arguments_changed
