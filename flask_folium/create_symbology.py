from folium.plugins import MarkerCluster
from folium.features import GeoJsonPopup, GeoJsonTooltip
import geopandas as gpd
import folium


def add_route_to_map(gdf_best_route: gpd.GeoDataFrame, basemap):
    """This function adds the best routes to the basemap 

    Args:
        gdf_best_route (gpd.GeoDataFrame)
        basemap ([type])
    """
    #create a list of random colors
    colors = ['orange', 'darkred', 'darkblue', 'purple', 'darkgreen', '#364e4a', 'cadetblues']
    
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
        basemap.add_child(fg)
    
    return None


def add_close_cities_to_map(gdf_close_cities: gpd.GeoDataFrame, basemap):
    """This function adds the close cities to the basemap 

    Args:
        gdf_close_cities (gpd.GeoDataFrame)
        basemap ([type])
    """ 
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
        basemap.add_child(fg_cities)
    except: pass

    return None


def add_close_heris_to_map(gdf_close_heris: gpd.GeoDataFrame, basemap):
    """This function adds the close heritages to the basemap 

    Args:
        gdf_close_heris (gpd.GeoDataFrame)
        basemap ([type])
    """
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
        basemap.add_child(fg_heris)
    except: pass

    return None


def add_starters_to_map(gdf_best_route: gpd.GeoDataFrame, basemap):
    """This function adds the start cities of the best routes to the basemap 

    Args:
        gdf_best_route (gpd.GeoDataFrame)
        basemap ([type])
    """
    #create a list of random colors
    colors = ['orange', 'darkred', 'darkblue', 'purple', 'darkgreen', '#364e4a', 'cadetblue']
    fg_marker = folium.FeatureGroup("Destination Cities")
    for i, row in gdf_best_route.iterrows():
        fg_marker.add_child(folium.Marker(
            location=row["folium_geom"][0],
            tooltip=f"{row['start_city']}",
            icon=folium.Icon(color=colors[i], icon='train', prefix='fa')
            ))
    basemap.add_child(fg_marker)

    return None

def add_nature_to_map(gdf_close_natus: gpd.GeoDataFrame, basemap):
    """This function adds the nature parks to the basemap 

    Args:
        gdf_close_natus (gpd.GeoDataFrame)
        basemap ([type])
    """
    
    # make a feature group for every route
    # merge them to a feature group
    # add the nature parks
     # add the nature parks
    fg_nature = folium.FeatureGroup("Natural Parks")
    folium.GeoJson(
        gdf_close_natus,
        style_function=lambda feature: {
            'fillColor': 'lightgreen',
            'color' : 'darkgreen',
            'fillOpacity' : 0.5,
            },
        tooltip= GeoJsonTooltip(
            fields=["name"],
            aliases=[""]),
        popup=GeoJsonPopup(
            fields=["name"],
            aliases=[""])
    ).add_to(fg_nature)
    basemap.add_child(fg_nature)
    
    return None