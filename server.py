from flask import Flask, render_template, request, redirect
import geopandas as gpd
import folium
import random
import main
import etl as e
import flask_folium as ff
from datetime import datetime, time
from multiprocessing import Process

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
    server.terminate()
    #e.die("process dies")

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

    # Prepare close city data if not empty
    try:
        gdf_close_cities = gpd.read_file("data/close_cities").set_crs("EPSG:32629")
        gdf_close_cities = gdf_close_cities.to_crs("EPSG:4326")
        # create lines from shapely (lon, lat), to folium (lat, lon)
        gdf_close_cities = ff.point_geom(gdf_close_cities)
    except: pass

    # Prepare close heritage data if not empty
    try: 
        gdf_close_heris = gpd.read_file("data/close_heris").set_crs("EPSG:32629")
        gdf_close_heris = gdf_close_heris.to_crs("EPSG:4326")
        # create lines from shapely (lon, lat), to folium (lat, lon)
        gdf_close_heris = ff.point_geom(gdf_close_heris)
    except: pass

    # Prepare close heritage data if not empty
    try: 
        gdf_close_natus = gpd.read_file("data/close_natus").set_crs("EPSG:32629")
        gdf_close_natus = gdf_close_natus.to_crs("EPSG:4326")
        # create lines from shapely (lon, lat), to folium (lat, lon)
        #gdf_close_natus = ff.line_geom(gdf_close_natus)
    except: pass

    # add the nature parks
    ff.add_nature_to_map(gdf_close_natus, map)

    # add the corresponding close heris
    ff.add_close_heris_to_map(gdf_close_heris, map)

    # add the corresponding close cities
    ff.add_close_cities_to_map(gdf_close_cities, map)
    
    # add route to the basemap
    ff.add_route_to_map(gdf_best_route, map)

    # add the start marker
    ff.add_starters_to_map(gdf_best_route, map)
  
    

    # add the layer control for toggling the layers
    map.add_child(folium.LayerControl())
    
    head = """ 
    <h1 style="font-family: Verdana, Geneva, Tahoma, sans-serif;color:rgb(0, 0, 0);float: center;text-align:center;font-size:30px;">
                Here's your optomized route: </h1>
                """

    return head + map._repr_html_()

if __name__ == "__main__":
    app.run(debug=True)