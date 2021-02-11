# FOR TESTING
import random
import pprint as pp
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp


def create_distance_matrix(stations: list, mirror_matrix: bool) -> dict:
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

    """
    dict_distance_matrix = {}
    dict_distance_matrix["stations_index"] = stations
    dict_distance_matrix["num_vehicles"] = 1
    dict_distance_matrix['depot'] = 0
    distance_matrix = []

    # Loop over all stations as origins
    for st_origin in stations:
        list_dist_st_origin = []
        # Loop over all stations as destinations
        for st_destination in stations:

            # If station origin and station destination are the same insert distance = 0
            if st_origin == st_destination:
                list_dist_st_origin.append(0)
            
            # If the destination is listed before the origin in the stations this distance has already been 
            # calculated. So it can be appended already by distance_matrix[index_destination][index_origin]
            elif (stations.index(st_destination)) < stations.index(st_origin) and (mirror_matrix == True):
                index_origin = stations.index(st_origin)
                index_destination = stations.index(st_destination)
                list_dist_st_origin.append(distance_matrix[index_destination][index_origin])

            # Only calculate the distance new if the destination station is listed 
            # after the origin station in the stations list
            elif stations.index(st_destination) > stations.index(st_origin) and (mirror_matrix == True):
                #shortest_path = func_shortest_path(st_origin, st_destination)
                #distance = shortest_path.length()
                # FOR TESTING
                distance = random.randint(0,1000)
                list_dist_st_origin.append(distance)

            # If mirror_matrix = False just calculate everything
            else:
                distance = random.randint(0,1000)
                list_dist_st_origin.append(distance)

        # After all distances from the origin station have been calculated append it to the matrix
        distance_matrix.append(list_dist_st_origin)
        # Reset the distance list to an empty list
        list_dist_st_origin = []


    # After the matrix have been create insert it to the dictionary
    dict_distance_matrix["distance_matrix"] = distance_matrix
    return dict_distance_matrix






def print_solution(manager, routing, solution, dict_distance_matrix):
    """prints solution on console."""
    print('Objective: {} miles'.format(solution.ObjectiveValue()))
    index = routing.Start(0)
    plan_output = "Route from start station:\n"
    route_distance = 0
    while not routing.IsEnd(index):
        plan_output += f" {manager.IndexToNode(index)},"
        previous_index = index
        index = solution.Value(routing.NextVar(index))
        route_distance += routing.GetArcCostForVehicle(previous_index, index, 0)
    plan_output += ' {}\n'.format(manager.IndexToNode(index))

    the_route = []
    for i in plan_output:
        
        try:
            i = int(i)
            data1 = dict_distance_matrix['stations_index'][i]
            the_route.append(data1)
        except:
            pass


    print("->".join(the_route))
    print(plan_output)
    plan_output += 'Route distance: {}miles\n'.format(route_distance)


def main():
    """Entry point of the program"""
    # Intitiate the data problem.
    data = create_distance_matrix(['Lisbon', 'Porto', 'Coimbra', 'Faro', 'Beja', 'Lisbon1', 'Porto1', 'Coimbra1', 'Faro1', 'Beja1', 'Lisbon2', 'Porto2'], mirror_matrix=True)
    pp.pprint(data)
    
    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                          data['num_vehicles'], data['depot'])
    
    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)
    
    
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]
    
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
        print_solution(manager, routing, solution, data)

    

main()