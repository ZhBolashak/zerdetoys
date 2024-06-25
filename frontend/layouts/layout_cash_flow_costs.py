from dash import html, dcc
import dash_bootstrap_components as dbc

def cash_flow_get_layout():
    return dbc.Container([
        dbc.Row(dbc.Col(html.H1("Расходы, техничекие операции"))),
        dbc.Row(dbc.Col(html.Div(id='cash-flow-output'))),
        html.Div(id='init_cash_flow', style={'display': 'none'}),
    ])

def payment_article_costs_get_layout():
    return dbc.Container([
        dbc.Row(dbc.Col(html.H1("Указать движения средств"))),
        dbc.Row([
            dbc.Col(dbc.DropdownMenu(id='payment-article-dropdown_costs', label="Выберите статью", nav=True)),
            dbc.Col(dcc.Dropdown(id='dropdown-cash-store_costs', placeholder='Выберите магазин')),
            dbc.Col(dcc.Dropdown(id='dropdown-cash-wallet_costs', placeholder='Выберите кошелек')),
            dbc.Col(dcc.Dropdown(id='dropdown-cash-currency_costs', placeholder='Выберите валюту')),
            dbc.Col(dcc.DatePickerSingle(id='single-date-picker_costs', placeholder='Выберите дату', display_format='YYYY-MM-DD')),
            dbc.Col(dcc.Input(id='input-amount_costs', type='number', placeholder='Введите сумму', min=0)),
        ]),
        dbc.Row(dbc.Col(html.Button('Сохранить', id='submit-button_costs'))),
        html.Div(id='selected-article-name_costs'),
        html.Div(id='submission-status_costs'),
        html.Div(id='init-particle_costs', style={'display': 'none'}),
        html.Div(id='init-cash-store_costs', style={'display': 'none'}),
        html.Div(id='init-cash-wallet_costs', style={'display': 'none'}),
        html.Div(id='init-cash-currency_costs', style={'display': 'none'}),
    ])

def combined_layout():
    return dbc.Container([
        payment_article_costs_get_layout(),
        html.Hr(),  # Разделитель между секциями
        cash_flow_get_layout(),
    ])
