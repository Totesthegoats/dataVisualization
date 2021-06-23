import dash
import plotly.express as px
import pandas as pd
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import numpy as np

# Dataset import
df = pd.read_csv('C:/Users/Toto/OneDrive - National University of Ireland, Galway/MachineEye/Example.csv', sep=',', header=0)
# Create a copy dataset so original isn't altered
ddf = df.copy()
# Chane from Unix timestamp and only use dates
ddf["Time"] = pd.to_datetime(ddf['Time'], unit='s')
ddf["Time"]  = ddf['Time'].dt.strftime('%Y-%m-%d')

# CSS style sheet
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# lists of categories
options1 = sorted(ddf["Machine_ID"].unique().tolist())

# dictionary of category - subcategories
all_options = ddf.groupby("Machine_ID")['Time'].unique()\
                .apply(list).to_dict()

# we add as first subcategory for each category `all`
for k, v in all_options.items():
    all_options[k].insert(0, 'all')

# Create the dash app
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
# HTM components
app.layout = html.Div([

    html.H1("Belfast Harbor Data Overview", style ={'text-align': 'center'}),

    #Droptown for machine type

    dcc.Dropdown(id="slct_machine",
                 options=[{'label': k, 'value': k} for k in all_options.keys()],
                 multi=False,
                 value=options1[0],
                 style={'width': "70%"}
                 ),

    #Dropdown for date
    dcc.Dropdown(id="selct_date",
                 style={'width': "70%"},
    ),

    #HTML Break
    html.Br(),

    html.H2("Heatmap Of Machine Location", style ={'text-align': 'center'}),
    #Map Graph
    dcc.Graph(id='map', figure={}, style={'width': "90%", 'height' : "100%"}), # style = { 'height': "90%"})
    # HTML Break
    html.Br(),
    #Month or day Container
    html.H2(id='output_container', style={'text-align': 'center'}),
    #Bar chart for month or day
    dcc.Graph(id='hist', figure={}, style={'width': "90%"}),
    #HTML Break
    html.Br(),
    #Start time Container
    html.H2(id='day_container', style={'text-align': 'center'}),
])

# ------------------------------------------------------------------------------
#Callback for first drop down
@app.callback(
    Output('selct_date', 'options'),
    [Input('slct_machine', 'value')])
def set_2_options(first_option):
    return [{'label': i, 'value': i} for i in all_options[first_option]]

#Callback for second drop down
@app.callback(
    Output('selct_date', 'value'),
    [Input('selct_date', 'options')])
def set_2_value(available_options):
    return available_options[0]['value']

#Callback for that passes values drop down
@app.callback(
     Output('output_container', 'children'),
     Output('day_container', 'children'),
     Output('map', 'figure'),
     Output('hist', 'figure'),
    [Input('slct_machine', 'value'),
     Input('selct_date', 'value')])
def update_graph(slct_machine, selct_date):
    #fuction that updates the graphs
    dff = df.copy()
    #If all is selected we will plot monthly data on a daily basis
    if selct_date == 'all':
        # Container will populate with this data
        container = "Camera Events/Day"
        #Selected machine will be the MAchine_ID
        dff = dff[dff["Machine_ID"] == slct_machine]
        #Ppopulate the map with datapoints, lat and long coords
        fig = px.density_mapbox(dff, lat='Lat', lon='Long', z ="Time", radius=10, center=dict(lat=54.5973, lon=5.9301), zoom=5, mapbox_style="stamen-terrain")

        #Change time from UNIX to get daily events
        dff['Time'] = pd.to_datetime(dff['Time'], unit='s')

        #Group evenst based on day
        num = dff.groupby(dff.Time.dt.date)["Camera event"].sum()
        num = num.to_frame().reset_index()
        num.columns = ['Date', 'Camera event']
        #Plot events on bar chart
        fig1 = px.bar(num, x=num.Date, y=num["Camera event"])
        #There is no daily start or end time
        day_start = None

    else:
        #If a day, then
        dff["Time"] = pd.to_datetime(dff['Time'], unit='s')

        dff = dff[(dff["Machine_ID"] == slct_machine) & (dff["Time"].dt.strftime('%Y-%m-%d') == selct_date)]

        dff["Time"] = dff['Time'].astype(np.int64) // 10 ** 9
        fig = px.density_mapbox(dff, lat='Lat', lon='Long', z="Time", radius=10, center=dict(lat=54.5973, lon=5.9301),zoom=5, mapbox_style="stamen-terrain")

        dff["Time"] = pd.to_datetime(dff['Time'], unit='s')

        num = dff.groupby(dff.Time.dt.hour)["Camera event"].sum()
        num = num.to_frame().reset_index()
        num.columns = ['Hour', 'Camera event']

        print(num.Hour)

        fig1 = px.bar(num, x=num.Hour, y=num["Camera event"])

        container = "Camera Events/Hour"

        day_start = "Start time for this Machine " + str(num.Hour[0])

        print(day_start)

    return container, day_start, fig, fig1


if __name__ == '__main__':
    app.run_server(debug=True)


# Connect the Plotly graphs with Dash Components
# @app.callback(
#     [Output(component_id='output_container', component_property='children'),
#      Output(component_id='map', component_property='figure'),
#      Output(component_id='hist', component_property='figure')],
#     [State(component_id='slct_machine', component_property='value')]
#
# )
# def update_graph(option_slctd):
#     print(option_slctd)
#     print(type(option_slctd))
#
#     container = "The Machine you have chosen is: {}".format(option_slctd)
#
#     dff = df.copy()
#     dff = dff[dff["Machine ID"] == option_slctd]
#
#     fig = px.density_mapbox(dff, lat='Lat', lon='Long', z ="Time", radius=10, center=dict(lat=54.5973, lon=5.9301), zoom=5, mapbox_style="stamen-terrain")
#
#
#     dff['Time'] = pd.to_datetime(dff['Time'], unit='s')
#     num = dff.groupby(dff.Time.dt.date)["Camera event"].sum()
#     num = num.to_frame().reset_index()
#     num.columns = ['Date', 'Camera event']
#
#
#     fig1 = px.bar(num, x=num.Date, y=num["Camera event"])
#
#
#     return container, fig, fig1



#