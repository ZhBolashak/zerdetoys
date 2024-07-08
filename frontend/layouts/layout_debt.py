from dash import dcc, html
import dash_bootstrap_components as dbc

# Функция для получения лэйаута для страницы ДДС
def debt_get_layout():
    return dbc.Container([
        dbc.Row(dbc.Col(html.H1("Дебиторка"))),
        dbc.Row([
            dbc.Col(dcc.Dropdown(id='client-dropdown', multi=False, placeholder='Выберите клиента')),
            dbc.Col(dcc.DatePickerRange(
                id='date-picker-range',
                start_date_placeholder_text='Начальная дата',
                end_date_placeholder_text='Конечная дата',
                display_format='YYYY-MM-DD'
            ))
        ]),
        dbc.Row(dbc.Col(dbc.Button('Получить отчет', id='get-debt-button', n_clicks=0, color='primary', className='me-1'))),
        dbc.Row(dbc.Col(dbc.Button('Сохранить в Excel', id='download-excel-button', n_clicks=0, color='secondary', className='me-1'))),
        dbc.Row(dbc.Col(dcc.Download(id="download-excel_debt"))),
        dbc.Row(dbc.Col(html.Div(id='report-debt-output'))),
        html.Div(id='init_debt', style={'display': 'none'}),
        dcc.Store(id='debt-data')  # Добавляем Store для хранения данных
    ])
