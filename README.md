# Interrail planer

## The basic challenge
This Python based application is designed to help users plan interrail trips based on their preferences of selected countries and citites in Europe. 
From OpenStreetMap (OSM) through the Overpass API, the application collects data about the railway network in the cuntries selected by the user, and calculates the optimal route between the chosen multiple cities. The results are visualised in a map in your webbrowser. 

## Data
The data extracted from OSM is:
- railways
- stations
- cities
- heritage/cultural sites
- natural parks

## Pre-processing
The Overpass API returns crude froms of data that requiers aditinal data pre-processing to create a network where routing can be performed.
The pre-processing is as follows:
- Snap stations to rails. This geograpically aligns the stations with the railway tracks. 
- Split segments where stations are snapped to the rail, creating two segments from the original one. This enables stations to be start and end points of the network. 
- Connect create artificial rails between stations closer than 500 m to each other. This is to simulate changing trains at two different stations that are near to each other. 

## Routing
The routing process consist of the following steps:
- Linkning stations to cities. 
- Calculating and create a shortest path distance matrix between all combinations of input cities.
- Based on the distance matrix, the "traveling salesman problem (TSP)" is solved using Dijkstra's algorithm.
- Finally, other cities, cultural sites and natural parks that are in proximity to the route are ge


## Spatial database overview of possible tables: 
1)	Railway lines
2)	Railway stations
3)	Cities
4)	Customer (table for user information and preferences for possible further data analyses)
 
## The programme features as input parameters
1)	personal information (name, age, nationality)
2)	which cities hen wants to visit 
3)	the start and end point of the trip

## Calculations
The problem we are trying to solve is often referred to as the “Travelling Salesperson Problem”. The optimal route calculations could be done in two ways:
1)	In the form of actually calculating all the possible combinations of routes between the cities and returning the shortest route (most likely the approach we will take).
2)	We could implement a more advanced algorithm to make the calculation more efficient.

## Results and Visualisation
The result should be a simple map with the best matching route for the users preferences. Either the programme will call QGIS or a web framework will be developed. 

## Possible extensions
If possible within time constraints we might try to implement the following additional features:
1)	Include a bigger railway network (like adding Spain) or let the user choose the railway network
1)	Instead of only using the railway distance, also implement travel time by using the average speed of trains in calculations.
→ Enable the user to specify the timeframe of the trip (1 week or 2 weeks etc.).
2)	Choose more preferences like natural parks or cultural sites.
 

