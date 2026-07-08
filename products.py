# Product CRUD operations (create table, insert, update, delete, view).
import psycopg2
from Database import conn

class Product:
    def __init__(self, name, description, price, quantity):
        self.name = name
        self.description = description
        self.price = price
        self.quantity = quantity

    def create_table():
        cur = conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            price DECIMAL(10, 2) NOT NULL,
            quantity INTEGER NOT NULL
        )''')
        conn.commit()
        cur.close()

    def insert_product(name, description, price, quantity):
        cur = conn.cursor()
        cur.execute('''INSERT INTO products (name, description, price, quantity)
                       VALUES (%s, %s, %s, %s)''',
                    (name, description, price, quantity))
        conn.commit()
        cur.close()

    def update_product(product_id, name=None, description=None, price=None, quantity=None):
        cur = conn.cursor()
        try:
            cur.execute('SELECT * FROM products WHERE id = %s', (product_id,))
            product = cur.fetchone()
            if not product:
                print("Product not found")
                return

            update_fields = []
            values = []
            if name is not None:
                update_fields.append("name = %s")
                values.append(name)
            if description is not None:
                update_fields.append("description = %s")
                values.append(description)
            if price is not None:
                update_fields.append("price = %s")
                values.append(price)
            if quantity is not None:
                update_fields.append("quantity = %s")
                values.append(quantity)

            if not update_fields:
                return

            values.append(product_id)
            update_query = f"UPDATE products SET {', '.join(update_fields)} WHERE id = %s"
            cur.execute(update_query, values)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()
    
    def delete_product(product_id):
        cur = conn.cursor()
        cur.execute('DELETE FROM products WHERE id = %s', (product_id,))
        conn.commit()
        cur.close()

    def view_products():
        cur = conn.cursor()
        cur.execute('SELECT * FROM products')
        products = cur.fetchall()
        cur.close()
        return products
    
    def view_product_id(product_id):
        cur = conn.cursor()
        cur.execute('SELECT * FROM products WHERE id = %s', (product_id,))
        product = cur.fetchone()
        cur.close()
        return product

#Menu
    def product_menu():
        while True:
            print("1. Create Table")
            print("2. Insert Product")
            print("3. Update Product")
            print("4. Delete Product")
            print("5. View Products")
            print("6. View Product by ID")
            print("0. Exit")

            choice = input("Enter choice: ")
            if choice == '1':
                Product.create_table()
                print("Table created")

            elif choice == '2':
                name = input("Enter product name: ")
                description = input("Enter product description: ")
                price = float(input("Enter product price: "))
                quantity = int(input("Enter product quantity: "))
                Product.insert_product(name, description, price, quantity)
                print("Product inserted")

            elif choice == '3':
                product_id = int(input("Enter product id: "))
                name = input("Enter product name: ")
                description = input("Enter product description: ")
                price = float(input("Enter product price: "))
                quantity = int(input("Enter product quantity: "))
                Product.update_product(product_id, name, description, price, quantity)
                print("Product updated")

            elif choice == '4':
                product_id = int(input("Enter product id: "))
                Product.delete_product(product_id)
                print("Product deleted")

            elif choice == '5':
                products = Product.view_products()
                for product in products:
                    print(product)
                print("Product viewed")
            
            elif choice == '6':
                product_id = int(input("Enter product id: "))
                product = Product.view_product_id(product_id)
                print(product)
                print("Product viewed")

            elif choice == '0':
                print("Exiting...")
                break

            else:
                print("Invalid choice. Please try again.")


if __name__ == '__main__':
    Product.product_menu()
