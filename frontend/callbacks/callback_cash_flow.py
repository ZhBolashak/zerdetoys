#callback_cash_flow.py
from dash import Dash, html, Input, Output, State, callback, no_update
from dash.dependencies import Input, Output, State, ALL, MATCH
from dash import callback_context
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import requests
import json
import pandas as pd

#внутренный импорт
from frontend.config import BASE_URL

# Внешний стиль для Bootstrap
external_stylesheets = [dbc.themes.BOOTSTRAP]


app = Dash(__name__, external_stylesheets=external_stylesheets)


# ---------Callback для получение списка статей-----------------

def cash_flow_callbacks(app):
    # Callback для получения списка статей
    @app.callback(
        Output('payment-article-dropdown', 'options'),
        Input('init-particle', 'children')
    )
    def update_payment_article_dropdown(_):
        try:
            response = requests.get(f'{BASE_URL}/api/debt/payment_articles_debt')
            if response.status_code == 200:
                payment_articles = response.json()
                options = [{'label': article['ref_payment_article'], 'value': article['id']} for article in payment_articles if article['ref_payment_article'] is not None]
                return options
            else:
                print(f"Failed to fetch articles, status code: {response.status_code}")
                return []
        except Exception as e:
            print(f"Error updating dropdowns: {e}")
            return []

    # Callback для получения списка магазинов
    @app.callback(
        Output('dropdown-cash-store', 'options'),
        Input('init-cash-store', 'children')
    )
    def cash_store_options(_):
        try:
            response_stores = requests.get(f'{BASE_URL}/api/dds/store')
            if response_stores.status_code == 200:
                stores = response_stores.json()
                store_options = [{'label': store['name'], 'value': store['id']} for store in stores if store['name'] is not None]
                return store_options
            else:
                print(f"Failed to fetch stores, status code: {response_stores.status_code}")
                return []
        except Exception as e:
            print(f"Error updating dropdowns: {e}")
            return []

    # Callback для получения списка клиентов
    @app.callback(
        Output('dropdown-cash-client', 'options'),
        Input('init-cash-client', 'children')
    )
    def cash_client_options(_):
        try:
            response_clients = requests.get(f'{BASE_URL}/api/debt/clients')
            clients = response_clients.json() if response_clients.status_code == 200 else []
            client_options = [{'label': client['name'], 'value': client['id']} for client in clients if client['name'] is not None]
            return client_options
        except Exception as e:
            print(f"Error updating dropdowns: {e}")
            return []

    # Callback для получения списка кошельков
    @app.callback(
        Output('dropdown-cash-wallet', 'options'),
        Input('init-cash-wallet', 'children')
    )
    def cash_wallet_options(_):
        try:
            response_wallets = requests.get(f'{BASE_URL}/api/dds/wallet')
            if response_wallets.status_code == 200:
                wallets = response_wallets.json()
                wallet_options = [{'label': wallet['name'], 'value': wallet['id']} for wallet in wallets if wallet['name'] is not None]
                return wallet_options
            else:
                print(f"Failed to fetch wallets, status code: {response_wallets.status_code}")
                return []
        except Exception as e:
            print(f"Error updating dropdowns: {e}")
            return []

    # Callback для получения списка валют
    @app.callback(
        Output('dropdown-cash-currency', 'options'),
        Input('init-cash-currency', 'children')
    )
    def cash_currency_options(_):
        try:
            response_currency = requests.get(f'{BASE_URL}/api/dds/currency')
            if response_currency.status_code == 200:
                currency = response_currency.json()
                currency_options = [{'label': currency_item['name'], 'value': currency_item['id']} for currency_item in currency if currency_item['name'] is not None]
                return currency_options
            else:
                print(f"Failed to fetch currency, status code: {response_currency.status_code}")
                return []
        except Exception as e:
            print(f"Error updating dropdowns: {e}")
            return []

    # Callback для обновления даты
    @app.callback(
        Output('output-container-date-picker-single', 'children'),
        Input('single-date-picker', 'date')
    )
    def update_output(date):
        if date is not None:
            # Преобразуем строку даты в объект datetime
            date_object = pd.to_datetime(date)
            # Форматируем дату, чтобы она была понятна пользователю
            date_string = date_object.strftime('%B %d, %Y')
            return 'Вы выбрали следующую дату: {}'.format(date_string)

    # Callback для обновления суммы ввода
    @app.callback(
        Output('output-container-amount', 'children'),
        Input('input-amount', 'value')
    )
    def update_output(value):
        if value is not None:
            # Преобразуем введенное значение в float и выполняем необходимые действия
            try:
                value = float(value)
                return f'Введенная сумма: {value}'
            except ValueError:
                return 'Пожалуйста, введите число'

    # Объединенный callback для записи данных в базу и обновления таблицы
    @app.callback(
        Output('submission-status', 'children'),
        Output('cash-flow-debt-output', 'children'),
        Input('submit-button', 'n_clicks'),
        Input('init_cash_flow_debt', 'n_intervals'),
        State('input-amount', 'value'),
        State('dropdown-cash-client', 'value'),
        State('dropdown-cash-wallet', 'value'),
        State('dropdown-cash-currency', 'value'),
        State('payment-article-dropdown', 'value'),
        State('dropdown-cash-store', 'value'),
        State('single-date-picker', 'date'),
        prevent_initial_call=True,
    )
    def update_content(n_clicks, n_intervals, amount, client_id, wallet_id, currency_id, article_id, store_id, date):
        ctx = callback_context
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        status_message = no_update
        if triggered_id == 'submit-button':
            if n_clicks:
                cash_flow_data = {
                    'amount': amount,
                    'client_id': client_id,
                    'currency_id': currency_id,
                    'payment_article_id': article_id,
                    'wallet_type_id': wallet_id,
                    'occurred_on': date,
                    'store_id': store_id
                }

                print("Отправляемые данные:", cash_flow_data)

                response = requests.post(
                    f'{BASE_URL}/api/dds/cash_flow',
                    json=cash_flow_data,
                    headers={'Content-Type': 'application/json'}
                )

                print("Статус ответа:", response.status_code)
                print("Тело ответа:", response.text)

                if response.status_code == 200:
                    status_message = "Данные успешно отправлены."
                else:
                    status_message = f"Ошибка при отправке данных: {response.text}"
            else:
                raise PreventUpdate

        # Обработка обновления таблицы
        try:
            response = requests.get(f'{BASE_URL}/api/debt/cash_flow_debt')
            if response.status_code == 200:
                cash_flow_data = response.json()
                print("Received data from API:", cash_flow_data)
            else:
                return status_message, html.Div(f"Ошибка при получении данных: {response.status_code}")

            if not cash_flow_data:
                return status_message, html.Div("Нет данных по выбранным критериям.")

            df = pd.DataFrame(cash_flow_data)
            print("DataFrame created:", df)

            table_header = [html.Thead(html.Tr([html.Th(col) for col in df.columns]))]
            table_body = [html.Tbody([html.Tr([html.Td(df.iloc[i][col]) for col in df.columns]) for i in range(len(df))])]
            table = dbc.Table(table_header + table_body, bordered=True, striped=True, hover=True)

            return status_message, table
        except Exception as e:
            print(f"Error loading cash flow data: {e}")
            return status_message, html.Div(f"Error: {str(e)}")