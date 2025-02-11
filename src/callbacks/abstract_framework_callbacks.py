# callbacks/abstract_framework_callbacks.py

import base64
import json
import os
import shutil
from dash import callback, Input, Output, State, callback_context
from dash.exceptions import PreventUpdate

# Import PyArg functions and readers/writers
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

# Utility import for reading the AF from text fields
from py_arg_visualisation.functions.import_functions.read_argumentation_framework_functions import (
    read_argumentation_framework,
)

# Check for Graphviz dot path (if needed in this module)
dot_path = shutil.which("dot")
if dot_path is None:
    raise FileNotFoundError(
        "Graphviz 'dot' command not found. Ensure Graphviz is installed."
    )


# -- Example Callback: Show/hide visualization panel based on accordion state --
@callback(
    Output("layered-vis-param", "style"),
    Input("abstract-evaluation-accordion", "active_item"),
)
def show_hide_element(accordion_value):
    if accordion_value == "Evaluation":
        return {"display": "block"}
    else:
        return {"display": "none"}


# -- Callback for downloading a generated abstract argumentation framework --
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
    _nr_clicks, arguments_text, defeats_text, filename, extension
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


# -- Callback for choosing examples --
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


# -- Callback for handling text field interaction (upload or generate random AF) --
@callback(
    Output("abstract-arguments", "value"),
    Output("abstract-attacks", "value"),
    Input("generate-random-af-button", "n_clicks"),
    Input("upload-af", "contents"),
    Input("examples-dropdown", "value"),
    State("upload-af", "filename"),
)
def load_argumentation_framework(
    _nr_clicks_random, af_content, selected_example, af_filename
):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate

    if ctx.triggered_id == "generate-random-af-button":
        from py_arg.abstract_argumentation.generators.abstract_argumentation_framework_generator import AbstractArgumentationFrameworkGenerator
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
        example_path = os.path.join(EXAMPLES_FOLDER, selected_example)
        try:
            with open(example_path, "r", encoding="utf-8") as file:
                file_content = file.read()
            opened_af = ArgumentationFrameworkFromJsonReader().from_json(
                json.loads(file_content)
            )
            abstract_arguments_value = "\n".join(str(arg) for arg in opened_af.arguments)
            abstract_attacks_value = "\n".join(
                f"({str(defeat.from_argument)},{str(defeat.to_argument)})"
                for defeat in opened_af.defeats
            )
            return abstract_arguments_value, abstract_attacks_value
        except Exception as e:
            print(f"Error reading example file {selected_example}: {e}")
            return "", ""

    return "", ""
