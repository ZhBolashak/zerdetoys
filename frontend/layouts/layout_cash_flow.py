#layout_cash_flow.py
from dash import html, dcc
import dash_bootstrap_components as dbc

def payment_article_get_layout():
    return dbc.Container([
        dbc.Row(dbc.Col(html.H1("Дебиторка: движения средств"))),
        dbc.Row([
            dbc.Col(dcc.Dropdown(id='payment-article-dropdown', placeholder="Выберите статью")),
            dbc.Col(dcc.Dropdown(id='dropdown-cash-client', placeholder='Выберите клиента')),
        ],style={'margin-bottom': '20px'}),  # Добавление отступа снизу
        dbc.Row([
            dbc.Col(dcc.Dropdown(id='dropdown-cash-store', placeholder='Выберите магазин')),
            dbc.Col(dcc.Dropdown(id='dropdown-cash-wallet', placeholder='Выберите кошелек')),
            dbc.Col(dcc.Dropdown(id='dropdown-cash-currency', placeholder='Выберите валюту')),
            dbc.Col(dcc.DatePickerSingle(id='single-date-picker', placeholder='Выберите дату', display_format='YYYY-MM-DD')),
            dbc.Col(dcc.Input(id='input-amount', type='number', placeholder='Введите сумму', min=0)),
            dbc.Col(html.Button('Сохранить', id='submit-button')),
        ]),
        html.Div(id='selected-article-name'),  # Элемент для отображения выбранной статьи
        html.Div(id='submission-status'),  # Элемент для отображения статуса отправки данных
        # Инициализирующие элементы для каждого компонента
        html.Div(id='init-particle', style={'display': 'none'}),
        html.Div(id='init-cash-store', style={'display': 'none'}),
        html.Div(id='init-cash-client', style={'display': 'none'}),
        html.Div(id='init-cash-wallet', style={'display': 'none'}),
        html.Div(id='init-cash-currency', style={'display': 'none'}),
    ])


def cash_flow_debt_layout():
    return dbc.Container([
        dbc.Row(dbc.Col(html.H1("Посаженные данные"))),
        dbc.Row(dbc.Col(html.Div(id='cash-flow-debt-output'))),
        dcc.Interval(id='init_cash_flow_debt', interval=3600*1000, n_intervals=0) # Интервал для автоматического вызова колбэка,
    ])


def cash_flow_debt_combined_layout():
    return dbc.Container([
        payment_article_get_layout(),
        html.Hr(),  # Разделитель между секциями
        cash_flow_debt_layout(),
    ])