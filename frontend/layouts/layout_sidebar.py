#layout_sale.py
from dash import  dcc, html
import dash_bootstrap_components as dbc

# Функция для получения лэйаута для ,бокового меню

def sidebar_layout():
    sidebar_header = dbc.Row([
        dbc.Col(html.H2("Отчетность", className="display-4")),
        dbc.Col(html.Hr()),
    ])
    
    sidebar = html.Div(
        [
            sidebar_header,
            dbc.Nav(
                [
                    dbc.NavLink("Остаток товара", href="/", active="exact"),
                    dbc.NavLink("Движение средств", href="/sales", active="exact"),
                ],
                vertical=True,
                pills=True,
            ),
        ],
        style={'padding': '10px', 'border-right': '2px solid #d6d6d6'}
    )
    return sidebar