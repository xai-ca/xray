# callbacks/abstract_framework_callbacks.py

import base64
import json
import os
import shutil
from dash import callback, Input, Output, State, callback_context, no_update
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
# @callback(
#     Output("layered-vis-param", "style"),
#     Input("abstract-evaluation-accordion", "active_item"),
# )
# def show_hide_element(accordion_value):
#     if accordion_value == "Evaluation":
#         return {"display": "block"}
#     else:
#         return {"display": "block"}


# -- Callback for downloading a generated abstract argumentation framework --

@callback(
    Output("21-af-download", "data"),
    Input("21-af-download-button", "n_clicks"),
    Input("examples-dropdown", "value"),
    State("abstract-arguments", "value"),
    State("abstract-attacks", "value"),
    State("21-af-filename", "value"),
    State("21-af-extension", "value"),
    State("raw-json", "data"),
    prevent_initial_call=True,
)
def download_generated_abstract_argumentation_framework(
    n_clicks, example_name, arguments_text, defeats_text, filename, extension, raw_json
):
    ctx = callback_context  # Get the callback context
    triggered_inputs = {t["prop_id"].split(".")[0] for t in ctx.triggered}
    
    # Ensure that both button and dropdown were triggered together
    if "21-af-download-button" not in triggered_inputs:
        return no_update  # Do nothing if only one is triggered

    # Only use example_name as filename if no custom filename is provided
    if not filename:
        if example_name:
            filename = example_name.split(".")[0]  # Remove the file extension
        else:
            filename = "edited_af"

    if extension == "json":
        # Prefer preserving annotations from raw_json (if available) while
        # reflecting current edits from the text fields.
        def _parse_argument_ids(text: str):
            seen = set()
            ordered_ids = []
            for line in (text or "").splitlines():
                arg_id = line.strip()
                if not arg_id:
                    continue
                if arg_id not in seen:
                    seen.add(arg_id)
                    ordered_ids.append(arg_id)
            return ordered_ids

        def _parse_defeats(text: str):
            pairs = []
            seen_pairs = set()
            for line in (text or "").splitlines():
                s = line.strip()
                if not s:
                    continue
                # Accept formats like (a,b) or a,b
                if s.startswith("(") and s.endswith(")"):
                    s = s[1:-1]
                if "," in s:
                    left, right = s.split(",", 1)
                    frm = left.strip()
                    to = right.strip()
                    key = (frm, to)
                    if frm and to and key not in seen_pairs:
                        seen_pairs.add(key)
                        pairs.append(key)
            return pairs

        if raw_json:
            try:
                source = raw_json
                source_args = {a.get("id"): a for a in source.get("arguments", [])}
                source_defs = {(d.get("from"), d.get("to")): d for d in source.get("defeats", [])}

                new_arg_ids = _parse_argument_ids(arguments_text)
                new_def_pairs = _parse_defeats(defeats_text)

                merged_arguments = []
                for arg_id in new_arg_ids:
                    existing = source_args.get(arg_id)
                    if existing:
                        # keep all known fields (incl. annotation/url)
                        merged_arguments.append({**existing, "id": arg_id})
                    else:
                        merged_arguments.append({"id": arg_id, "annotation": "", "url": ""})

                merged_defeats = []
                for frm, to in new_def_pairs:
                    existing = source_defs.get((frm, to))
                    if existing:
                        merged_defeats.append({**existing, "from": frm, "to": to})
                    else:
                        merged_defeats.append({"from": frm, "to": to, "annotation": ""})

                name = source.get("name") or (filename or "edited_af")
                argumentation_framework_json = {
                    "name": name,
                    "arguments": merged_arguments,
                    "defeats": merged_defeats,
                }
                argumentation_framework_str = json.dumps(argumentation_framework_json)
            except Exception:
                # Fallback to constructing from text fields only if merging fails
                argumentation_framework = read_argumentation_framework(arguments_text, defeats_text)
                argumentation_framework_json = ArgumentationFrameworkToJSONWriter().to_dict(
                    argumentation_framework
                )
                argumentation_framework_str = json.dumps(argumentation_framework_json)
        else:
            # No raw_json available: construct from text fields only
            argumentation_framework = read_argumentation_framework(arguments_text, defeats_text)
            argumentation_framework_json = ArgumentationFrameworkToJSONWriter().to_dict(
                argumentation_framework
            )
            argumentation_framework_str = json.dumps(argumentation_framework_json)
    elif extension == "TGF":
        argumentation_framework = read_argumentation_framework(arguments_text, defeats_text)
        argumentation_framework_str = (
            ArgumentationFrameworkToTrivialGraphFormatWriter.write_to_str(
                argumentation_framework
            )
        )
    elif extension == "APX":
        argumentation_framework = read_argumentation_framework(arguments_text, defeats_text)
        argumentation_framework_str = (
            ArgumentationFrameworkToASPARTIXFormatWriter.write_to_str(
                argumentation_framework
            )
        )
    elif extension == "ICCMA23":
        argumentation_framework = read_argumentation_framework(arguments_text, defeats_text)
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
        files = [
            {"label": f[:-5], "value": f}  # Remove '.json' from label
            for f in os.listdir(EXAMPLES_FOLDER)
            if os.path.isfile(os.path.join(EXAMPLES_FOLDER, f))
            and f.lower().endswith(".json")
        ]
        # Sort the files alphabetically by their value (filename)
        return sorted(files, key=lambda x: x["value"])
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
    Output("examples-dropdown", "value"),  # Added extra output to clear the selection when needed
    Output("21-af-filename", "value"),
    Output("raw-json", "data"),
    Input("generate-random-af-button", "n_clicks"),
    Input("upload-af", "contents"),
    Input("examples-dropdown", "value"),
    State("upload-af", "filename"),
    
)
def load_argumentation_framework(_nr_clicks_random, af_content, selected_example, af_filename):
    ctx = callback_context
    # print(ctx.triggered_id)
    if not ctx.triggered:
        raise PreventUpdate

    if ctx.triggered_id == "generate-random-af-button":
        # When clicking the generate button, generate a random AF.
        from py_arg.abstract_argumentation.generators.abstract_argumentation_framework_generator import AbstractArgumentationFrameworkGenerator
        random_af = AbstractArgumentationFrameworkGenerator(8, 8, True).generate()
        abstract_arguments_value = "\n".join(str(arg) for arg in random_af.arguments)
        abstract_attacks_value = "\n".join(
            f"({str(defeat.from_argument)},{str(defeat.to_argument)})"
            for defeat in random_af.defeats
        )
        # Convert the generated AF to JSON format for raw JSON output.
        raw_json = ArgumentationFrameworkToJSONWriter().to_dict(random_af)
        # Clear the examples dropdown selection.
        return abstract_arguments_value, abstract_attacks_value, None, "edited_af", raw_json

    elif ctx.triggered_id == "upload-af":
        # Reading from an uploaded file.
        content_type, content_str = af_content.split(",")
        decoded = base64.b64decode(content_str)
        name = af_filename.split(".")[0]

        if af_filename.upper().endswith(".JSON"):
            # Decode bytes to a string before loading JSON.
            opened_af = ArgumentationFrameworkFromJsonReader().from_json(
                json.loads(decoded.decode())
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
        file_name = af_filename.split(".")[0]  # Remove the file extension
        if af_filename.upper().endswith(".JSON"):
            raw_json = json.loads(decoded.decode())
        else:
            # Populate raw_json from the parsed AF for non-JSON uploads
            raw_json = ArgumentationFrameworkToJSONWriter().to_dict(opened_af)
        # Clear the examples dropdown when opening a file.
        return abstract_arguments_value, abstract_attacks_value, None, file_name, raw_json
    
    elif ctx.triggered_id == "examples-dropdown" and selected_example:
        # Reading from an example file.
        example_path = os.path.join(EXAMPLES_FOLDER, selected_example)
        try:
            with open(example_path, "r", encoding="utf-8") as file:
                file_content = file.read()
            raw_json = json.loads(file_content)
            opened_af = ArgumentationFrameworkFromJsonReader().from_json(json.loads(file_content))
            abstract_arguments_value = "\n".join(str(arg) for arg in opened_af.arguments)
            abstract_attacks_value = "\n".join(
                f"({str(defeat.from_argument)},{str(defeat.to_argument)})"
                for defeat in opened_af.defeats
            )
            file_name = selected_example.split(".")[0]  # Remove the file extension
            # When selecting an example, we leave the dropdown selection unchanged.
            return abstract_arguments_value, abstract_attacks_value, selected_example, file_name, raw_json
        except Exception as e:
            print(f"Error reading example file {selected_example}: {e}")
            return "", "", no_update, no_update, no_update

    return "", "", no_update, no_update, no_update
