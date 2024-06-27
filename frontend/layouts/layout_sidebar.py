#layout_sidebar.py
from dash import  html
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
                    dbc.NavLink("Дебиторская задолжность", href="/debt", active="exact"),
                    dbc.NavLink("Движение средств:Дебиторка", href="/cashflow", active="exact"),
                    dbc.NavLink("Движение средств:Кредиторка", href="/credit", active="exact"),
                    dbc.NavLink("Движение средств:Расходы", href="/cash_flow_costs", active="exact"),
                    
                ],
                vertical=True,
                pills=True,
            ),
        ],
        style={'padding': '10px', 'borderright': '2px solid #d6d6d6'}
    )
    return sidebar
