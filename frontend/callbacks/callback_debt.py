#callback_debt.py
from dash import Dash, dcc, html, Input, Output, State, callback, no_update
import dash_bootstrap_components as dbc
import pandas as pd
import requests
from urllib.parse import quote
from datetime import datetime
import io
from frontend.config import BASE_URL
from dash.exceptions import PreventUpdate


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


def debt_callbacks(app):
    @app.callback(
        [Output('client-dropdown', 'options')],
        Input('init_debt', 'children')  
    )
    def debt_dropdowns(_):
        try:
            response_clients = requests.get(f'{BASE_URL}/api/debt/clients')
            clients = response_clients.json() if response_clients.status_code == 200 else []

            client_options = [{'label': client['name'], 'value': client['name']} for client in clients if client['name'] is not None]

            return [client_options] 
        except Exception as e:
            print(f"Error updating dropdowns: {e}")
            return [], []  # This should return a list within a list

    @app.callback(
        Output('report-debt-output', 'children'),
        [Input('get-debt-button', 'n_clicks')],
        [State('client-dropdown', 'value'), 
        State('date-picker-range', 'start_date'),
        State('date-picker-range', 'end_date')]
    )
    def debt_report(n_clicks, selected_client, start_date, end_date):
        if not n_clicks or not selected_client or not start_date or not end_date:
            return html.Div("Выберите клиента, укажите даты и нажмите 'Получить отчет'.")

        # Создание строки запроса
        params = {
            'client': selected_client,
            'start_date': start_date,
            'end_date': end_date
        }

        # Выполнение POST-запроса с параметрами в строке запроса
        response = requests.post(f'{BASE_URL}/api/debt/debt/', params=params)

        if response.status_code == 200:
            debt_data = response.json()
        else:
            return html.Div(f"Ошибка при получении данных: {response.status_code}")

        if not debt_data:
            return html.Div("Нет данных по выбранным критериям.")

        # Получение данных
        debt_data = response.json()

        if not debt_data:
            return html.Div("Нет данных по выбранным критериям.")

        # Создание DataFrame из полученных данных
        df = pd.DataFrame(debt_data)

        # Преобразование столбцов 'Debet' и 'Kredit' в числовые значения
        df['Debet'] = pd.to_numeric(df['Debet'], errors='coerce').fillna(0)
        df['Kredit'] = pd.to_numeric(df['Kredit'], errors='coerce').fillna(0)

        # Агрегирование данных по first_name
        summary_df = df.groupby('first_name').agg({
            'Debet': 'sum',
            'Kredit': 'sum'
        }).reset_index()

        # Расчет разницы между Кредитом и Дебетом
        summary_df['Balance'] = summary_df['Kredit'] - summary_df['Debet']

        # Сортировка данных для удобства просмотра
        summary_df = summary_df.sort_values('first_name')

        # Создание таблицы HTML
        table_header = [html.Thead(html.Tr([html.Th(col) for col in summary_df.columns]))]
        table_body = [html.Tbody([html.Tr([html.Td(summary_df.iloc[i][col]) for col in summary_df.columns]) for i in range(len(summary_df))])]
        table = dbc.Table(table_header + table_body, bordered=True, striped=True, hover=True)


        # Создание таблицы HTML
        table_header2 = [html.Thead(html.Tr([html.Th(col) for col in df.columns]))]
        table_body2 = [html.Tbody([html.Tr([html.Td(df.iloc[i][col]) for col in df.columns]) for i in range(len(df))])]
        table2 = dbc.Table(table_header2 + table_body2, bordered=True, striped=True, hover=True)

        return table,table2 
