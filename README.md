# Interrail planer

## The basic challenge
We want to create an application where a user can easily plan his/her route for an interrail trip based on his preferences of selected cities in Portugal.
The system should collect railway data from an API connected to OpenStreetMap and calculate the optimal route between the chosen multiple cities. Then this should be visualised for the user on a map.

## Data
The extracted OpenStreetMap (OSM) data should contain at least line features for the railways and point features for the train station. This will be transformed into a network to perform routing analyses on.
Trials for accessing OSM data:
1)	The Overpass API for extracting specific features in OSM can be reached by the python packages overpy or request  but returns quite crude data requiring more data pre-processing.
2)	We also tried accessing the data using OSMnx, which is a Python package designed for downloading, modeling, visualising, and analysing spatial data from OSM. With a single line of Python this gives access to analysis-ready data within the package environment. However, OSMnx was too slow for retrieving the size of datasets we wanted for this project.

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
 

