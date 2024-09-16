from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

def product_sale_get_layout():
    return html.Div([
        html.Div(id='init_product', style={'display': 'none'}),

        dbc.Row([
            dbc.Col([
                dcc.Dropdown(
                    id='product-dropdown', 
                    multi=True, 
                    placeholder='Выберите продукты'
                ),
            ], width=6),
            dbc.Col([
                html.Button('Поиск', id='search-button', className='btn btn-primary'),
            ], width=6),
        ], style={'margin-top': '20px'}),

        html.Div(id='order-items-table', style={'margin-top': '20px'}),

        dcc.Store(id='order-items-data'),
    ])
