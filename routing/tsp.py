import random
import pprint as pp
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import shapely.geometry as sg
from shapely.geometry import Point, MultiPoint, MultiLineString
from shapely.ops import nearest_points
import geopandas as gpd
import pandas as pd
import networkx as nx
import momepy


def city_to_station(gdf_city, gdf_station, list_input_city):
    """Relates the input citiy to the closest station and if no station name replace by the city name

    Args:
        gdf_city (gpd.GeoDataFrame)
        gdf_station (gpd.GeoDataFrame)
        list_input_city (gpd.GeoDataFrame): The input list of cities in correct order (first city is start and end point)
    
    Returns:
        gpd.GeoDataFrame: For the stations which are visited in correct order
    """
    # create a pandas dataframe for the list input city
    city_data = {'index':  list(range(len(list_input_city))),
        'city': list_input_city
        }
    city_df = pd.DataFrame (city_data, columns = ['index','city'])

    # Filtering the city GeoDataFrame(gdf_city) to match only the cities of interest (list_input_city).
    new = gdf_city['name'].isin(list_input_city) # -> create a boolean
    gdf_city = gdf_city[new]
    
    # calculate nearest_points() between each city in gdf_city and gdf_stations
    multi_station = MultiPoint(gdf_station['geometry'])
    output_gdf = gpd.GeoDataFrame()
    for i, row in gdf_city.iterrows():
        city_point = row['geometry']
        city_name = row['name']

        near_point = nearest_points(city_point, multi_station) # output = [city point, station point]
        
        near_station = gdf_station[gdf_station['geometry'] == near_point[1]]
        near_station = gpd.GeoDataFrame(near_station)
        near_station['city'] = ''
        near_station['city'] = city_name

        output_gdf = output_gdf.append(near_station)

    # order the output dataframe to have the start city at the beginning
    output_gdf = pd.merge(output_gdf, city_df, on=['city', 'city'])
    output_gdf = output_gdf.set_index('index')
    output_gdf = output_gdf.sort_index()

    # write city name as station name when there is nan
    for i, row in output_gdf.iterrows():
        if row['name'] == 'nan':
            output_gdf.iloc[i, 0] = row['city']

    print(output_gdf)
    return output_gdf


def shortest_path(station_gdf : gpd.GeoDataFrame, start_station_name: str, end_station_name: str, rail_segments_gdf: gpd.GeoDataFrame):
    """
    calculate shortest path between two stations by station name

    Args:
        station_gdf (GeoDataFrame): stations points GeoDataFrame
        start_station_name (str): Then name of the start station
        end_station_name (str): The name of the end station
        rail_segments_gdf (GeoDataFrame): rails segments GeoDataFrame
    """
    #Select the stations raws
    start_station = station_gdf[["name","geometry"]][station_gdf['name'] == start_station_name].head(1)
    end_station = station_gdf[["name","geometry"]][station_gdf['name'] == end_station_name].head(1)
    
    #creat geodataframe from the stations selected
    start_end_dataframe = start_station.append(end_station)
    
    #transefer it into grapgh
    stations_nodes = momepy.gdf_to_nx(start_end_dataframe, approach='primal')
    print("datatype stations", type(stations_nodes))
    
    #create network from the new geo_data_frame
    rail_network = momepy.gdf_to_nx(rail_segments_gdf, approach='primal')
    print("datatype rail_network", type(rail_network ))

    #select start and end stations nodes
    start_node = list(stations_nodes.nodes)[0]
    end_node = list(stations_nodes.nodes)[1]

    shortest_path = nx.shortest_path(rail_network, start_node, end_node, weight=None, method='dijkstra')
    shortest_path_line_string = sg.LineString(list(shortest_path))
    
    return(shortest_path_line_string)

