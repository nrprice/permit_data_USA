# Library Imports
import math
import numpy as np
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input
pd.set_option("display.max_columns", 50)
pd.set_option("display.max_rows", 400000)
pd.set_option("display.width", 1000)

# Create app instance & server
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Read Data
census_and_party = pd.read_csv('Assets/output_census_and_party.csv')
gun_data = pd.read_csv('Assets/output_cleaned_gun_data.csv')

# Organise Gun Data
gun_data.drop(columns='Unnamed: 0', inplace=True)
gun_data['date'] = pd.to_datetime(gun_data['date'])
gun_data.set_index('date', inplace=True)

# Organise census and party data
census_and_party['date'] = pd.to_datetime(census_and_party['date'])
census_and_party.set_index('date', inplace=True)

# Check Min Dates
min_dates = [gun_data.index.min(), census_and_party.index.min()]
min_dates.sort()
min_date = min_dates[1]

states_list = gun_data['state'].unique()
metric_list = ['total_permits', 'permits_per_capita', 'handgun', 'long_gun']


# Layout components
title = html.Div([html.Br(),
                  html.H1("Gun Permit Applications Over Time - By State"),
                  html.Br()])
side_box = html.Div([html.H6('Description'),
                     html.Li("Each Election day is marked by the Dashed line"),
                     html.Li('Line color is dependant on which party won the popular vote for an election cycle')],
                     style={'padding': '1rem 1rem',
                            "background-color": "#f8f9fa",
                            'height': '100%',
                            'margin': 'auto',
                            'align-items': 'center',
                            'justify-content': 'center'})

controls = html.Div([html.H6('Please Select State:'),
                                dcc.Dropdown(id='state_choice',
                                             options=[{'label': x, 'value': x} for x in states_list],
                                             value=states_list[0],
                                             style={'width':'50%', 'align':'center', 'color': 'black'}),
                                html.Br(),
                                html.H6('Please select metric:'),
                                dcc.RadioItems(id='metric_choice',
                                               options=[{'label': x.title().replace('_', " "), 'value': x} for x in metric_list],
                                               style={'color': 'black'},
                                               value=metric_list[0],
                                               inputStyle={"margin-right": "5px", 'margin-left': '12px'})])

graph = dcc.Graph(id='graph',
                          config={'displayModeBar': False},
                          style={'width':'100vw', 'height': '75vh'})

# Layout
app.layout = html.Div([
        dbc.Row(dbc.Col(title,
                        style={'textAlign': 'center'})),
        dbc.Row([
                dbc.Col(side_box,
                        width=5),
                dbc.Col(controls)
        ]),
        dbc.Row(graph)
])

@app.callback(
    #Outputs
    Output(component_id='graph', component_property='figure'),
    #Inputs
    Input(component_id='state_choice', component_property='value'),
    Input(component_id='metric_choice', component_property='value')
)

def interactive_graph(state_choice, metric_choice):
    figure = go.Figure()

    date_range = pd.date_range(start=min_date, end='1/02/2021', freq='MS')

    empty_date_df = pd.DataFrame(index=date_range)

    state_data = empty_date_df.join(census_and_party[census_and_party['state'] == state_choice])

    state_data['state'] = state_data['state'].fillna(state_choice)
    state_data['count'] = state_data['count'].interpolate()
    state_data['party'] = state_data['party'].fillna(method='ffill')

    state_guns = gun_data[gun_data['state'] == state_choice]

    joined = state_guns.join(state_data, on='date', how='inner', lsuffix=' ')
    joined['total_permits'] = joined['handgun'] + joined['long_gun'] + (joined['multiple'] * 2)
    joined['permits_per_capita'] = joined['total_permits'] / joined['count']
    # Plot Republican Data
    republican_data = joined[joined['party'] == 'REPUBLICAN']
    republican_data = empty_date_df.join(republican_data)
    figure.add_trace(go.Scatter(x=republican_data.index,
                     y=republican_data[metric_choice],
                     name='Republican',
                     showlegend=True,
                     line_color='red'))
    # Plot Democrat Data
    democrat_data = joined[joined['party'] == 'DEMOCRAT']
    democrat_data = empty_date_df.join(democrat_data)

    figure.add_trace(go.Scatter(x=democrat_data.index,
                     y=democrat_data[metric_choice],
                     name='Democrat',
                     showlegend=True,
                     line_color='blue'))

    election_dates = ['2000-11-07', '2004-11-02', '2008-11-04', '2012-11-06', '2016-11-08', '2020-11-03']
    for date in election_dates:
        figure.add_vline(x=date,
                         line_width=1.5,
                         line_dash='dash')

    return figure

if __name__ == '__main__':
    app.run_server()

