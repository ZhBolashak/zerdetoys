#layout_product.py
from dash import  dcc, html
import dash_bootstrap_components as dbc

# Функция для получения лэйаута для страницы Остаток товара
def product_get_layout():
    return dbc.Container([
        dbc.Row(dbc.Col(html.H1("Остаток"))),
        dbc.Row([
            dbc.Col(dcc.Dropdown(id='store-dropdown', multi=True, placeholder='Магазин')),
            dbc.Col(dcc.Dropdown(id='provider-dropdown', multi=True, placeholder='Поставщик'))
        ]),
        dbc.Row(dbc.Col(html.Button('Поиск', id='search-button', n_clicks=0))),
        dbc.Row(dbc.Col(html.Div(id='products-table'))),
        html.Div(id='init_product', style={'display': 'none'})
    ])
def download_excel_layout():
    return html.Div([
        dcc.Store(id='store-data'),  # Используется для хранения данных между callbacks
        dbc.Row(dbc.Col(html.Button("Скачать Excel", id="download-excel-button", className='mt-2 mb-2'))),
        dcc.Download(id="download-excel")
    ])