def create_distance_matrix(gdf_input_stations: gpd.GeoDataFrame, rail_segments_gdf, mirror_matrix: bool) -> dict:
    """This function creates a distance matrix including all possible distances between input station list.
    Distances are calculated as shortest path along a network

    Args:
        stations (list):The list of stations contains each station which should be included in the distance matrix
                        This is a list of strings.
        mirror_matrix (bool): If True it takes distances which are already calculated for a pair of stations
                        assumption: distance(1->2) = distance(2->1)

    Returns:
        dict: The dictionary contains two elements.
                1. "stations_index": [list of stations]
                2. "distance_matrix": [[d11=0, d12, d13, d14],
                                       [d21, d22=0, d23, d24],
                                       [d31, d32, d33=0, d34],
                                       [d41, d42, d43, d44=0]]
                3. "path_matrix" (containing LineString objects as paths): 
                                      [[path11=0, path12, path13, path14],
                                       [path21, path22=0, path23, path24],
                                       [path31, path32, path33=0, path34],
                                       [path41, path42, path43, path44=0]]

    """
    stations = list(gdf_input_stations["name"])
    print(stations)
    dict_distance_matrix = {}
    dict_distance_matrix["stations_index"] = stations
    dict_distance_matrix["num_vehicles"] = 1
    dict_distance_matrix['depot'] = 0
    distance_matrix = []
    path_matrix = []

    # Loop over all stations as origins
    for st_origin in stations:
        list_dist_st_origin = []
        list_path_st_origin = []
        # Loop over all stations as destinations
        for st_destination in stations:
            # If station origin and station destination are the same insert distance = 0 or path = None
            if st_origin == st_destination:
                list_dist_st_origin.append(0)
                list_path_st_origin.append(None)

            # If the destination is listed before the origin in the stations the path and distance has already been 
            # calculated. So it can be appended already by distance_matrix[index_destination][index_origin]
            elif (stations.index(st_destination)) < stations.index(st_origin) and (mirror_matrix == True):
                index_origin = stations.index(st_origin)
                index_destination = stations.index(st_destination)
                list_dist_st_origin.append(distance_matrix[index_destination][index_origin])
                list_path_st_origin.append(path_matrix[index_destination][index_origin])

            # Only calculate the path and distance new if the destination station is listed 
            # after the origin station in the stations list
            elif stations.index(st_destination) > stations.index(st_origin) and (mirror_matrix == True):
                shortest_path_result = shortest_path(gdf_input_stations, st_origin, st_destination, rail_segments_gdf)
                list_path_st_origin.append(shortest_path_result)
                distance = shortest_path_result.length/1000
                print(f"from {st_origin} to {st_destination} is takes {distance} kilometers")
                ## FOR TESTING
                ##distance = random.randint(0,1000)
                list_dist_st_origin.append(distance)

            # If mirror_matrix = False just calculate everything
            else:
                shortest_path_result = shortest_path(gdf_input_stations, st_origin, st_destination, rail_segments_gdf)
                list_path_st_origin.append(shortest_path_result)
                distance = shortest_path_result.length/1000
                ## FOR TESTING
                ##distance = random.randint(0,1000)
                list_dist_st_origin.append(distance)

        # After all distances from the origin station have been calculated append it to the matrix
        distance_matrix.append(list_dist_st_origin)
        path_matrix.append(list_path_st_origin)

        # Reset the distance and list to an empty list
        list_dist_st_origin = []
        list_path_st_origin = []


    # After the matrices have been created insert it to the dictionary
    dict_distance_matrix["distance_matrix"] = distance_matrix
    dict_distance_matrix["path_matrix"] = path_matrix

    pp.pprint(dict_distance_matrix)

    return dict_distance_matrix


def tsp_solution(manager, routing, solution, dict_distance_matrix):
    #TODO add informations to the DocString!
    """prints solution on console."""
    print('Objective: {} miles'.format(solution.ObjectiveValue()))
    
    # create the output with index names
    index = routing.Start(0)
    plan_output = "" #starting string
    route_distance = 0 #starting distance
    while not routing.IsEnd(index):
        plan_output += f"{manager.IndexToNode(index)} " #add index to string output
        previous_index = index 
        index = solution.Value(routing.NextVar(index)) #define the following stop...
        route_distance += routing.GetArcCostForVehicle(previous_index, index, 0) #...to get the distance between the stops
    plan_output += '{} '.format(manager.IndexToNode(index))

    # create a string output with city names
    route_list = plan_output.replace(",", " ")
    route_list = route_list.split(" ")
    route_cities = []
    for i in route_list:
        try:
            i = int(i)
            city = dict_distance_matrix["stations_index"][i]
            route_cities.append(city)
        except:
            pass
    route_cities = "-> ".join(route_cities)

    # print the route with indices, cities and distances
    print(route_cities)
    print(plan_output)
    return plan_output


def tsp_calculation(dict_distance_matrix: dict):
    # TODO add informatino to docstring
  
    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(dict_distance_matrix['distance_matrix']), dict_distance_matrix['num_vehicles'], dict_distance_matrix['depot'])
    
    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)
    

    def distance_callback(from_index, to_index):
         # TODO change comments
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return dict_distance_matrix['distance_matrix'][from_node][to_node]
    
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    
    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    
    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    
    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)
    
    # Print solution on console.
    if solution: 
        plan_output = tsp_solution(manager, routing, solution, dict_distance_matrix)
        return plan_output


def merge_tsp_solution(dict_distance_matrix: dict, plan_output:str, crs: str) -> gpd.GeoDataFrame:

    plan_list = plan_output.split(' ')
    plan_list.remove('')

    # Create empty Dictionary for GeoDataFrame
    route_dict = {'start_city': [], 'end_city': [], 'geometry': [], 'distance': []}

    for i in range(len(plan_list)-1):
        start_city_index = int(plan_list[i])
        end_city_index = int(plan_list[i+1])
        route = dict_distance_matrix['path_matrix'][start_city_index][end_city_index]
        distance = dict_distance_matrix['distance_matrix'][start_city_index][end_city_index]
        route_dict['start_city'].append(dict_distance_matrix['stations_index'][start_city_index]) 
        route_dict['end_city'].append(dict_distance_matrix['stations_index'][end_city_index]) 
        route_dict['geometry'].append(route) 
        route_dict['distance'].append(distance) 
    pp.pprint(route_dict)

    route_df = pd.DataFrame (route_dict, columns = ['start_city','end_city', 'geometry', 'distance'])
    print(route_df)
    route_gdf = gpd.GeoDataFrame(route_df, crs=crs)
    print(route_gdf)

    return(route_gdf)
