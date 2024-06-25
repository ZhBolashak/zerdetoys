# callback_cash_flow_costs.py
from dash import Dash, html, Input, Output, State, callback, no_update
from dash.dependencies import Input, Output, State, ALL
import dash_bootstrap_components as dbc
from datetime import datetime
import pandas as pd
import requests
from frontend.config import BASE_URL
from dash import callback_context
from dash.exceptions import PreventUpdate
import json

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

def cash_flow_costs_callbacks(app):
    @app.callback(
        Output('cash-flow-output', 'children'),
        Input('init_cash_flow', 'children')  # Триггерим callback при загрузке страницы
    )
    def load_cash_flow_data(_):
        response = requests.get(f'{BASE_URL}/api/costs/cash_flow_costs')

        if response.status_code == 200:
            cash_flow_data = response.json()
        else:
            return html.Div(f"Ошибка при получении данных: {response.status_code}")

        if not cash_flow_data:
            return html.Div("Нет данных по выбранным критериям.")

        # Создание DataFrame из полученных данных
        df = pd.DataFrame(cash_flow_data)

        # Создание таблицы HTML
        table_header = [html.Thead(html.Tr([html.Th(col) for col in df.columns]))]
        table_body = [html.Tbody([html.Tr([html.Td(df.iloc[i][col]) for col in df.columns]) for i in range(len(df))])]
        table = dbc.Table(table_header + table_body, bordered=True, striped=True, hover=True)

        return table

    @app.callback(
        Output('payment-article-dropdown_costs', 'children'),
        Input('init-particle_costs', 'children')
    )
    def update_payment_article_dropdown(_):
        try:
            response = requests.get(f'{BASE_URL}/api/costs/payment_articles_costs')
            if response.status_code == 200:
                payment_articles = response.json()
            else:
                print(f"Failed to fetch payment articles, status code: {response.status_code}")
                return []

            # Словарь для группировки статей платежей по их группам
            grouped_articles = {}
            for article in payment_articles:
                group = article['payment_article_group']
                if group not in grouped_articles:
                    grouped_articles[group] = []
                grouped_articles[group].append(article)

            # Создание DropdownMenu с подменю для каждой группы
            dropdown_items = []
            for group, articles in grouped_articles.items():
                sub_menu_items = [
                    dbc.DropdownMenuItem(
                        article['ref_payment_article'],
                        id={
                            'type': 'payment-article-item_costs',
                            'index': article['payment_article_id']
                        }
                    )
                    for article in articles
                ]
                sub_menu = dbc.DropdownMenu(sub_menu_items, label=group, nav=True)
                dropdown_items.append(sub_menu)

            return dropdown_items

        except Exception as e:
            print(f"Error updating dropdowns: {e}")
            return []

    @app.callback(
        Output('payment-article-dropdown_costs', 'value'),
        [Input({'type': 'payment-article-item_costs', 'index': ALL}, 'n_clicks')],
        [State({'type': 'payment-article-item_costs', 'index': ALL}, 'id')]
    )
    def display_selected_article(n_clicks_list, ids_list):
        ctx = callback_context
        if not ctx.triggered:
            # Если не было события, вернуть значение по умолчанию
            return no_update
        else:
            # Получаем ID выбранной статьи
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            selected_article_id = json.loads(button_id)['index']
            # Возвращаем ID, который будет использоваться в callback для сохранения данных
            return selected_article_id

    @app.callback(
        Output('selected-article-name_costs', 'children'),
        [Input({'type': 'payment-article-item_costs', 'index': ALL}, 'n_clicks')],
        prevent_initial_call=True
    )
    def display_selected_article_name(n_clicks):
        ctx = callback_context
        if not ctx.triggered:
            return "No article selected"
        else:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            selected_article_id = json.loads(button_id)['index']
            # Загружаем список статей заново при каждом вызове функции
            response = requests.get(f'{BASE_URL}/api/costs/payment_articles_costs')
            payment_articles = response.json() if response.status_code == 200 else []
            selected_article_name = next(
                (article['ref_payment_article'] for article in payment_articles if article['payment_article_id'] == selected_article_id),
                "Неизвестная статья"
            )
            return f"Выбранная статья: {selected_article_name}"

    @app.callback(
        Output('dropdown-cash-store_costs', 'options'),
        Input('init-cash-store_costs', 'children')
    )
    def cash_store_options(_):
        try:
            response_stores = requests.get(f'{BASE_URL}/api/costs/store_costs')
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

    @app.callback(
        Output('dropdown-cash-wallet_costs', 'options'),
        Input('init-cash-wallet_costs', 'children')
    )
    def cash_wallet_options(_):
        try:
            response_wallets = requests.get(f'{BASE_URL}/api/costs/wallet_costs')
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

    @app.callback(
        Output('dropdown-cash-currency_costs', 'options'),
        Input('init-cash-currency_costs', 'children')
    )
    def cash_currency_options(_):
        try:
            response_currency = requests.get(f'{BASE_URL}/api/costs/currency_costs')
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

    @app.callback(
        Output('output-container-date-picker-single-costs', 'children'),
        Input('single-date-picker_costs', 'date')
    )
    def update_output(date):
        if date is not None:
            # Преобразуем строку даты в объект datetime
            date_object = datetime.fromisoformat(date)
            # Форматируем дату, чтобы она была понятна пользователю
            date_string = date_object.strftime('%B %d, %Y')
            return 'Вы выбрали следующую дату: {}'.format(date_string)

    @app.callback(
        Output('output-container-amount-costs', 'children'),
        Input('input-amount_costs', 'value')
    )
    def update_output(value):
        if value is not None:
            # Преобразуем введенное значение в float и выполняем необходимые действия
            try:
                value = float(value)
                return f'Введенная сумма: {value}'
            except ValueError:
                return 'Пожалуйста, введите число'

    @app.callback(
        Output('submission-status_costs', 'children'),
        Input('submit-button_costs', 'n_clicks'),
        [
            State('input-amount_costs', 'value'),
            State('dropdown-cash-wallet_costs', 'value'),
            State('dropdown-cash-currency_costs', 'value'),
            State('payment-article-dropdown_costs', 'value'),
            State('dropdown-cash-store_costs', 'value'),
            State('single-date-picker_costs', 'date'),
        ],
        prevent_initial_call=True,
    )
    def submit_to_api(n_clicks, amount, wallet_id, currency_id, article_id, store_id, date):
        if n_clicks:
            cash_flow_data = {
                'amount': amount,
                'currency_id': currency_id,
                'payment_article_id': article_id,
                'wallet_type_id': wallet_id,
                'occurred_on': date,
                'store_id': store_id
            }

            print("Отправляемые данные:", cash_flow_data)

            response = requests.post(
                f'{BASE_URL}/api/costs/cash_flow_costs_insert',
                json=cash_flow_data,
                headers={'Content-Type': 'application/json'}
            )

            print("Статус ответа:", response.status_code)
            print("Тело ответа:", response.text)

            if response.status_code == 200:
                return "Данные успешно отправлены."
            else:
                return f"Ошибка при отправке данных: {response.text}"
        else:
            raise PreventUpdate
