import streamlit as st
import pandas as pd
import requests
from io import BytesIO
from datetime import datetime

API_URL = 'http://localhost:8000'

# Функция для получения данных о товарах с вашего FastAPI сервера
def fetch_products(store=None, provider=None):
    # Параметры для запроса к API
    params = {
        'store': store,
        'provider': provider
    }
    response = requests.post(f'{API_URL}/api/v1/products/', json=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f'Ошибка получения данных: {response.status_code}')
        return []

# Функции для получения магазинов и провайдеров
def fetch_stores():
    response = requests.get(f'{API_URL}/api/v1/stores')
    return response.json() if response.status_code == 200 else []

def fetch_providers():
    response = requests.get(f'{API_URL}/api/v1/providers')
    return response.json() if response.status_code == 200 else []




# Предполагается, что функции fetch_stores, fetch_providers, и fetch_products уже определены

def format_filename(providers):
    # Получаем текущую дату
    date_str = datetime.now().strftime("%Y-%m-%d")
    # Формируем имя файла
    file_name = f"{date_str}_{'_'.join(providers) if providers else 'all_providers'}_zerde.xlsx"
    return file_name

def to_excel(dataframe):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    dataframe.to_excel(writer, sheet_name='Sheet1', index=False)
    writer.close()
    processed_data = output.getvalue()
    return processed_data

def streamlit_interface():
    st.sidebar.title("Остаток товара")

    stores = fetch_stores()
    providers = fetch_providers()
    
    store_names = [store['name'] for store in stores]
    provider_names = [provider['name'] for provider in providers]

    store_filter = st.sidebar.multiselect('Магазин', store_names)
    provider_filter = st.sidebar.multiselect('Поставщик', provider_names)

    if st.sidebar.button('Поиск'):
        products_data = fetch_products(store=store_filter, provider=provider_filter)
        if products_data:
            products_df = pd.DataFrame(products_data)
            # Предполагаем, что 'картинка' является URL изображения
            # Создаем столбец с HTML-кодом для изображений
            products_df['Картинка'] = products_df['картинка'].apply(
                lambda x: f'<img src="{x}" width="50" />' if x else ''
            )
            # Удаляем столбец с URL изображений
            products_df.drop('картинка', axis=1, inplace=True)
            # Используем st.write для отображения HTML-таблицы с изображениями
            st.write(products_df.to_html(escape=False, index=False), unsafe_allow_html=True)
            
            # ... (код для создания Excel-файла и кнопки скачивания)

            
            excel_data = to_excel(products_df)  # Генерируем данные Excel из DataFrame
            file_name = format_filename(provider_filter)
            st.sidebar.download_button(
                label="Скачать Excel",
                data=excel_data,
                file_name=file_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

if __name__ == "__main__":
    streamlit_interface()
