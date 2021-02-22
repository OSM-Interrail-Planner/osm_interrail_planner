from flask import Flask, render_template, request, redirect
import geopandas as gpd
import folium
import random
import main
import etl as e

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
    main.network_preprocessing(config, country)
    return render_template('city.html')


@app.route("/route_between/<str1>/<str2>/<str3>/<str4>/<str5>/<str6>")
def base(str1, str2, str3, str4, str5, str6):

    list_city = [str1, str2, str3, str4, str5, str6]
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
    new_lines = []
    for i, row in gdf_best_route.iterrows():
        line = list(row["geometry"].coords)
        new_line = []
        for point in line:
            new_line.append([point[1], point[0]])
        new_lines.append(new_line)
    gdf_best_route["folium_geom"] = new_lines

    #create a list of random colors
    colors = ['orange', 'red', 'blue', 'purple', 'darkgreen', 'lightgreen', 'orange', 'brown', 'grey']

    # make a feature group for every route
    # merge them to a feature group
    for i, row in gdf_best_route.iterrows():
        fg = folium.FeatureGroup(f"Route {row['order']}")
        fg.add_child(folium.PolyLine(
            locations=row["folium_geom"], 
            popup=f"From {row['start_city']} to {row['end_city']}",
            tooltip=f"Route {row['order']}",
            color=colors[i], 
            dash_array='10',
            weight=4))
        map.add_child(fg)

    # add the start marker
    fg_marker = folium.FeatureGroup("Cities")
    for i, row in gdf_best_route.iterrows():
        fg_marker.add_child(folium.Marker(
            location=row["folium_geom"][0],
            tooltip=f"{row['start_city']}",
            icon=folium.Icon(color=colors[i])
            ))
    map.add_child(fg_marker)
  
    map.add_child(folium.LayerControl())

    return map._repr_html_()

if __name__ == "__main__":
    app.run(debug=True)