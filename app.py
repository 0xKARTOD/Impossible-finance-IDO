from dash import Dash, html, dcc
from dash.dependencies import Input, Output, State
import flask
import pandas as pd
import json

from scripts.main_kpi import *
from scripts.information_by_pools import *
from scripts.user_types import *
from scripts.best_impossible_users import *

config = {
    'displayModeBar': False
}

pool_addresses = []
full_data = pd.DataFrame()
currency = ['BUSD', 'IDIA']

f = open('config/IDO_pools.json')
IDO_pools = json.load(f)


for item in IDO_pools:
    pool_addresses.append(item['pool_address'].lower())

f.close()

for token in currency:
    df = pd.read_csv('transactions_data/' + str(token) +'_to_pools_transactions.csv')
    df['hash'] = df['hash'].str.lower()
    df['from'] = df['from'].str.lower()
    df['to'] = df['to'].str.lower()
    if token == 'BUSD':
        df['USD_amount'] = df['amount']
    if token == 'IDIA':
        df['USD_amount'] = df['amount']*0.025/0.0136
    full_data = pd.concat([full_data, df])
    
full_data = full_data.loc[(full_data['to']).isin(pool_addresses)]

total_unique_users, total_usd_purchased, unique_IDOS, total_unique_purchase_txs, unique_sale_type = main_kpis(full_data)


USD_by_launchpad, Num_participants = purchased_stats_by_launchpad(full_data)

fig_USD_by_sale, fig_participants_by_sale = purchased_stats_by_launchpad_and_sale(full_data)

fig_USD_by_user_type, fig_participants_by_user_type = purchased_stats_by_user_type(full_data)

table_with_all_users, users_distribution = top_users(full_data)

###############################################################
############################# App #############################
###############################################################

server = flask.Flask(__name__)
app = Dash(__name__, server = server)
app.title = 'IDO Dashboard'

app.layout = html.Div([
    html.Div([
        html.Div([
            html.H6(children = 'Total unique IDO participants',
                style = {
                    'textAlign': 'center',
                    'color': 'white',
                    'fontSize': 18,
                    'margin-top': '15px',
                    'height': '1px'
                }
            ),
            html.P(f"{total_unique_users:,.0f}",
                style = {
                    'textAlign': 'center',
                    'color': 'blue',
                    'fontSize': 45,
                }
            )
        ], className = "card_container"),
        html.Div([
            html.H6(children = 'Total tokens purchased',
                style = {
                    'textAlign': 'center',
                    'color': 'white',
                    'fontSize': 18,
                    'margin-top': '15px',
                    'height': '1px'
                }
            ),
            html.P(f"${total_usd_purchased:,.1f}",
                style = {
                    'textAlign': 'center',
                    'color': 'yellow',
                    'fontSize': 45,
                }
            )
        ], className = "card_container"),
        html.Div([
            html.H6(children = 'Number of IDOs',
                style = {
                    'textAlign': 'center',
                    'color': 'white',
                    'fontSize': 18,
                    'margin-top': '15px',
                    'height': '1px'
                }
            ),
            html.P(f"{unique_IDOS:,.0f}",
                style = {
                    'textAlign': 'center',
                    'color': 'orange',
                    'fontSize': 45,
                }
            )
        ], className = "card_container"),
    ], className = "container"),

    html.Div([
        html.Div([
            html.H6(children = 'Total purchase transactions',
                style = {
                    'textAlign': 'center',
                    'color': 'white',
                    'fontSize': 18,
                    'margin-top': '15px',
                    'height': '1px'
                }
            ),
            html.P(f"{total_unique_purchase_txs:,.0f}",
                style = {
                    'textAlign': 'center',
                    'color': 'blue',
                    'fontSize': 45,
                }
            )
        ], className = "card_container_double"),
        html.Div([
            html.H6(children = 'Unique Sale Types',
                style = {
                    'textAlign': 'center',
                    'color': 'white',
                    'fontSize': 18,
                    'margin-top': '15px',
                    'height': '1px'
                }
            ),
            html.P(f"{unique_sale_type:,.0f}",
                style = {
                    'textAlign': 'center',
                    'color': 'orange',
                    'fontSize': 45,
                }
            )
        ], className = "card_container_double"),
    ], className = "container"),


    html.Div([
        html.H1('Analysis of USD tokens purchased'),
        dcc.Graph(
            id = 'usd-by-launchpad',
            figure = USD_by_launchpad,
            config = config
        ),
        dcc.Graph(
            id = 'usd-by-launchpad-by-sale',
            figure = fig_USD_by_sale,
            config = config
        ),
        dcc.Graph(
            id = 'usd-by-launchpad-by-user-type',
            figure = fig_USD_by_user_type,
            config = config
        )
    ],className = "usd_and_users_cards"
    ),
    html.Div([
        html.H1('Analysis of participants count'),
        dcc.Graph(
            id = 'number-of-participants',
            figure = Num_participants,
            config = config
        ),
        dcc.Graph(
            id = 'number-of-participants-by-sale',
            figure = fig_participants_by_sale,
            config = config
        ),
        dcc.Graph(
            id = 'num-users-by-launchpad-by-user-type',
            figure = fig_participants_by_user_type,
            config = config
        )
    ],className = "usd_and_users_cards"
    ),


    #html.Div(children = dcc.Graph(
    #    id = 'users-table',
    #    figure = table_with_all_users,
    #    config = config
    #),
    #style={'width': '65%', 'display': 'inline-block'},
    #),
    #html.Div(children = dcc.Graph(
    #    id = 'users-histogram',
    #    figure = users_distribution,
    #    config = config
    #),
    #style={'width': '35%', 'display': 'inline-block'},
    #)
])

if __name__ == '__main__':
    app.run_server(debug = True)