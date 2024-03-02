import streamlit as st
import pandas as pd
import requests
from io import BytesIO
from datetime import datetime



# Функция для получения данных о товарах с вашего FastAPI сервера
def fetch_products(store=None, provider=None):
    # Параметры для запроса к API
    params = {
        'store': store,
        'provider': provider
    }
    response = requests.post('http://localhost:8000/api/v1/products/', json=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f'Ошибка получения данных: {response.status_code}')
        return []

# Функции для получения магазинов и провайдеров
def fetch_stores():
    response = requests.get('http://localhost:8000/api/v1/stores')
    return response.json() if response.status_code == 200 else []

def fetch_providers():
    response = requests.get('http://localhost:8000/api/v1/providers')
    return response.json() if response.status_code == 200 else []


# Получение данных для фильтров
stores = fetch_stores()
providers = fetch_providers()

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