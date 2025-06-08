from dash import Input, Output, State, callback, html, callback_context
import dash_bootstrap_components as dbc
import json

@callback(
    Output("file-content-modal", "is_open"),
    Output("file-content-modal-body", "children"),
    Input("show-file-content-button", "n_clicks"),
    Input("close-file-content-modal", "n_clicks"),
    State("raw-json", "data"),
    prevent_initial_call=True,
)
def toggle_file_content_modal(show_clicks, close_clicks, raw_json):
    ctx = callback_context
    if not ctx.triggered:
        return False, None
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    if button_id == "show-file-content-button" and show_clicks:
        if raw_json is None:
            return True, html.Div("No file content available", style={"color": "red"})
        
        try:
            # Format the JSON content for better readability
            formatted_json = json.dumps(raw_json, indent=2)
            return True, html.Pre(formatted_json, style={"whiteSpace": "pre-wrap"})
        except Exception as e:
            return True, html.Div(f"Error displaying content: {str(e)}", style={"color": "red"})
    
    return False, None 