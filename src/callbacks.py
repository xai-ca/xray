# callbacks.py

import base64
import json
from typing import List, Dict

import dash
from dash import html, callback, Input, Output, State, ALL, dcc, ctx
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import dash_interactive_graphviz
import os
import subprocess
import time
import shutil

# Check where 'dot' is located
dot_path = shutil.which("dot")

if dot_path is None:
    raise FileNotFoundError(
        "Graphviz 'dot' command not found. Ensure Graphviz is installed."
    )


# -- Your PyArg imports --
from py_arg.abstract_argumentation.classes.abstract_argumentation_framework import (
    AbstractArgumentationFramework,
)
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
from py_arg_visualisation.functions.explanations_functions.explanation_function_options import (
    EXPLANATION_FUNCTION_OPTIONS,
)
from py_arg_visualisation.functions.explanations_functions.get_af_explanations import (
    get_argumentation_framework_explanations,
)
from py_arg.abstract_argumentation.semantics.get_accepted_arguments import (
    get_accepted_arguments,
)
from py_arg.abstract_argumentation.semantics.get_argumentation_framework_extensions import (
    get_argumentation_framework_extensions,
)
from py_arg_visualisation.functions.extensions_functions.get_acceptance_strategy import (
    get_acceptance_strategy,
)
from py_arg_visualisation.functions.graph_data_functions.get_af_dot_string import (
    generate_plain_dot_string,
    generate_dot_string,
)
from py_arg_visualisation.functions.graph_data_functions.get_af_graph_data import (
    get_argumentation_framework_graph_data,
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

# Define the examples folder path
EXAMPLES_FOLDER = "examples"


# Function to get file list
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


@callback(
    Output("layered-vis-param", "style"),
    Input("abstract-evaluation-accordion", "active_item"),
)
def show_hide_element(accordion_value):
    if accordion_value == "Evaluation":
        return {"display": "block"}
    else:
        return {"display": "none"}


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
    if not isinstance(selected_arguments, dict):
        selected_arguments = {}
    """
    Generate the argumentation framework visualization and handle file download.
    """

    # Ensure `selected_arguments_changed` is initialized properly
    if selected_arguments_changed is None:
        selected_arguments_changed = False

    # Set `dot_source` to None so we can update it properly
    dot_source = None

    # Read or initialize the argumentation framework
    try:
        arg_framework = read_argumentation_framework(arguments, attacks)
    except ValueError:
        arg_framework = AbstractArgumentationFramework()

    triggered_id = ctx.triggered_id  # Get which input triggered the callback

    # Only set `dot_source` to default if no valid user interaction is detected
    if not triggered_id or active_item == "ArgumentationFramework":
        dot_source = generate_plain_dot_string(arg_framework, dot_layout)
        selected_arguments_changed = False  # Reset state
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

        # Sleep to ensure files are written before returning
        time.sleep(0.1)

        download_dot_source = generate_dot_string(
            arg_framework,
            selected_arguments,
            True,
            dot_layout,
            dot_rank,
            special_handling,
            layout_freeze,
        )
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
                dict(content=settings + "\n" + download_dot_source, filename="output.gv"),
                dot_source,
                selected_arguments_changed,
            )

    return None, dot_source, selected_arguments_changed


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


@callback(
    Output("21-abstract-evaluation-semantics", "children"),
    Output("21-abstract-evaluation-accepted", "children"),
    State("abstract-arguments", "value"),
    State("abstract-attacks", "value"),
    Input("abstract-evaluation-accordion", "active_item"),
    Input("abstract-evaluation-semantics", "value"),
    Input("abstract-evaluation-strategy", "value"),
    prevent_initial_call=True,
)
def evaluate_abstract_argumentation_framework(
    arguments: str, attacks: str, active_item: str, semantics: str, strategy: str
):
    if active_item != "Evaluation":
        raise PreventUpdate

    arg_framework = read_argumentation_framework(arguments, attacks)
    frozen_extensions = get_argumentation_framework_extensions(arg_framework, semantics)
    extensions = [set(frozen_ext) for frozen_ext in frozen_extensions]

    # Build extension buttons
    extension_buttons = []
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

        extension_buttons.append(
            dbc.Button(
                [extension_readable_str],
                color="secondary",
                id={"type": "extension-button-abstract", "index": extension_long_str},
            )
        )

    # Compute accepted arguments
    acceptance_strategy = get_acceptance_strategy(strategy)
    accepted_arguments = get_accepted_arguments(frozen_extensions, acceptance_strategy)

    # Build accepted argument buttons
    accepted_argument_buttons = [
        dbc.Button(
            arg.name,
            color="secondary",
            id={"type": "argument-button-abstract", "index": arg.name},
        )
        for arg in sorted(accepted_arguments)
    ]

    semantics_div = html.Div(
        [
            html.B("The extension(s):"),
            html.Br(),
            html.I("Click on an extension to display it in the graph."),
            html.Div(extension_buttons),
            html.Br(),
        ]
    )
    accepted_div = html.Div(
        [
            html.B("The accepted argument(s):"),
            html.Br(),
            html.I("Click on an argument to display it in the graph."),
            html.Div(accepted_argument_buttons),
        ]
    )

    return semantics_div, accepted_div


