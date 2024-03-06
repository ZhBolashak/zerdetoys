#callback_sale.py
from dash import dash,dash_table,html, Input, Output, State, no_update
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime
import requests
#from dash.exceptions import PreventUpdate
from frontend.config import BASE_URL

app = dash.Dash(__name__)

def sale_callbacks(app):
    @app.callback(
        Output('store-dropdown-report', 'options'),
        Input('init_sale', 'children')
    )
    def get_store_options(_):

        try:
            response_stores = requests.get(f'{BASE_URL}/api/dds/store')
            #print(f"Status Code: {response_stores.status_code}")  # Проверяем статус код
            if response_stores.status_code == 200:
                stores = response_stores.json()
                #print(f"Stores received: {stores}")  # Логируем список магазинов
                store_options = [{'label': store['name'], 'value': store['name']} for store in stores if store['name'] is not None]
            else:
                print(f"Failed to fetch stores, status code: {response_stores.status_code}")
                stores = []
                store_options = []
            return store_options
        except Exception as e:
            print(f"Error updating dropdowns: {e}")
            return []

    @app.callback(
        Output('report-output', 'children'),
        [Input('get-report-button', 'n_clicks')],
        [State('store-dropdown-report', 'value'),
         State('date-picker-range', 'start_date'),
         State('date-picker-range', 'end_date')]
    )
    def update_report(n_clicks, selected_store, start_date, end_date):
        if not n_clicks or not selected_store or not start_date or not end_date:
            # Если кнопка не была нажата или значения не выбраны, не обновляем данные
            return html.Div("Пожалуйста, выберите магазин и укажите даты и нажмите 'Получить отчет'.")

        # Преобразование дат в нужный формат
        start_date_formatted = datetime.strptime(start_date, '%Y-%m-%d').strftime('%d.%m.%Y') if start_date else None
        end_date_formatted = datetime.strptime(end_date, '%Y-%m-%d').strftime('%d.%m.%Y') if end_date else None

        # Создание строки запроса
        params = {
            'store': selected_store,
            'start_date': start_date_formatted,
            'end_date': end_date_formatted
        }

        # Выполнение POST-запроса с параметрами в строке запроса
        response = requests.post(f'{BASE_URL}/api/dds/sales-and-orders/', params=params)

        if response.status_code == 200:
            raw_data = response.json()
        else:
            return html.Div(f"Ошибка при получении данных: {response.status_code}")

        if not raw_data:
            return html.Div("Нет данных по выбранным критериям.")

        # Создание DataFrame из полученных данных
        products_df = pd.DataFrame(raw_data)

        # Создание таблицы HTML
        table_header = [html.Thead(html.Tr([html.Th(col) for col in products_df.columns]))]
        table_body = [html.Tbody([html.Tr([html.Td(products_df.iloc[i][col]) for col in products_df.columns]) for i in range(len(products_df))])]
        table = dbc.Table(table_header + table_body, bordered=True, striped=True, hover=True)

        return table  # Возвращаем готовую таблицу для отображения на странице
 



# ... Код для запуска сервера ...
    if __name__ == '__main__':
        app.run_server(debug=True)
