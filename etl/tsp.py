# FOR TESTING we use random numbers so far
#from module shortest_path import calculate_shortest_path
import random
import pprint as pp
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import geopandas as gpd


def create_distance_matrix(gdf_input_stations: gpd.GeoDataFrame, mirror_matrix: bool) -> dict:
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
    ## path_matrix = []

    # Loop over all stations as origins
    for st_origin in stations:
        list_dist_st_origin = []
        ## list_path_st_origin = []
        # Loop over all stations as destinations
        for st_destination in stations:

            # If station origin and station destination are the same insert distance = 0 or path = None
            if st_origin == st_destination:
                list_dist_st_origin.append(0)
                ## list_path_st_origin.append(None)

            # If the destination is listed before the origin in the stations the path and distance has already been 
            # calculated. So it can be appended already by distance_matrix[index_destination][index_origin]
            elif (stations.index(st_destination)) < stations.index(st_origin) and (mirror_matrix == True):
                index_origin = stations.index(st_origin)
                index_destination = stations.index(st_destination)
                list_dist_st_origin.append(distance_matrix[index_destination][index_origin])
                ## list_path_st_origin.append(path_matrix[index_destination][index_origin])

            # Only calculate the path and distance new if the destination station is listed 
            # after the origin station in the stations list
            elif stations.index(st_destination) > stations.index(st_origin) and (mirror_matrix == True):
                ## shortest_path = calculate_shortest_path(st_origin, st_destination)
                ## list_path_st_origin.append(distance)
                ## distance = shortest_path.length()
                # FOR TESTING
                distance = random.randint(0,1000)
                list_dist_st_origin.append(distance)

            # If mirror_matrix = False just calculate everything
            else:
                ## shortest_path = calculate_shortest_path(st_origin, st_destination)
                ## list_path_st_origin.append(distance)
                ## distance = shortest_path.length()
                # FOR TESTING
                distance = random.randint(0,1000)
                list_dist_st_origin.append(distance)

        # After all distances from the origin station have been calculated append it to the matrix
        distance_matrix.append(list_dist_st_origin)
        ##path_matrix.append(list_path_st_origin)

        # Reset the distance and list to an empty list
        list_dist_st_origin = []
        ##list_path_st_origin = []


    # After the matrices have been created insert it to the dictionary
    dict_distance_matrix["distance_matrix"] = distance_matrix
    ##dict_distance_matrix["path_matrix"] = path_matrix

    return dict_distance_matrix


def tsp_solution(manager, routing, solution, dict_distance_matrix):
    #TODO add informations to the DocString!
    """prints solution on console."""
    print('Objective: {} miles'.format(solution.ObjectiveValue()))
    
    # create the output with index names
    index = routing.Start(0)
    plan_output = "Route from start station:\n" #starting string
    route_distance = 0 #starting distance
    while not routing.IsEnd(index):
        plan_output += f" {manager.IndexToNode(index)}," #add index to string output
        previous_index = index 
        index = solution.Value(routing.NextVar(index)) #define the following stop...
        route_distance += routing.GetArcCostForVehicle(previous_index, index, 0) #...to get the distance between the stops
    plan_output += ' {}\n'.format(manager.IndexToNode(index))

    # create a string output with city names
    route_list = plan_output.replace("\n", "").replace(",", " ")
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
    return route_cities
    return plan_output

    # WHAT HAPPENS HERE?
    plan_output += 'Route distance: {}miles\n'.format(route_distance)


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
        tsp_solution(manager, routing, solution, dict_distance_matrix)


