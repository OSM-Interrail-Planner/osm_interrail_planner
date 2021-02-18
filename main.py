import pandas as pd
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go

import dash  # (version 1.12.0) pip install dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

app = dash.Dash()


import geopandas as gpd
import shapely.geometry
import numpy as np
import webbrowser
from threading import Timer






    
# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div([
    html.H1("Here is the route:", style={'text-align': 'center'}),

dcc.Dropdown(id="slct_year",
        options=[
            {"label": "Linha do Vouga", "value": "Linha do Vouga"},
            {"label": "Linha do Norte", "value": "Linha do Norte"},
            {"label": "Linha da Beira Baixan", "value": "Linha da Beira Baixan"},
            {"label": "Ramal de Tomar", "value": "Ramal de Tomar"}],
        multi=False,
        value="nan",
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
    print(f"option:{(option_slctd)}")
    print(type(option_slctd))
    
    geo_df = gpd.read_file("zip://C:/Users/Laptop/temp/railways/railways/railways1.zip")
    print(f"geo_df1: {geo_df}")
    geo_df = geo_df.copy()

    geo_df = geo_df[geo_df["name"] == option_slctd]
    print(f"geo_df2: {geo_df}")

    lats = []
    lons = []
    names = []


    for feature, name in zip(geo_df.geometry, geo_df.name):
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
    print(f"before fig: {geo_df}")
    #fig = px.line_geo(lat=lats, lon=lons, hover_name=names)
    fig = px.line_mapbox(lat=lats, lon=lons, hover_name=names, mapbox_style="stamen-terrain", zoom=7, width=1300, height=800)
    print(f"Fig: {fig}")

    fig.update_geos(fitbounds="locations")



    return fig



# App launcher
def open_browser():
	webbrowser.open_new("http://localhost:{}".format(8050))

if __name__ == '__main__':
    Timer(1, open_browser).start();
    app.run_server(debug=True, port=8050)

