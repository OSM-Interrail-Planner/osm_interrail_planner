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
        Cities_list.append((input("What is the first city ? ")))
        for n in range(Number_Of_Cities-1):
           Cities_list.append((input("What else ? ")))
    return(Cities_list)