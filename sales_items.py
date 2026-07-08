# sale_items.py operations

# create_table() → Create the sale_items table

# add_item(sale_id, product_id, quantity, price) → Add a product to a sale

# # get_items_by_sale(sale_id) → Fetch all products for a specific sale

import psycopg2
from Database import conn

class SaleItem:
    def __init__(self, sale_id, product_id, quantity, price):
        self.sale_id = sale_id
        self.product_id = product_id
        self.quantity = quantity
        self.price = price
        
    def create_table():
        cur = conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS sale_items (
                        id SERIAL PRIMARY KEY,
                        sale_id INTEGER NOT NULL,
                        product_id INTEGER NOT NULL,
                        quantity INTEGER NOT NULL,
                        price DECIMAL(10, 2) NOT NULL
                    )''')
        conn.commit()
        cur.close()
    def add_item(sale_id, product_id, quantity, price):
        cur = conn.cursor()
        cur.execute('''INSERT INTO sale_items (sale_id, product_id, quantity, price)
                       VALUES (%s, %s, %s, %s)''',
                    (sale_id, product_id, quantity, price))
        conn.commit()
        cur.close()
        print("Item added to sale")
        
    def get_items_by_sale(sale_id):
        cur = conn.cursor()
        cur.execute('SELECT * FROM sale_items WHERE sale_id = %s', (sale_id,))
        items = cur.fetchall()
        cur.close()
        return items

    def view_sale_items(sale_id):
        cur = conn.cursor()
        cur.execute('SELECT * FROM sale_items WHERE sale_id = %s', (sale_id,))
        items = cur.fetchall()
        for item in items:
            print(item)
        cur.close()
        total_amount = 0
        for item in items:
            total_amount += item[3] * item[4]  # quantity * price
        print("Total Amount for Sale ID", sale_id, ":", total_amount)
        return total_amount
    def sale_item_menu():
        while True:
            print("1. Create Table")
            print("2. Add Item to Sale") 
            print("3. View Sale Items")
            print("0. Exit")
            choice = input("Enter choice: ")
            if choice == '1':
                SaleItem.create_table()
                print("Table created")
            elif choice == '2':
                sale_id = int(input("Enter sale id: "))
                product_id = int(input("Enter product id: "))
                quantity = int(input("Enter quantity: "))
                price = float(input("Enter price: "))
                SaleItem.add_item(sale_id, product_id, quantity, price)
                print("Item added to sale")
            elif choice == '3':
                sale_id = int(input("Enter sale id: "))
                total_amount = SaleItem.view_sale_items(sale_id)
                print("Total Amount:", total_amount)
            elif choice == '0':
                print("Exiting...")
                break
            else:
                print("Invalid choice. Please try again.")


if __name__ == '__main__':
    SaleItem.sale_item_menu()

