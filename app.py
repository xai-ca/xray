# app.py

import dash
import dash_bootstrap_components as dbc
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from server import server
from layout import layout
import callbacks  # noqa: F401 (necessary for callbacks to register)


app = dash.Dash(
    __name__,
    server=server,
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

# Assign the layout from layout.py
app.layout = layout

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=False)

