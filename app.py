# app.py
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc

# layouts
from frontend.layouts.layout_product import product_get_layout, download_excel_layout
from frontend.layouts.layout_sale import sale_get_layout, download_excel_sale_layout
from frontend.layouts.layout_sidebar import sidebar_layout
from frontend.layouts.layout_debt import debt_get_layout
from frontend.layouts.layout_cash_flow import cash_flow_debt_combined_layout
from frontend.layouts.layout_cash_flow_costs import combined_layout
from frontend.layouts.layout_credit import cash_flow_credit_combined_layout

# callbacks
from frontend.callbacks.callback_product import register_callbacks as register_product_callbacks
from frontend.callbacks.callback_sale import sale_callbacks as register_sale_callbacks
from frontend.callbacks.callback_debt import debt_callbacks
from frontend.callbacks.callback_cash_flow import cash_flow_callbacks
from frontend.callbacks.callback_cash_flow_costs import cash_flow_costs_callbacks
from frontend.callbacks.callback_credit import cash_flow_credit_callbacks

app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dbc.Row([
        dbc.Col(sidebar_layout(), width=2),
        dbc.Col(html.Div(id='page-content'), width=10),
    ], style={'height': '100vh'})
])

@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def render_page_content(pathname):
    if pathname == "/": return download_excel_layout(), product_get_layout()
    elif pathname == "/sales": return download_excel_sale_layout(), sale_get_layout()
    elif pathname == "/cashflow": return cash_flow_debt_combined_layout()
    elif pathname == "/debt": return debt_get_layout()
    elif pathname == "/credit": return cash_flow_credit_combined_layout()
    elif pathname == "/cash_flow_costs": return combined_layout()
    else:
        return dbc.Container([
            html.H1("404: Страница не найдена", className="text-danger"),
            html.Hr(),
            html.P(f"Путь {pathname} не распознан...")
        ], fluid=True)

# Регистрация колбэков
register_product_callbacks(app)
register_sale_callbacks(app)
debt_callbacks(app)
cash_flow_callbacks(app)
cash_flow_costs_callbacks(app)
cash_flow_credit_callbacks(app)

# Запуск сервера
server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)
