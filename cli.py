from yelpApi import get_attractions
from prompt import generate_itinerary


def show_menu():
    print("\nBon Voyage: Your Travel Planning Assistant!")
    print("0. Show menu again")
    print("1. Plan a new trip")
    print("2. Exit")


def main():
    show_menu()

    while True:
        choice = input("\nEnter your choice: ")

        if choice == "0":
            show_menu()

        elif choice == "1":
            destination = input("Enter a city for your travel itinerary: ")
            days = input("How many days are you traveling for? ")
            try:
                num_days = int(days)
            except ValueError:
                print("Please enter a valid number.")
                continue

            attractions = get_attractions(destination, num_days)
            generate_itinerary(destination, num_days, attractions)

        elif choice == "2":
            print("Bon Voyage!")
            break
        else:
            print("Invalid option, type 0 to see menu again.")


if __name__ == "__main__":
    main()
