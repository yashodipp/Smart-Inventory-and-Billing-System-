# Customer Table → Stores basic customer info (id, name, contact).
# Operations:

# CRUD: Add, View, Update, Delete

# Analytics / Helpers: Get sales by customer, search customer

import psycopg2
from Database import conn
class Customer:
    def __init__(self, name, contact):
        self.name = name
        self.contact = contact
    def create_table():
        cur = conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS customers (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            contact VARCHAR(100) NOT NULL
        )''')
        conn.commit()
        cur.close()
    def insert_customer(name, contact):
        cur = conn.cursor()
        cur.execute('''INSERT INTO customers (name, contact)
                       VALUES (%s, %s)''',
                    (name, contact))
        conn.commit()
        cur.close()
    def update_customer(customer_id, name=None, contact=None):
        cur = conn.cursor()
        try:
            cur.execute('SELECT * FROM customers WHERE id = %s', (customer_id,))
            customer = cur.fetchone()
            if not customer:
                print("Customer not found")
                return

            update_fields = []
            values = []
            if name is not None:
                update_fields.append("name = %s")
                values.append(name)
            if contact is not None:
                update_fields.append("contact = %s")
                values.append(contact)

            if not update_fields:
                return

            values.append(customer_id)
            update_query = f"UPDATE customers SET {', '.join(update_fields)} WHERE id = %s"
            cur.execute(update_query, values)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()
    def delete_customer(customer_id):
        cur = conn.cursor()
        cur.execute('DELETE FROM customers WHERE id = %s', (customer_id,))
        conn.commit()
        cur.close()
    def get_all_customers():
        cur = conn.cursor()
        cur.execute('SELECT * FROM customers')
        customers = cur.fetchall()
        cur.close()
        return customers
    
    def view_customers():
        cur = conn.cursor()
        cur.execute('SELECT * FROM customers')
        customers = cur.fetchall()
        for customer in customers:
            print(customer)
        cur.close()
    def view_customer_by_id(customer_id):
        cur = conn.cursor()
        cur.execute('SELECT * FROM customers WHERE id = %s', (customer_id,))
        customer = cur.fetchone()
        if customer:
            print(customer)
        else:
            print("Customer not found")
        cur.close()
    def get_sales_by_customer(customer_id):
        cur = conn.cursor()
        cur.execute('''SELECT s.id, s.date, s.total_amount FROM sales s
                       JOIN customers c ON s.customer_id = c.id
                       WHERE c.id = %s''', (customer_id,))
        sales = cur.fetchall()
        for sale in sales:
            print(sale)
        cur.close()
    def search_customer(name):
        cur = conn.cursor()
        cur.execute('SELECT * FROM customers WHERE name ILIKE %s', ('%' + name + '%',))
        customers = cur.fetchall()
        for customer in customers:
            print(customer)
        cur.close()
# Menu
    def customer_menu():
        while True:
                print("1. Create Table")
                print("2. Insert Customer")
                print("3. Update Customer")
                print("4. Delete Customer")
                print("5. View Customers")
                print("6. View Customer by ID")
                print("7. Get Sales by Customer")
                print("8. Search Customer")
                print("0. Exit")
                choice = input("Enter choice: ")
                if choice == '1':
                    Customer.create_table()
                    print("Table created")
                elif choice == '2':
                    name = input("Enter customer name: ")
                    contact = input("Enter customer contact: ")
                    Customer.insert_customer(name, contact)
                    print("Customer inserted")

                elif choice == '3':
                    customer_id = int(input("Enter customer id: "))
                    name = input("Enter customer name: ")
                    contact = input("Enter customer contact: ")
                    Customer.update_customer(customer_id, name, contact)
                    print("Customer updated")

                elif choice == '4':
                    customer_id = int(input("Enter customer id: "))
                    Customer.delete_customer(customer_id)
                    print("Customer deleted")
                elif choice == '5':
                    Customer.view_customers()
                    print("Customers viewed")
                elif choice == '6':
                    customer_id = int(input("Enter customer id: "))
                    Customer.view_customer_by_id(customer_id)
                    print("Customer viewed")
                elif choice == '7':
                    customer_id = int(input("Enter customer id: "))
                    Customer.get_sales_by_customer(customer_id)
                    print("Sales viewed")
                elif choice == '8':
                    name = input("Enter customer name: ")
                    Customer.search_customer(name)
                    print("Customer searched")



                elif choice == '0':
                    print("Exiting...")
                    break
                else:
                    print("Invalid choice. Please try again.")
if __name__ == '__main__':
    Customer.customer_menu()
