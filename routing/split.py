import geopandas as gpd
from shapely.ops import split, snap


def split_line_by_nearest_points(gdf_line, gdf_points):
    """
    Split the union of lines with the union of points resulting 
    Parameters
    ----------
    gdf_line : geoDataFrame
        geodataframe with multiple rows of connecting line segments
    gdf_points : geoDataFrame
        geodataframe with multiple rows of single points

    Returns
    -------
    gdf_segments : geoDataFrame
        geodataframe of segments
    """

    # union all geometries
    line = gdf_line.geometry.unary_union
    coords = gdf_points.geometry.unary_union

    # snap and split coords on line
    # returns GeometryCollection
    split_line = split(line, coords)

    # transform Geometry Collection to GeoDataFrame
    segments = [feature for feature in split_line]

    gdf_segments = gpd.GeoDataFrame(
        list(range(len(segments))), geometry=segments, crs=gdf_points.crs)
    gdf_segments.columns = ['index', 'geometry']

    return gdf_segments
