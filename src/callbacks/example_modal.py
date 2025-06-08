from dash import Input, Output, State, callback, html, callback_context
import dash_bootstrap_components as dbc
import json
import os

EXAMPLES_FOLDER = "examples"

@callback(
    Output("example-content-modal", "is_open"),
    Output("example-content-modal-body", "children"),
    Input("show-more-button", "n_clicks"),
    Input("close-example-modal", "n_clicks"),
    State("examples-dropdown", "value"),
    prevent_initial_call=True,
)
def toggle_example_modal(show_clicks, close_clicks, selected_example):
    ctx = callback_context
    if not ctx.triggered:
        return False, None
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    if button_id == "show-more-button" and show_clicks:
        if not selected_example:
            return True, html.Div("No example selected", style={"color": "red"})
        
        try:
            # Read the example file directly
            example_path = os.path.join(EXAMPLES_FOLDER, selected_example)
            with open(example_path, "r", encoding="utf-8") as file:
                file_content = json.load(file)
            
            # Format the JSON content for better readability
            formatted_json = json.dumps(file_content, indent=2)
            return True, html.Div([
                html.H5(f"Example: {selected_example}"),
                html.Pre(formatted_json, style={
                    "whiteSpace": "pre-wrap",
                    "backgroundColor": "#f8f9fa",
                    "padding": "15px",
                    "borderRadius": "5px",
                    "border": "1px solid #dee2e6",
                    "maxHeight": "70vh",
                    "overflowY": "auto"
                })
            ])
        except Exception as e:
            return True, html.Div(f"Error reading example file: {str(e)}", style={"color": "red"})
    
    return False, None 