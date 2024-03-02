import streamlit as st
import pandas as pd
import requests
from io import BytesIO
from datetime import datetime

API_URL = 'http://192.168.1.103:8501'

# Функция для получения данных о товарах с вашего FastAPI сервера
def fetch_products(store=None, provider=None):
    # Параметры для запроса к API
    params = {
        'store': store,
        'provider': provider
    }
    try:
        response = requests.post(f'{API_URL}/api/v1/products/', json=params)
        response.raise_for_status()  # Это вызовет исключение для кодов состояния 4xx/5xx
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error occurred: {http_err}")  # HTTP error
    except requests.exceptions.ConnectionError as conn_err:
        st.error(f"Error connecting to the API: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        st.error(f"Timeout error with the API: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        st.error(f"API request error: {req_err}")
    except Exception as err:
        st.error(f"Other error occurred: {err}")  # Other errors
    return []  # Вернуть пустой список в случае ошибки


# Функции для получения магазинов и провайдеров
def fetch_stores(api_url):
    try:
        response = requests.get(f'{api_url}/api/v1/stores')
        response.raise_for_status()  # Will raise HTTPError for bad requests (4xx or 5xx)
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error occurred: {http_err}")  # HTTP error
    except Exception as err:
        st.error(f"Other error occurred: {err}")  # Other errors
    return []  # Return an empty list in case of error


def fetch_providers(api_url):
    try:
        response = requests.get(f'{API_URL}/api/v1/providers')
        response.raise_for_status()  # Поднимет исключение для кодов состояния 4xx/5xx
        return response.json()  # Исправлено здесь
    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error occurred: {http_err}")  # HTTP error
    except Exception as err:
        st.error(f"Other error occurred: {err}")  # Other errors
    return []  # Вернуть пустой список в случае ошибки




# Получение данных для фильтров
stores = fetch_stores(API_URL)
providers = fetch_providers(API_URL)

# Списки имен магазинов и провайдеров для выпадающих списков
store_names = [store['name'] for store in stores]
provider_names = [provider['name'] for provider in providers]

# Создание выпадающих списков фильтров в Streamlit
store_filter = st.sidebar.multiselect('Магазин', store_names)
provider_filter = st.sidebar.multiselect('Поставщик', provider_names)

# Поиск и отображение данных
if st.sidebar.button('Поиск'):
    products_data = fetch_products(store=store_filter, provider=provider_filter)
    if products_data:
        actual_df = pd.DataFrame(products_data)

        # Добавление названий столбцов вручную
        header_cols = st.columns([3,4,4, 3, 8, 4, 4, 2])
        header_cols[0].write("№")
        header_cols[1].write("Магазин")
        header_cols[2].write("Провайдер")
        header_cols[3].write("Остаток")
        header_cols[4].write("Товар")
        header_cols[5].write("Артикул")
        header_cols[6].write("Баркод")
        header_cols[7].write("Картинка")

        # Отображение данных
        for index, product in actual_df.iterrows():
            cols = st.columns([3,4,4, 3, 8, 4, 4, 2])
            cols[0].write(index + 1)
            cols[1].write(product['магазин'])
            cols[2].write(product['провайдер'])
            cols[3].write(product['остаток_колво'])
            cols[4].write(product['товар'])
            cols[5].write(product['vendor_code'])
            cols[6].write(product['barcode'])
            if product['картинка']:
                cols[7].image(product['картинка'], width=44)




        # Функция для форматирования имени файла с текущей датой и именами провайдеров
        def format_filename(providers):
            # Получаем текущую дату
            date_str = datetime.now().strftime("%Y-%m-%d")
            # Если выбран один провайдер, используем его имя
            if len(providers) == 1:
                provider_name = providers[0]
            # Если выбрано несколько провайдеров, объединяем их имена через подчеркивание
            elif providers:
                provider_name = "_".join(providers)
            else:
                provider_name = "all_providers"
            # Формируем имя файла
            file_name = f"{date_str}_{provider_name}_zerde.xlsx"
            return file_name

         # Функция для сохранения DataFrame в байтовом потоке вместо файла на диске
        def to_excel(dataframe):
            output = BytesIO()
            writer = pd.ExcelWriter(output, engine='xlsxwriter')
            dataframe.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.close()
            processed_data = output.getvalue()
            return processed_data

        excel_data = to_excel(actual_df)  # Генерируем данные Excel из DataFrame

        # Использование функции format_filename для задания имени файла
        file_name = format_filename(provider_filter)

        # Кнопка для скачивания Excel файла с динамическим именем файла
        st.sidebar.download_button(
            label="Скачать Excel",
            data=excel_data,
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
