from dash import Dash, dcc, html, Input, Output, State, callback, no_update
import dash_bootstrap_components as dbc
import pandas as pd
import requests
import io
from urllib.parse import quote
from datetime import date, datetime
from frontend.config import BASE_URL
from dash.exceptions import PreventUpdate
import re  # Для удаления запрещенных символов из имени клиента

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
            return [[]]  # Return an empty list inside a list

    @app.callback(
        [Output('report-debt-output', 'children'),
         Output('debt-data', 'data')],
        [Input('get-debt-button', 'n_clicks')],
        [State('client-dropdown', 'value'), 
         State('date-picker-range', 'start_date'),
         State('date-picker-range', 'end_date')]
    )
    def debt_report(n_clicks, selected_client, start_date, end_date):
        if not n_clicks:
            return [html.Div("Нажмите 'Получить отчет' для получения данных."), no_update]

        if not start_date:
            start_date = "2024-01-01"
        if not end_date:
            end_date = date.today().isoformat()

        params = {
            'client': selected_client if selected_client else '',
            'start_date': start_date,
            'end_date': end_date
        }

        response = requests.post(f'{BASE_URL}/api/debt/debt/', params=params)

        if response.status_code == 200:
            debt_data = response.json()
        else:
            return [html.Div(f"Ошибка при получении данных: {response.status_code}"), no_update]

        if not debt_data:
            return [html.Div("Нет данных по выбранным критериям."), no_update]

        df = pd.DataFrame(debt_data)

        df['Debet'] = pd.to_numeric(df['Debet'], errors='coerce').fillna(0)
        df['Kredit'] = pd.to_numeric(df['Kredit'], errors='coerce').fillna(0)

        summary_df = df.groupby('first_name').agg({
            'Debet': 'sum',
            'Kredit': 'sum'
        }).reset_index()

        summary_df['Balance'] = summary_df['Kredit'] - summary_df['Debet']
        summary_df = summary_df.sort_values('first_name')

        table_header = [html.Thead(html.Tr([html.Th(col) for col in summary_df.columns]))]
        table_body = [html.Tbody([html.Tr([html.Td(summary_df.iloc[i][col]) for col in summary_df.columns]) for i in range(len(summary_df))])]
        table = dbc.Table(table_header + table_body, bordered=True, striped=True, hover=True)

        table_header2 = [html.Thead(html.Tr([html.Th(col) for col in df.columns]))]
        table_body2 = [html.Tbody([html.Tr([html.Td(df.iloc[i][col]) for col in df.columns]) for i in range(len(df))])]
        table2 = dbc.Table(table_header2 + table_body2, bordered=True, striped=True, hover=True)

        return [[table, table2], df.to_dict('records')]

    @app.callback(
        Output('download-excel_debt', 'data'),
        Input('download-excel-button', 'n_clicks'),
        State('debt-data', 'data'),
        State('client-dropdown', 'value')
    )
    def download_excel(n_clicks, data, client_name):
        if n_clicks is None or data is None:
            raise PreventUpdate

        products_df = pd.DataFrame(data)
        
        # Очистка имени клиента от запрещенных символов
        clean_client_name = re.sub(r'[^a-zA-Z0-9А-Яа-яЁё-]', '_', client_name) if client_name else 'unknown_client'

        # Генерация названия файла
        file_name = f"debt_{clean_client_name}_{datetime.now().strftime('%Y-%m-%d')}.xlsx"

        return dcc.send_bytes(to_excel(products_df), file_name)

    def to_excel(df):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Sheet1')
        output.seek(0)
        return output.getvalue()