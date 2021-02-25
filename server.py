from flask import Flask, render_template, request, redirect
import geopandas as gpd
from folium.plugins import MarkerCluster
import folium
import random
import main
import etl as e
import flask_folium as ff
from datetime import datetime, time

config = e.read_config("config/00.yml")

app = Flask(__name__)

@app.route("/")
def start():
    return render_template('index.html')

@app.route("/countries")
def select_countries():
    return render_template('country.html')

@app.route("/city_selection_in/<str1>/<str2>")
def select_cities(str1, str2):
    country = [str1, str2]
    main.extraction(config, country)

    all_cities_list = main.network_preprocessing(config, country)
    all_cities_list.append('None')
    
    return render_template('city.html', option_list = all_cities_list)

@app.route("/route_between/<str1>/<str2>/<str3>/<str4>/<str5>/<str6>")
def base(str1, str2, str3, str4, str5, str6):
    list_city = [str1, str2, str3, str4, str5, str6]
    for n in list_city:
        if n == 'None':
            list_city.remove(n)

    main.routing(list_city)

        # this is base map
    map = folium.Map(
        location=[38, -5],
        zoom_start=6,
        tiles="Stamen Terrain"
    )

    # Prepare route data
    gdf_best_route = gpd.read_file("data/best_route")
    gdf_best_route = gdf_best_route.to_crs("EPSG:4326")
    # create lines from shapely (lon, lat), to folium (lat, lon)
    gdf_best_route = ff.line_geom(gdf_best_route)

    # Prepare close city data
    try:
        gdf_close_cities = gpd.read_file("data/close_cities").set_crs("EPSG:32629")
        gdf_close_cities = gdf_close_cities.to_crs("EPSG:4326")
        # create lines from shapely (lon, lat), to folium (lat, lon)
        gdf_close_cities = ff.point_geom(gdf_close_cities)
    except: pass

    # Prepare close heritage data
    try: 
        gdf_close_heris = gpd.read_file("data/close_heris").set_crs("EPSG:32629")
        gdf_close_heris = gdf_close_heris.to_crs("EPSG:4326")
        # create lines from shapely (lon, lat), to folium (lat, lon)
        gdf_close_heris = ff.point_geom(gdf_close_heris)
    except: pass

    #create a list of random colors
    colors = ['orange', 'darkred', 'darkblue', 'purple', 'darkgreen', 'cadetblue', 'lightred']
    
    # make a feature group for every route
    # merge them to a feature group
    for i, row in gdf_best_route.iterrows():
        fg = folium.FeatureGroup(f"Route {row['order']} from {row['start_city']} to {row['end_city']}")
        # add the simple route
        fg.add_child(folium.PolyLine(
            locations=row["folium_geom"], 
            popup=f"From {row['start_city']} to {row['end_city']}",
            tooltip=f"Route {row['order']}",
            color=colors[i], 
            dash_array='10',
            weight=4))
        map.add_child(fg)

    # add the corresponding close cities
    try:
        fg_cities = folium.FeatureGroup('Close Cities')
        for j, rowj in gdf_close_cities.iterrows():
            folium.CircleMarker(
                location=rowj["folium_geom"],
                radius=6,
                tooltip=f"{rowj['name']}",
                popup=f"{rowj['name']}",
                color="darkred",
                fill=True,
                fill_color="black"
                ).add_to(fg_cities)
        map.add_child(fg_cities)
    except: pass
    
    # add the corresponding close heri marker
    try:
        fg_heris = folium.FeatureGroup('Close Heritages')
        marker_cluster = MarkerCluster()
        for i, row in gdf_close_heris.iterrows():
            folium.Marker(
                location=row["folium_geom"],
                popup=f"{row['name']} (Heritage Class)",
                icon=folium.Icon(color="beige", icon='university', prefix='fa')
                ).add_to(marker_cluster)
        fg_heris.add_child(marker_cluster)
        map.add_child(fg_heris)
    except: pass

    # add the start marker
    fg_marker = folium.FeatureGroup("Destination Cities")
    for i, row in gdf_best_route.iterrows():
        fg_marker.add_child(folium.Marker(
            location=row["folium_geom"][0],
            tooltip=f"{row['start_city']}",
            icon=folium.Icon(color=colors[i], icon='train', prefix='fa')
            ))
    map.add_child(fg_marker)
  
    map.add_child(folium.LayerControl())
    
    head = """<h1 style="color:rgb(126, 125, 173);text-align:center;font-size:30px;background-color: rgb(218, 233, 166, 0.7);">
                Hello Team! </h1>"""

    return head + map._repr_html_()

if __name__ == "__main__":
    app.run(debug=True)