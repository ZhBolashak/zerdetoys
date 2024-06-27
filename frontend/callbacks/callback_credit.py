#callback_credit.py
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

def cash_flow_credit_callbacks(app):
    @app.callback(
        Output('payment-article-credit-dropdown', 'options'),
        Input('init-particle-credit', 'children')
    )
    def update_payment_article_dropdown(_):
        try:
            response = requests.get(f'{BASE_URL}/api/credits/payment_articles_credit')
            if response.status_code == 200:
                #print("API call successful")
                payment_articles = response.json()
                #print("Received data:", payment_articles)
                options = [{'label': article['ref_payment_article'], 'value': article['id']} for article in payment_articles if article['ref_payment_article'] is not None]
                #print("Dropdown options:", options)
                return options
            else:
                print(f"Failed to fetch articles, status code: {response.status_code}")
                return []
        except Exception as e:
            print(f"Error updating dropdowns: {e}")
            return []



# ---------Callback для получение списка провайдеров-----------------
    @app.callback(
        [Output('dropdown-cash-provider', 'options')],
        Input('init-cash-provider', 'children')  
    )
    def cash_client_options(_):
        try:
            response_clients = requests.get(f'{BASE_URL}/api/credits/provider')
            clients = response_clients.json() if response_clients.status_code == 200 else []
            client_options = [{'label': client['name'], 'value': client['id']} for client in clients if client['name'] is not None]
            return [client_options] 
        except Exception as e:
            print(f"Error updating dropdowns: {e}")
            return []


# ---------Callback для получение списка кошельков-----------------
    @app.callback(
        Output('dropdown-cash-wallet-credit', 'options'), 
        Input('init-cash-wallet-credit', 'children') 
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


# ---------Callback для получение списка валют-----------------
    @app.callback(
        Output('dropdown-cash-currency-credit', 'options'),  
        Input('init-cash-currency-credit', 'children')  
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


# ---------Callback для получение даты-----------------
    @app.callback(
        Output('output-container-date-picker-single-credit', 'children'),
        Input('single-date-picker-credit', 'date')
    )
    def update_output(date):
        if date is not None:
            # Преобразуем строку даты в объект datetime
            date_object = date.fromisoformat(date)
            # Форматируем дату, чтобы она была понятна пользователю
            date_string = date_object.strftime('%B %d, %Y')
            return 'Вы выбрали следующую дату: {}'.format(date_string)
        

# ---------Callback для получение суммы ввода-----------------
    @app.callback(
        Output('output-container-amount-credit', 'children'),
        Input('input-amount-credit', 'value')
    )
    def update_output(value):
        if value is not None:
            # Преобразуем введенное значение в float и выполняем необходимые действия
            try:
                value = float(value)
                return f'Введенная сумма: {value}'
            except ValueError:
                return 'Пожалуйста, введите число'


# ---------Callback для записи полученных данных в базу-----------------
    @app.callback(
        Output('submission-status-credit', 'children'),
        Input('submit-button-credit', 'n_clicks'),
        [
            State('input-amount-credit', 'value'),
            State('dropdown-cash-provider', 'value'),
            State('dropdown-cash-wallet-credit', 'value'),
            State('dropdown-cash-currency-credit', 'value'),
            State('payment-article-credit-dropdown', 'value'),
            State('single-date-picker-credit', 'date'),
        ],
        prevent_initial_call=True,
    )
    def submit_to_api(n_clicks, amount, provider_id, wallet_id, currency_id, article_id, date):
        if n_clicks: 
            try:
                cash_flow_data = {
                    'amount': amount,
                    'provider_id': provider_id,
                    'currency_id': currency_id,
                    'payment_article_id': article_id,
                    'wallet_type_id': wallet_id,
                    'occurred_on': date,
                }

                print("Отправляемые данные:", cash_flow_data) 

                response = requests.post(
                    f'{BASE_URL}/api/credits/cash_flow_credit_insert',
                    json=cash_flow_data,
                    headers={'Content-Type': 'application/json'}
                )

                print("Статус ответа:", response.status_code) 
                print("Тело ответа:", response.text) 

                if response.status_code == 200:
                    return "Данные успешно отправлены."
                else:
                    return f"Ошибка при отправке данных: {response.text}"
            except Exception as e:
                print("Произошла ошибка:", str(e))
                return f"Произошла ошибка: {str(e)}"
        else:
            raise PreventUpdate
        
#---------------------посаженные данные по дебиторке---------------------------


    @app.callback(
        Output('cash-flow-credit-output', 'children'),
        Input('init_cash_flow_credit', 'n_intervals')  # Изменение на n_intervals для автоматического вызова
    )
    def load_cash_flow_data(_):
        try:
            response = requests.get(f'{BASE_URL}/api/credits/cash_flow_credit')
            if response.status_code == 200:
                cash_flow_data = response.json()
                #print("Received data from API:", cash_flow_data)
            else:
                return html.Div(f"Ошибка при получении данных: {response.status_code}")

            if not cash_flow_data:
                return html.Div("Нет данных по выбранным критериям.")

            # Создание DataFrame из полученных данных
            df = pd.DataFrame(cash_flow_data)
            #print("DataFrame created:", df)

            # Создание таблицы HTML
            table_header = [html.Thead(html.Tr([html.Th(col) for col in df.columns]))]
            table_body = [html.Tbody([html.Tr([html.Td(df.iloc[i][col]) for col in df.columns]) for i in range(len(df))])]
            table = dbc.Table(table_header + table_body, bordered=True, striped=True, hover=True)

            return table
        except Exception as e:
            print(f"Error loading cash flow data: {e}")
            return html.Div(f"Error: {str(e)}")