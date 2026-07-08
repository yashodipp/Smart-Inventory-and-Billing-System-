#Sales -> Columns: id, customer_id, date, total_amount
import psycopg2
from Database import conn
class Sale:
    def __init__(self, customer_id, date, total_amount):
        self.customer_id = customer_id
        self.date = date
        self.total_amount = total_amount
    def create_table():
        cur = conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS sales (
                        id SERIAL PRIMARY KEY,
                        customer_id INTEGER NOT NULL,
                        date DATE NOT NULL,
                        total_amount DECIMAL(10, 2) NOT NULL
                    )''')
        conn.commit()
        cur.close()
    def insert_sale(customer_id, date, total_amount):
        cur = conn.cursor()
        cur.execute('''INSERT INTO sales (customer_id, date, total_amount)
                       VALUES (%s, %s, %s)''',
                    (customer_id, date, total_amount))
        conn.commit()
        cur.close()

    def view_sales():
        cur = conn.cursor()
        cur.execute('SELECT * FROM sales')
        sales = cur.fetchall()
        for sale in sales:
            print(sale)
        cur.close()

    def view_sale_by_id(sale_id):
        cur = conn.cursor()
        cur.execute('SELECT * FROM sales WHERE id = %s', (sale_id,))
        sale = cur.fetchone()
        print(sale)
        cur.close()

    def add_sale_items(sale_id, product_id, quantity, price):
        cur = conn.cursor()
        cur.execute('''INSERT INTO sale_items (sale_id, product_id, quantity, price)
                       VALUES (%s, %s, %s, %s)''',
                    (sale_id, product_id, quantity, price))
        conn.commit()
        cur.close()

    def update_inventory(product_id, quantity_sold):
        cur = conn.cursor()
        cur.execute('''UPDATE products
                       SET quantity = quantity - %s
                       WHERE id = %s''',
                    (quantity_sold, product_id))
        conn.commit()
        cur.close()
    
    def generate_bill(sale_id):
        cur = conn.cursor()
        cur.execute('SELECT * FROM sale_items WHERE sale_id = %s', (sale_id,))
        sale_items = cur.fetchall()
        print("Bill for Sale ID:", sale_id)
        total_amount = 0
        for item in sale_items:
            print("Product ID:", item[2], "Quantity:", item[3], "Price:", item[4])
            total_amount += item[4] * item[3]
        print("Total Amount:", total_amount)
        cur.close()
        return total_amount
    
#----------Analytical Queries----------#
    def get_total_sales_by_date(start_date, end_date):
        cur = conn.cursor()
        cur.execute('''SELECT SUM(total_amount) FROM sales
                       WHERE date BETWEEN %s AND %s''',
                    (start_date, end_date))
        total_sales = cur.fetchone()[0]
        cur.close()
        return total_sales
    
    def get_top_selling_products():
        cur = conn.cursor()
        cur.execute('''SELECT product_id, SUM(quantity) as total_quantity
                       FROM sale_items
                       GROUP BY product_id
                       ORDER BY total_quantity DESC
                       LIMIT 5''')
        top_products = cur.fetchall()
        cur.close()
        return top_products
    
    def get_sales_by_customer(customer_id):
        cur = conn.cursor()
        cur.execute('SELECT * FROM sales WHERE customer_id = %s', (customer_id,))
        sales = cur.fetchall()
        for sale in sales:
            print(sale)
        cur.close()
        return sales
    
    def sale_menu():
        while True:
            print("1. Create Table")
            print("2. Insert Sale")
            print("3. View Sales")
            print("4. View Sale by ID")
            print("5. Add Sale Items")
            print("6. Update Inventory")
            print("7. Generate Bill")
            print("8. Get Total Sales by Date")
            print("9. Get Top Selling Products")
            print("10. Get Sales by Customer")
            print("0. Exit")
            choice = input("Enter choice: ")
            if choice == '1':
                Sale.create_table()
                print("Table created")
            elif choice == '2':
                customer_id = int(input("Enter customer id: "))
                date = input("Enter date: ")
                total_amount = float(input("Enter total amount: "))
                Sale.insert_sale(customer_id, date, total_amount)
                print("Sale inserted")

            elif choice == '3':
                Sale.view_sales()
                print("Sales viewed")

            elif choice == '4':
                sale_id = int(input("Enter sale id: "))
                Sale.view_sale_by_id(sale_id)
                print("Sale viewed by ID")

            elif choice == '5':
                sale_id = int(input("Enter sale id: "))
                product_id = int(input("Enter product id: "))
                quantity = int(input("Enter quantity: "))
                price = float(input("Enter price: "))
                Sale.add_sale_items(sale_id, product_id, quantity, price)
                print("Sale item added")
            
            elif choice == '6':
                product_id = int(input("Enter product id: "))
                quantity_sold = int(input("Enter quantity sold: "))
                Sale.update_inventory(product_id, quantity_sold)
                print("Inventory updated")
            elif choice == '7':
                sale_id = int(input("Enter sale id: "))
                total_amount = Sale.generate_bill(sale_id)
                print("Total Amount:", total_amount)
            elif choice == '8':
                start_date = input("Enter start date (YYYY-MM-DD): ")
                end_date = input("Enter end date (YYYY-MM-DD): ")
                total_sales = Sale.get_total_sales_by_date(start_date, end_date)
                print("Total Sales from", start_date, "to", end_date, "is:", total_sales)
            elif choice == '9':
                top_products = Sale.get_top_selling_products()
                print("Top Selling Products:")
                for product in top_products:
                    print("Product ID:", product[0], "Total Quantity Sold:", product[1])
            elif choice == '10':
                customer_id = int(input("Enter customer id: "))
                sales = Sale.get_sales_by_customer(customer_id)
                print("Sales for Customer ID:", customer_id)
                for sale in sales:
                    print(sale)
                    print("Total Amount:", Sale.generate_bill(sale[0]))
            
            elif choice == '0':
                print("Exiting...")
                break

            else:
                print("Invalid choice. Please try again.")


if __name__ == '__main__':
    Sale.sale_menu()
