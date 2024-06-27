#layout_cash_flow.py
from dash import html, dcc
import dash_bootstrap_components as dbc

def payment_article_credit_layout():
    return dbc.Container([
        dbc.Row(dbc.Col(html.H1("Кредиторка: движения средств"))),
        dbc.Row([
            dbc.Col(dcc.Dropdown(id='payment-article-credit-dropdown', placeholder="Выберите статью")),
            dbc.Col(dcc.Dropdown(id='dropdown-cash-provider', placeholder='Выберите провайдера')),
        ],style={'margin-bottom': '20px'}), 
        dbc.Row([
            dbc.Col(dcc.Dropdown(id='dropdown-cash-wallet-credit', placeholder='Выберите кошелек')),
            dbc.Col(dcc.Dropdown(id='dropdown-cash-currency-credit', placeholder='Выберите валюту')),
            dbc.Col(dcc.DatePickerSingle(id='single-date-picker-credit', placeholder='Выберите дату', display_format='YYYY-MM-DD')),
            dbc.Col(dcc.Input(id='input-amount-credit', type='number', placeholder='Введите сумму', min=0)),
            dbc.Col(html.Button('Сохранить', id='submit-button-credit')),
        ]),
        html.Div(id='selected-article-name'),  
        html.Div(id='submission-status-credit'),  
        html.Div(id='init-particle-credit', style={'display': 'none'}),
        html.Div(id='init-cash-provider', style={'display': 'none'}),
        html.Div(id='init-cash-wallet-credit', style={'display': 'none'}),
        html.Div(id='init-cash-currency-credit', style={'display': 'none'}),
    ])


def cash_flow_credit_layout():
    return dbc.Container([
        dbc.Row(dbc.Col(html.H1("Посаженные данные"))),
        dbc.Row(dbc.Col(html.Div(id='cash-flow-credit-output'))),
        dcc.Interval(id='init_cash_flow_credit', interval=3600*1000, n_intervals=0) 
    ])


def cash_flow_credit_combined_layout():
    return dbc.Container([
        payment_article_credit_layout(),
        html.Hr(),  
        cash_flow_credit_layout(),
    ])