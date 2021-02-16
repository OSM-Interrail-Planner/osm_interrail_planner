import geopandas as gpd

# FOR TESTING
city_gdf = gpd.read_file("data/processed/cities")
station_gdf = gpd.read_file("data/processed/stations")   
rail_gdf = gpd.read_file("data/processed/railways")

# 1. We need to reproject the data
station_proj = station_gdf.to_crs("EPSG:32629")
city_proj = city_gdf.to_crs("EPSG:32629")
rail_proj = rail_gdf.to_crs("EPSG:32629")

# 2. Spatial index on the lines we are snapping to
rail_proj.sindex # -> now we can query the lines with bounding boxes from a different layer (point)

# 3. Create bounding box for the points in offset distance in meters (that's the reason for the reprojection)
offset = 100
station_bbox = station_proj.bounds + [-offset, -offset, offset, offset]
print(station_bbox)

# 4. Now, we can apply an operation to this station_bbox to find get a list of the lines that overlap:
hits = station_bbox.apply(lambda row: list(rail_proj.sindex.intersection(row)), axis=1)
print(hits)

# 5. Create a better datastructure to relate the station points to their rails in tolerance distance
import pandas as pd
import numpy as np

tmp = pd.DataFrame({
    # index of points table
    "pt_idx": np.repeat(hits.index, hits.apply(len)),    
    # ordinal position of line - access via iloc later
    "line_i": np.concatenate(hits.values)
})
print(tmp)

# 6. Join back to the lines on line_i
    # we use reset_index() to give us the ordinal position of each line
tmp = tmp.join(rail_proj.reset_index(drop=True), on="line_i")
    # Join back to the original points to get their geometry and rename the point geometry as "point"
tmp = tmp.join(station_proj.geometry.rename("point"), on="pt_idx")
    # Convert back to a GeoDataFrame, so we can do spatial ops
tmp = gpd.GeoDataFrame(tmp, geometry="geometry", crs=station_proj.crs)
print(tmp)

# 7. Now we calculate the distance between each line and its associated point feature
tmp["snap_dist"] = tmp.geometry.distance(gpd.GeoSeries(tmp.point))
print(tmp)

# 8. Discard and sort by line bs distance to each point
    # Discard any lines that are greater than tolerance from points
tmp = tmp.loc[tmp.snap_dist <= offset]
    # Sort on ascending snap distance, so that closest goes to top
tmp = tmp.sort_values(by=["snap_dist"])

# 9. Find closest line to a point
    # group by the index of the points and take the first, which is the closest line 
closest = tmp.groupby("pt_idx").first()
    # construct a GeoDataFrame of the closest lines
closest = gpd.GeoDataFrame(closest, geometry="geometry")
print(closest)

# 10. Real Snapping: 
    # Position of nearest point from start of the line
pos = closest.geometry.project(gpd.GeoSeries(closest.point))
    # Get new point location geometry
new_pts = closest.geometry.interpolate(pos)

# 11. Join back the new geometry to our original station
    # Identify the columns we want to copy from the closest line to the point, such as a line ID.
line_columns = []
    # Create a new GeoDataFrame from the columns from the closest line and new point geometries (which will be called "geometries")
snapped = gpd.GeoDataFrame(closest[line_columns],geometry=new_pts)
    # Join back to the original points:
updated_points = station_proj.drop(columns=["geometry"]).join(snapped)
    # You may want to drop any that didn't snap, if so:
updated_points = updated_points.dropna(subset=["geometry"])

updated_points.to_file(driver = 'ESRI Shapefile', filename= "data/snapped_station")