@callback(
    Output("selected-argument-store-abstract", "data"),
    Input({"type": "extension-button-abstract", "index": ALL}, "n_clicks"),
    Input({"type": "argument-button-abstract", "index": ALL}, "n_clicks"),
    Input("abstract-arguments", "value"),
    Input("abstract-attacks", "value"),
)
def mark_extension_or_argument_in_graph(
    _nr_of_clicks_extension_values, _nr_of_clicks_argument_values, _arguments, _attacks
):
    # Clear selection if arguments/attacks change
    if dash.ctx.triggered_id in ["abstract-arguments", "abstract-attacks"]:
        return []

    button_clicked_id = dash.callback_context.triggered[0]["prop_id"].split(".")[0]
    if not button_clicked_id:
        return []

    button_clicked_id_content = json.loads(button_clicked_id)
    button_type = button_clicked_id_content["type"]
    button_index = button_clicked_id_content["index"]

    if button_type == "extension-button-abstract":
        in_part, undecided_part, out_part = button_index.split("|", 3)
        return {
            "green": in_part.split("+") if in_part else [],
            "yellow": undecided_part.split("+") if undecided_part else [],
            "red": out_part.split("+") if out_part else [],
        }
    elif button_type == "argument-button-abstract":
        return {"blue": [button_index]}

    return []


@callback(
    Output("abstract-explanation-function", "options"),
    Output("abstract-explanation-function", "value"),
    [Input("abstract-explanation-type", "value")],
)
def setting_choice(choice: str):
    return EXPLANATION_FUNCTION_OPTIONS[choice], EXPLANATION_FUNCTION_OPTIONS[choice][
        0
    ]["value"]


@callback(
    Output("abstract-explanation", "children"),
    Input("abstract-evaluation-accordion", "active_item"),
    State("abstract-arguments", "value"),
    State("abstract-attacks", "value"),
    State("abstract-evaluation-semantics", "value"),
    Input("abstract-explanation-function", "value"),
    Input("abstract-explanation-type", "value"),
    State("abstract-evaluation-strategy", "value"),
    prevent_initial_call=True,
)
def derive_explanations_abstract_argumentation_framework(
    active_item,
    arguments: str,
    attacks: str,
    semantics: str,
    explanation_function: str,
    explanation_type: str,
    explanation_strategy: str,
):
    if active_item != "Explanation":
        raise PreventUpdate

    arg_framework = read_argumentation_framework(arguments, attacks)
    frozen_extensions = get_argumentation_framework_extensions(arg_framework, semantics)
    extensions = [set(frozen_extension) for frozen_extension in frozen_extensions]
    acceptance_strategy = get_acceptance_strategy(explanation_strategy)
    accepted_arguments = get_accepted_arguments(frozen_extensions, acceptance_strategy)

    explanations = get_argumentation_framework_explanations(
        arg_framework,
        extensions,
        accepted_arguments,
        explanation_function,
        explanation_type,
    )

    # Display the explanations
    return html.Div(
        [html.Div(html.B("Explanation(s) by argument:"))]
        + [
            html.Div(
                [
                    html.B(arg_name),
                    html.Ul(
                        [
                            html.Li(str(expl).replace("set()", "{}"))
                            for expl in explanation_list
                        ]
                    ),
                ]
            )
            for arg_name, explanation_list in explanations.items()
        ]
    )
