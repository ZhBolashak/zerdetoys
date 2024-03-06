#callback_product.py
from dash import Dash, dcc, html, Input, Output, State, callback, no_update
import dash_bootstrap_components as dbc
import pandas as pd
import requests
from urllib.parse import quote
from datetime import datetime
import io
import validators  # Убедитесь, что установили пакет validators
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



    @app.callback(
    Output('products-table', 'children'),
    Output('store-data', 'data'),  # Добавление выходного значения для сохранения данных в dcc.Store
    [Input('search-button', 'n_clicks')],
    [State('store-dropdown', 'value'), State('provider-dropdown', 'value')]
    )
    def update_table(n_clicks, selected_stores, selected_providers):
        if not n_clicks or not selected_stores or not selected_providers:
            # Если кнопка не была нажата или значения не выбраны, не обновляем данные
            return html.Div("Пожалуйста, выберите магазин и поставщика и нажмите 'Поиск'."), no_update


        # Подготовка данных для POST-запроса
        data = {
            'store': selected_stores,
            'provider': selected_providers,
            'include_image': True  # Мы хотим получить изображения
        }

        # Выполнение POST-запроса
        response = requests.post(f'{BASE_URL}/api/v1/products/', json=data)

        if response.status_code == 200:
            products_data = response.json()
        else:
            return f"Ошибка при получении данных: {response.status_code}"

        if not products_data:
            return "Нет данных по выбранным критериям."

        # Создание DataFrame из полученных данных
        products_df = pd.DataFrame(products_data)

        # Проверяем, что в DataFrame есть данные
        if products_df.empty:
            return "Нет данных по выбранным критериям."

        # Обновляем столбец 'картинка' для отображения изображений
        def generate_image_html(url):
            # Кодируем URL, чтобы корректно обрабатывать пробелы и другие специальные символы
            encoded_url = quote(url, safe=':/')
            # Проверяем валидность URL
            if validators.url(encoded_url):
                return html.Img(src=encoded_url, style={'max-height': '60px', 'max-width': '60px'})
            return ""  # Возвращаем пустое значение для невалидных URL
        products_df['картинка'] = products_df['картинка'].apply(generate_image_html)

        # Создание таблицы HTML вручную, поскольку dbc.Table.from_dataframe не поддерживает вставку HTML элементов
        table_header = [html.Thead(html.Tr([html.Th(col) for col in products_df.columns]))]
        table_body = [html.Tbody([
            html.Tr([
                html.Td(products_df.iloc[i][col]) if col != 'картинка' else 
                html.Td(products_df.iloc[i][col]) for col in products_df.columns
            ]) for i in range(len(products_df))
        ])]
        table = dbc.Table(table_header + table_body, bordered=True, striped=True, hover=True)

        return table, products_data  # products_data - это список словарей с данными продуктов   
    
     # Этот callback должен быть определен отдельно на верхнем уровне модуля
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