def inputs_country():
    while True:
        try:
            Number_Of_Countries = int(input("How many countries do you want to visit? "))
            break
        except ValueError:
            print("Oops!  That was no valid number.  Try again...")
                                  
    Countries_list = []
    while Number_Of_Countries < 1:
        Number_Of_Countries = int(input("Oops!  That was no valid number.  Try again..."))
    if Number_Of_Countries == 1:
        Countries_list.append((input("Which country ? ")))
    else:
        Countries_list.append(input("What is the first country ? "))
        for n in range(Number_Of_Countries-1):
            Countries_list.append(input("What else ? "))
    return(Countries_list)

def all_cities_list(cities: json):
    """
    function to extract a citys from cities Jason file

    Args:
        cities (json): The downloaded Json file of cities
    """
    all_cities_list = []
    for n in range(0, len((list(cities.values())[3]))-1):
        city = list(list(cities.values())[3][n].values())[4].get("name")
        all_cities_list.append(city)
    return(all_cities_list: list)

def inputs_city():
    while True:
        try:
            Number_Of_Cities = int(input("How many cities do you want to visit? "))
            break
        except ValueError:
            print("Oops!  That was no valid number.  Try again...")
            
    while Number_Of_Cities < 2:
        Number_Of_Cities = int(input("Please enter a valid number \n How many cities do you want to visit? "))
    else:
        Cities_list = []
        city = input("What is the first city ? ")
        while city not in all_cities_list:
            city = input("Maybe there is a typo the city name, it is not in our list \n   What is the first city ? ")
        Cities_list.append(city)
        for n in range(Number_Of_Cities-1):
            city = input("What else ? ")
            while city not in all_cities_list:
                city = input("Maybe there is a typo the city name, it is not in our list \n   What is the name of the city ? ")
            Cities_list.append(city)
    return(Cities_list)