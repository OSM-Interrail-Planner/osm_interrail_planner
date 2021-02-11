# FOR TESTING
import random
import pprint as pp


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


dist_dict = create_distance_matrix(["a", "b", "c", "d", "e"], mirror_matrix=True)
pp.pprint(dist_dict)

