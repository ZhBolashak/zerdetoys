from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
# Импортируем функции из файла table_product.py
from table_product import update_table, update_dropdowns

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Добавление невидимого компонента для инициализации данных
app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1("Остаток товара"))),
    dbc.Row([
        dbc.Col(dcc.Dropdown(id='store-dropdown', multi=True, placeholder='Магазин')),
        dbc.Col(dcc.Dropdown(id='provider-dropdown', multi=True, placeholder='Поставщик'))
    ]),
    dbc.Row(dbc.Col(html.Button('Поиск', id='search-button', n_clicks=0))),
    dbc.Row(dbc.Col(html.Div(id='products-table'))),
    # Невидимый компонент
    html.Div(id='init', style={'display': 'none'})
])

# Callback для обновления выпадающих списков
@app.callback(
    [Output('store-dropdown', 'options'),
     Output('provider-dropdown', 'options')],
    Input('init', 'children')
)
def dropdowns_callback(_):
    return update_dropdowns(_)

# Callback для обновления таблицы продуктов
@app.callback(
    Output('products-table', 'children'),
    [Input('search-button', 'n_clicks')],
    [State('store-dropdown', 'value'),
     State('provider-dropdown', 'value')]
)
def table_callback(n_clicks, selected_stores, selected_providers):
    return update_table(n_clicks, selected_stores, selected_providers)

if __name__ == '__main__':
    app.run_server(debug=True)
