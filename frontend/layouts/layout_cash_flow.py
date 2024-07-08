from dash import Dash, html, dcc, callback, no_update
import dash_bootstrap_components as dbc
import requests
import pandas as pd

# внутренний импорт
from frontend.config import BASE_URL

# Внешний стиль для Bootstrap
external_stylesheets = [dbc.themes.BOOTSTRAP]

app = Dash(__name__, external_stylesheets=external_stylesheets)

def payment_article_get_layout():
    return dbc.Container([
        dbc.Row(dbc.Col(html.H1("Дебиторка: движения средств"))),
        dbc.Row([
            dbc.Col(dcc.Dropdown(id='payment-article-dropdown', placeholder="Выберите статью")),
            dbc.Col(dcc.Dropdown(id='dropdown-cash-client', placeholder='Выберите клиента')),
        ],style={'margin-bottom': '20px'}),
        dbc.Row([
            dbc.Col(dcc.Dropdown(id='dropdown-cash-store', placeholder='Выберите магазин')),
            dbc.Col(dcc.Dropdown(id='dropdown-cash-wallet', placeholder='Выберите кошелек')),
            dbc.Col(dcc.Dropdown(id='dropdown-cash-currency', placeholder='Выберите валюту')),
            dbc.Col(dcc.DatePickerSingle(id='single-date-picker', placeholder='Выберите дату', display_format='YYYY-MM-DD')),
            dbc.Col(dcc.Input(id='input-amount', type='number', placeholder='Введите сумму', min=0)),
            dbc.Col(html.Button('Сохранить', id='submit-button')),
        ]),
        html.Div(id='selected-article-name'),
        html.Div(id='submission-status'),
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
        dcc.Interval(id='init_cash_flow_debt', interval=3600*1000, n_intervals=0),
    ])

def cash_flow_debt_combined_layout():
    return dbc.Container([
        payment_article_get_layout(),
        html.Hr(),
        cash_flow_debt_layout(),
    ])
