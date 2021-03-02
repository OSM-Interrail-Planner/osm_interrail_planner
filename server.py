from flask import Flask, render_template, request, redirect
import geopandas as gpd
import folium
import main
import etl as e
import flask_folium as ff
import json


app = Flask(__name__)

@app.route("/")
def start():
    return render_template('index.html')

@app.route("/countries")
def select_countries():
    all_countries_list = ['Portugal', 'Spain', "France", "Nederland", "Norway", "Sweden", "United Kingdom", "Schweiz", "Austria", "Belgium", "Luxembourg", "Italia", "Germany", "Ireland", "Liechtenstein", "Danmark", "Polska", "Czechia", "Slovensko" ,"Hungary", "Slovenia", "Croatia", "Bosnia and Herzegovina", "Serbia", "Montenegro", "Albania", "Kosovo", "North Macedonia", "Greece", "Bulgaria", "Turkey", "Romania", "Moldova", "Lithuania", "Latvia", "Estonia", "Finland"]
    all_countries_list.sort()
    all_countries_list.append('None')
    return render_template('country.html', option_list = all_countries_list)

@app.route("/city_selection_in/<str1>/<str2>/<str3>/<str4>/<str5>/<str6>")
def select_cities(str1, str2, str3, str4, str5, str6 ):
    list_country = [str1, str2, str3, str4, str5, str6]
    list_country = set(list_country)
    if 'None' in list_country:
        list_country.remove('None')

    # perform OSM data extraction from Overpass API
    main.extraction(list_country)

    # perform the preprocessin of the data (including the routable network)
    all_cities_list = main.network_preprocessing(list_country)
    all_cities_list.sort()
    all_cities_list.append('None')
    
    all_cities_dict = {'list' : all_cities_list}
    with open('data/original/all_cities_json.txt', 'w') as all_cities_json:
        json.dump(all_cities_dict, all_cities_json)


    return render_template('city.html', option_list = all_cities_list)

@app.route("/route_between/<str1>/<str2>/<str3>/<str4>/<str5>/<str6>")
def base(str1, str2, str3, str4, str5, str6):
    list_city = [str1, str2, str3, str4, str5, str6]
    copy = list_city

    if 'None' in list_city:
        list_city.remove('None')
    try:
        main.routing(list_city)
    except:
        with open('data/original/all_cities_json.txt') as all_cities_json:
            all_cities_dict = json.load(all_cities_json)
        all_cities_list = []
        for element in all_cities_dict['list']:
            all_cities_list.append(element)
        head = """ 
    <h1 style="font-family: Verdana, Geneva, Tahoma, sans-serif;color:rgb(0, 0, 0);float: center;text-align:center;font-size:30px;">
                Sorry Couldn't find a path from some cities </h1>
                """
        return head + render_template('city.html', option_list = all_cities_list)

    # this is base map
    map = folium.Map(
        location=[45, 5],
        zoom_start=4,
        tiles="Stamen Terrain"
    )

    # Prepare route data
    gdf_best_route = gpd.read_file("data/route/best_route")
    gdf_best_route = gdf_best_route.to_crs("EPSG:4326")
    # create lines from shapely (lon, lat), to folium (lat, lon)
    gdf_best_route = ff.line_geom(gdf_best_route)

    # Prepare close city data if not empty
    try:
        gdf_close_cities = gpd.read_file("data/route/close_cities").set_crs("EPSG:32629")
        gdf_close_cities = gdf_close_cities.to_crs("EPSG:4326")
        # create lines from shapely (lon, lat), to folium (lat, lon)
        gdf_close_cities = ff.point_geom(gdf_close_cities)
    except: pass

    # Prepare close heritage data if not empty
    try: 
        gdf_close_heris = gpd.read_file("data/route/close_heris").set_crs("EPSG:32629")
        gdf_close_heris = gdf_close_heris.to_crs("EPSG:4326")
        # create lines from shapely (lon, lat), to folium (lat, lon)
        gdf_close_heris = ff.point_geom(gdf_close_heris)
    except: pass

    # Prepare close heritage data if not empty
    try: 
        gdf_close_natus = gpd.read_file("data/route/close_natus").set_crs("EPSG:32629")
        gdf_close_natus = gdf_close_natus.to_crs("EPSG:4326")
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
    Timer(1, webbrowser.open('http://127.0.0.1:5000/')).start()
    app.run(debug=True, use_reloader=False)
