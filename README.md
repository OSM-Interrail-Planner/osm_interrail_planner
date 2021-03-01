# Interrail planer

## The application
This Python based application is designed to help users plan interrail trips based on their preferences of selected countries and citites in Europe. 
From OpenStreetMap (OSM) through the Overpass API, the application collects data about the railway network in the countries selected by the user, and calculates the optimal route between the chosen multiple cities. The results are visualised in a map in your webbrowser. 

## Input parameters
The input parameters from users are:
- Which countries to visit
- Which cities to visit

## Requirements
Following is required to run the program.
- Python 3
- the packages of the requirements.txt
- Run python server.py in the console to start the program

## Data
The data extracted from OSM is:
- railways
- stations
- cities
- heritage/cultural sites
- natural parks

## Pre-processing
The Overpass API returns crude data in json format that requiers aditional data pre-processing to create a network where routing can be performed.
The pre-processing is as follows:
- Snap stations to rails. This geograpically aligns the stations with the railway tracks. 
- Split segments where stations are snapped to the rail, creating two segments from the original one. This enables stations to be start and end points of the network. 
- Connecting stations by creating artificial rails between stations closer than 500 m to each other. This is to simulate changing trains at two different stations or even platforms that are near to each other. 

## Routing
The routing process consist of the following steps:
- Linking stations to cities. 
- Creating a shortest path distance matrix between all combinations of input cities using Dijkstra's algorithm.
- Based on the distance matrix, the "traveling salesman problem (TSP)" is solved.
- Finally, other cities, cultural sites and natural parks that are in geographical proximity to the route are linked to the route. 

## Output and Visualisation
Using the Python based micro web-framework Flask, the final route is presented on a map in the user's web browser toghetere with reccomended cities, cultural sites and natural parks.

## Possible extensions
If possible within time constraints we might try to implement the following additional features:
1)	Include a bigger railway network (like adding Spain) or let the user choose the railway network
1)	Instead of only using the railway distance, also implement travel time by using the average speed of trains in calculations.
→ Enable the user to specify the timeframe of the trip (1 week or 2 weeks etc.).
2)	Choose more preferences like natural parks or cultural sites.
 

