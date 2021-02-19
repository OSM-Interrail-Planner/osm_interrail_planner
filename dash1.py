import pandas as pd
import plotly.express as px  
import plotly.graph_objects as go

import dash 
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import geopandas as gpd
import shapely.geometry
import numpy as np
import webbrowser
from threading import Timer



app = dash.Dash()

def open_browser():
    webbrowser.open_new("http://localhost:{}".format(8050))

geo_df = gpd.read_file("zip://C:/Users/Lorenz Beck/Documents/Git/rail_planer/data/best_route.zip") #INSERT PATH HERE!

options_list = []
for i, row in geo_df.iterrows():
    option_dict = {}
    option_dict['label'] = f"{i+1}. {geo_df.iloc[i,0]} to {geo_df.iloc[i,1]}"
    option_dict['value'] = geo_df.iloc[i,0]
    options_list.append(option_dict)

#print(options_list)

#start_city = f"1. {geo_df.iloc[0,0]} to {geo_df.iloc[1,0]}"
    
# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div([
    html.H1("Here is the route:", style={'text-align': 'center'}),

#dcc.RangeSlider(
#    marks={i: 'Label {}'.format(i) for i in range(-5, 7)},
#    min=1,
#    max=6,
#    value=[-3, 4]
#)  

dcc.Dropdown(id="slct_year",
        options=options_list,
        multi=False,
        value="Ortiga",
        style={'width': "40%"}
        ),


    dcc.Graph(id='railway_map')
])

# App callback
@app.callback(
    Output(component_id='railway_map', component_property='figure'),
    Input(component_id='slct_year', component_property='value')
)
def update_output(option_slctd):
    #print(f"option:{(option_slctd)}")
    #print(type(option_slctd))
    
    geo_df = gpd.read_file("zip://C:/Users/Lorenz Beck/Documents/Git/rail_planer/data/best_route.zip") #INSERT PATH HERE!
    #print(f"geo_df1: {geo_df}")
    geo_df = geo_df.copy()
    geo_df_reproject = geo_df.to_crs("EPSG:4326")
    #print(f"geo_df_reproject: {geo_df_reproject}")
    geo_df_reproject = geo_df_reproject[geo_df_reproject["start_city"] == option_slctd]
   
    #print(f"geo_df_reproject2: {geo_df_reproject}")

    lats = []
    lons = []
    names = []

    for feature, name in zip(geo_df_reproject.geometry, geo_df_reproject.start_city):
        if isinstance(feature, shapely.geometry.linestring.LineString):
            linestrings = [feature]
        elif isinstance(feature, shapely.geometry.multilinestring.MultiLineString):
            linestrings = feature.geoms
        else:
            continue
        for linestring in linestrings:
            x, y = linestring.xy
            lats = np.append(lats, y)
            lons = np.append(lons, x)
            names = np.append(names, [name]*len(y))
            lats = np.append(lats, None)
            lons = np.append(lons, None)
            names = np.append(names, None)
    #print(f"before fig: {geo_df}")
    #fig = px.line_geo(lat=lats, lon=lons, hover_name=names)
    fig = px.line_mapbox(lat=lats, lon=lons, hover_name=names, mapbox_style="stamen-terrain", zoom=7, width=1300, height=800)
    #print(f"Fig: {fig}")

    fig.update_geos(fitbounds="locations")

    return fig


# App launcher

def initiate_dash():
    print('RUNNIG DASH SCRIPT')
    Timer(1, open_browser).start()
    app.run_server(debug=True, use_reloader=False, port=8050)

