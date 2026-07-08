# main.py is your central hub:

# Presents the main menu

# Directs the user to Customer, Product, or Sales operations

# Loops until exit

# Connects all modules together so the system works as one application

#Analytical Queries

import psycopg2
from Database import conn
from customers import Customer
from products import Product
from sales import Sale
from sales_items import SaleItem

def main_menu():
    while True:
        print("1. Customer Management")
        print("2. Product Management")
        print("3. Sales Management")
        print("4. Exit")
        choice = input("Select an option: ")
        if choice == '1':
            Customer.customer_menu()
        elif choice == '2':
            Product.product_menu()
        elif choice == '3':
            Sale.sale_menu()
        elif choice == '4':
            print("Exiting the application.")
            break
        else:
            print("Invalid choice. Please try again.")
        
if __name__ == "__main__":
    main_menu()