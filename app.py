# app.py
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc

# layouts,
from frontend.layouts.layout_product import product_get_layout, download_excel_layout
from frontend.layouts.layout_sale import sale_get_layout, download_excel_sale_layout
from frontend.layouts.layout_sidebar import sidebar_layout
from frontend.layouts.layout_debt import debt_get_layout
from frontend.layouts.layout_cash_flow import payment_article_get_layout

#callbacks
from frontend.callbacks.callback_product import register_callbacks as register_product_callbacks
from frontend.callbacks.callback_sale import sale_callbacks as register_sale_callbacks
from frontend.callbacks.callback_debt import debt_callbacks
from frontend.callbacks.callback_cash_flow import cash_flow_callbacks

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
    if pathname == "/": return  download_excel_layout(), product_get_layout()
    elif pathname == "/sales": return download_excel_sale_layout(), sale_get_layout()
    elif pathname == "/cashflow": return payment_article_get_layout()
    elif pathname == "/debt": return debt_get_layout()
    else:
        # Обновленный компонент для замены устаревшего Jumbotron
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

# Запуск сервера
server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)
