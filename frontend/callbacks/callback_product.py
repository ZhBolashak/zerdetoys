#callback_product.py
from dash import Dash, dcc, html, Input, Output, State, callback, no_update
import dash_bootstrap_components as dbc
import pandas as pd
import requests
from urllib.parse import quote
from datetime import datetime
import io
import validators  
from frontend.config import BASE_URL
from dash.exceptions import PreventUpdate


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


def register_callbacks(app):
    @app.callback(
        [Output('store-dropdown', 'options'),
        Output('provider-dropdown', 'options')],
        Input('init_product', 'children')  # Используем невидимый компонент в качестве Input
    )
    def update_dropdowns(_):
        try:
            response_stores = requests.get(f'{BASE_URL}/api/v1/stores')
            stores = response_stores.json() if response_stores.status_code == 200 else []

            response_providers = requests.get(f'{BASE_URL}/api/v1/providers')
            providers = response_providers.json() if response_providers.status_code == 200 else []

            # Исключаем опции, где label или value равны None
            store_options = [{'label': store['name'], 'value': store['name']} for store in stores if store['name'] is not None]
            provider_options = [{'label': provider['name'], 'value': provider['name']} for provider in providers if provider['name'] is not None]

            return store_options, provider_options
        except Exception as e:
            print(f"Error updating dropdowns: {e}")
            return [], []

    # Функция для обновления столбца 'картинка' с проверкой валидности URL
    def generate_image_html(url):
        if not isinstance(url, str) or not validators.url(url):
            return ""  # Возвращаем пустое значение для невалидных или отсутствующих URL
            
        encoded_url = quote(url, safe=':/')
        return html.Img(src=encoded_url, style={'max-height': '60px', 'max-width': '60px'})

    @app.callback(
        [Output('products-table', 'children'), Output('store-data', 'data')],
        [Input('search-button', 'n_clicks')],
        [State('store-dropdown', 'value'), State('provider-dropdown', 'value')]
    )
    def update_table(n_clicks, selected_stores, selected_providers):
        if not n_clicks or not selected_stores:
            return html.Div("Выберите магазин и нажмите 'Поиск'."), no_update

        data = {
            'store': selected_stores,
            'include_image': True
        }

        if selected_providers:
            data['provider'] = selected_providers

        response = requests.post(f'{BASE_URL}/api/v1/products/', json=data)

        if response.status_code != 200:
            return (f"Ошибка при получении данных: {response.status_code}", no_update)

        products_data = response.json()
        if not products_data:
            return ("Нет данных по выбранным критериям.", no_update)

        products_df = pd.DataFrame(products_data)
        if products_df.empty:
            return ("Нет данных по выбранным критериям.", no_update)

        products_df['картинка'] = products_df['картинка'].apply(generate_image_html)

        table_header = [html.Thead(html.Tr([html.Th(col) for col in products_df.columns]))]
        table_body = [html.Tbody([
            html.Tr([
                html.Td(products_df.iloc[i][col]) if col != 'картинка' else html.Td(products_df.iloc[i][col], style={'text-align': 'center'}) 
                for col in products_df.columns
            ]) for i in range(len(products_df))
        ])]
        table = dbc.Table(table_header + table_body, bordered=True, striped=True, hover=True)

        return table, products_data
 
    
     
    @app.callback(
        Output('download-excel', 'data'),
        Input('download-excel-button', 'n_clicks'),
        State('store-data', 'data')  # Используем данные из dcc.Store
    )
    def download_excel(n_clicks, data):
        if n_clicks is None or data is None:
            raise PreventUpdate
        
        # Конвертируем данные обратно в DataFrame
        products_df = pd.DataFrame(data)

        file_name = f"остаток товара_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"

        # Создаем и возвращаем Excel файл
        return dcc.send_bytes(to_excel(products_df), file_name)

    # Функция to_excel должна быть определена на верхнем уровне модуля
    def to_excel(df):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Sheet1')
        output.seek(0)  # Перемещаем указатель в начало потока
        return output.getvalue()