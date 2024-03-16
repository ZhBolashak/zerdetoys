#layout_sale.py
from dash import  dcc, html
import dash_bootstrap_components as dbc

# Функция для получения лэйаута для страницы ДДС
def sale_get_layout():
    return dbc.Container([
        dbc.Row(dbc.Col(html.H1("ДДСtestestsetset"))),
        dbc.Row([
            dbc.Col(dcc.Dropdown(id='store-dropdown-report', multi=False, placeholder='Выберите магазин')),
            dbc.Col(dcc.DatePickerRange(
                id='date-picker-range',
                start_date_placeholder_text='Начальная дата',
                end_date_placeholder_text='Конечная дата',
                display_format='DD.MM.YYYY'
            ))
        ]),
        dbc.Row(dbc.Col(dbc.Button('Получить отчет', id='get-report-button', n_clicks=0, color='primary', className='me-1'))),
        dbc.Row(dbc.Col(html.Div(id='report-output'))),
        html.Div(id='init_sale', style={'display': 'none'})
    ])

def download_excel_sale_layout():
    return html.Div([
        dcc.Store(id='sale-data'),  # Используется для хранения данных между callbacks
        dbc.Row(dbc.Col(html.Button("Скачать детали в Excel", id="download-excel-button", className='mt-2 mb-2'))),
        dcc.Download(id="download-excel_sale")
    ])
