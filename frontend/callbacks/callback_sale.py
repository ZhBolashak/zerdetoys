#callback_sale.py

from dash import dash,dcc, html, Input, Output, State, no_update
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime
import requests
import io
#для скачивание
from dash.exceptions import PreventUpdate
#внутренный импорт
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
        [Output('report-output', 'children'), Output('sale-data', 'data')],
        [Input('get-report-button', 'n_clicks')],
        [State('store-dropdown-report', 'value'),
        State('date-picker-range', 'start_date'),
        State('date-picker-range', 'end_date')]
    )
    def update_report(n_clicks, selected_store, start_date, end_date):
        if not n_clicks or not selected_store or not start_date or not end_date:
            return [html.Div("Выберите магазин, укажите даты и нажмите 'Получить отчет'."), no_update]

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

        if response.status_code != 200:
            return [html.Div(f"Ошибка при получении данных: {response.status_code}"), no_update]

        raw_data = response.json()

        if not raw_data:
            return [html.Div("Нет данных по выбранным критериям."), no_update]

        # Создание DataFrame из полученных данных
        products_df = pd.DataFrame(raw_data)

        # Агрегирование данных по типу оплаты
        summary_df = products_df.groupby(['days', 'payment']).agg({'amount': 'sum'}).reset_index()

        # Сортировка данных для удобства просмотра
        summary_df = summary_df.sort_values(['days', 'payment'])

        # Создание таблицы HTML
        table_header = [html.Thead(html.Tr([html.Th(col) for col in summary_df.columns]))]
        table_body = [html.Tbody([html.Tr([html.Td(summary_df.iloc[i][col]) for col in summary_df.columns]) for i in range(len(summary_df))])]
        table = [dbc.Table(table_header + table_body, bordered=True, striped=True, hover=True)]

        return [table, raw_data]  # Возвращаем готовую таблицу для отображения на странице



    @app.callback(
        Output('download-excel_sale', 'data'),
        Input('download-excel-button', 'n_clicks'),
        State('sale-data', 'data')  # Используем данные из dcc.Store
    )
    def download_excel(n_clicks, raw_data):
        if n_clicks is None or raw_data is None:
            raise PreventUpdate
        
        # Конвертируем данные обратно в DataFrame
        products_df = pd.DataFrame(raw_data)

        file_name = f"ДДС_детально_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"

        # Создаем и возвращаем Excel файл
        return dcc.send_bytes(to_excel(products_df), file_name)

    # Функция to_excel должна быть определена на верхнем уровне модуля
    def to_excel(df):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Sheet1')
        output.seek(0)  # Перемещаем указатель в начало потока
        return output.getvalue()




# ... Код для запуска сервера ...
    if __name__ == '__main__':
        app.run_server(debug=True)
