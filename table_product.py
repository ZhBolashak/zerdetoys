from dash import Dash, dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
import pandas as pd
import requests
import validators  # Убедитесь, что установили пакет validators

BASE_URL = 'http://77.243.81.124:8000'  # Определяем базовый URL как глобальную переменную

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])



@app.callback(
    [Output('store-dropdown', 'options'),
     Output('provider-dropdown', 'options')],
    Input('init', 'children')  # Используем невидимый компонент в качестве Input
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
    [Input('search-button', 'n_clicks')],
    [State('store-dropdown', 'value'),
     State('provider-dropdown', 'value')]
)


def update_table(n_clicks, selected_stores, selected_providers):
    if not n_clicks or not selected_stores or not selected_providers:
        # Если кнопка не была нажата или значения не выбраны, не обновляем данные
        return "Пожалуйста, выберите магазин и поставщика и нажмите 'Поиск'."

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
    # Проверяем валидность URL
        if validators.url(url):
            return html.Img(src=url, style={'max-height': '60px', 'max-width': '60px'})
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

    return table
