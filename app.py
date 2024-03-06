# app.py
from dash import Dash, dcc, html
import dash_bootstrap_components as dbc
from frontend.layouts.layout_main import product_get_layout, sale_get_layout, download_excel_layout
from frontend.callbacks.callback_product import register_callbacks as register_product_callbacks
from frontend.callbacks.callback_sale import sale_callbacks as register_sale_callbacks

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    dcc.Tabs([
        dcc.Tab(label='Остаток товара', children=[product_get_layout(), download_excel_layout()]),
        dcc.Tab(label='Движение средств', children=[sale_get_layout()]),
    ])
])

# Регистрация коллбэков для каждой вкладки
register_product_callbacks(app)
register_sale_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True)
