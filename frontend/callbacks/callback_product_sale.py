# callback_product_sale.py
from dash import Dash, dcc, html, Input, Output, State, callback, no_update
import dash_bootstrap_components as dbc
import pandas as pd
import requests
from dash.exceptions import PreventUpdate
from frontend.config import BASE_URL

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

def product_sale_callbacks(app):
    @app.callback(
        Output('product-dropdown', 'options'),
        Input('init_product', 'children')  
    )
    def update_product_dropdown(_):
        try:
            response = requests.get(f'{BASE_URL}/api/orders/products')
            products = response.json() if response.status_code == 200 else []
            product_options = [{'label': product['product'], 'value': product['id']} for product in products if product.get('product')]
            return product_options
        except Exception as e:
            print(f"Error updating product dropdown: {e}")
            return []

    @app.callback(
        Output('order-items-table', 'children'),
        Input('search-button', 'n_clicks'),
        State('product-dropdown', 'value')
    )
    def update_order_items_table(n_clicks, selected_products):
        if not n_clicks or not selected_products:
            return html.Div("Выберите продукты и нажмите 'Поиск'.")

        if isinstance(selected_products, int):
            selected_products = [selected_products]

        data = {
            'product_ids': selected_products
        }

        try:
            response = requests.post(f'{BASE_URL}/api/orders/order_items', json=data)
            if response.status_code != 200:
                return f"Ошибка при получении данных: {response.status_code}"

            order_items_data = response.json()
            if not order_items_data:
                return "Нет данных по выбранным критериям."

            order_items_df = pd.DataFrame(order_items_data)
            if order_items_df.empty:
                return "Нет данных по выбранным критериям."

            # Create table
            table_header = [html.Thead(html.Tr([html.Th(col) for col in order_items_df.columns]))]
            table_body = [html.Tbody([
                html.Tr([
                    html.Td(order_items_df.iloc[i][col]) for col in order_items_df.columns
                ]) for i in range(len(order_items_df))
            ])]
            table = dbc.Table(table_header + table_body, bordered=True, striped=True, hover=True)

            return table
        except Exception as e:
            print(f"Error fetching order items: {e}")
            return f"Ошибка при получении данных: {e}"