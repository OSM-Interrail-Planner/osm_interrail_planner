import geopandas as gpd


def line_geom(line_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """This function converts the geometry from [lon, lat] to [lat, lon] for folium

    Args:
        line_gdf (gpd.GeoDataFrame)

    Returns:
        gpd.GeoDataFrame with column ["folium_geom"]
    """
    new_lines = []
    for i, row in line_gdf.iterrows():
        line = list(row["geometry"].coords)
        new_line = []
        for point in line:
            new_line.append([point[1], point[0]])
        new_lines.append(new_line)
    line_gdf["folium_geom"] = new_lines

    return line_gdf


def point_geom(point_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """This function converts the geometry from [lon, lat] to [lat, lon] for folium

    Args:
        point_gdf (gpd.GeoDataFrame)

    Returns:
        gpd.GeoDataFrame with column ["folium_geom"]
    """
    new_points = []
    for i, row in point_gdf.iterrows():
        point = list(row["geometry"].coords)
        new_points.append([point[0][1], point[0][0]])
    point_gdf["folium_geom"] = new_points

    return point_gdf