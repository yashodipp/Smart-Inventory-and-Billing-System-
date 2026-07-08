import streamlit as st
import psycopg2
from psycopg2 import sql
from datetime import datetime, date
import sys
import os

# Add the models directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from Database import conn
from customers import Customer
from products import Product
from sales import Sale
from sales_items import SaleItem


def refresh_sequence(sequence_name, table_name):
    cur = conn.cursor()
    cur.execute(
        sql.SQL(
            """
            SELECT setval(
                %s,
                COALESCE((SELECT MAX(id) FROM {table_name}), 1),
                (SELECT COUNT(*) > 0 FROM {table_name})
            )
            """
        ).format(table_name=sql.Identifier(table_name)),
        (sequence_name,)
    )
    conn.commit()
    cur.close()


def format_currency(amount):
    return f"Rs. {float(amount or 0):.2f}"


def update_sale_total(sale_id):
    cur = conn.cursor()
    cur.execute(
        'SELECT COALESCE(SUM(quantity * price), 0) FROM sale_items WHERE sale_id = %s',
        (sale_id,)
    )
    total_amount = cur.fetchone()[0] or 0.0
    cur.execute(
        'UPDATE sales SET total_amount = %s WHERE id = %s',
        (total_amount, sale_id)
    )
    conn.commit()
    cur.close()
    return total_amount


def reset_transaction():
    try:
        conn.rollback()
    except Exception:
        pass


reset_transaction()


# Initialize tables if they don't exist
def initialize_tables():
    try:
        Customer.create_table()
        Product.create_table()
        Sale.create_table()
        SaleItem.create_table()
        
        # Fix sequences for all tables
        refresh_sequence('customers_id_seq', 'customers')
        refresh_sequence('products_id_seq', 'products')
        refresh_sequence('sales_id_seq', 'sales')
        refresh_sequence('sale_items_id_seq', 'sale_items')
        
        st.success("Database tables initialized successfully!")
    except Exception as e:
        st.error(f"Error initializing tables: {e}")

# App title and sidebar
st.set_page_config(page_title="Smart Inventory and Billing System", layout="wide")
st.title("🏪 Smart Inventory and Billing System")

# Initialize tables on first run
if 'tables_initialized' not in st.session_state:
    initialize_tables()
    st.session_state.tables_initialized = True

# Sidebar navigation
st.sidebar.header("Navigation")
menu_option = st.sidebar.radio(
    "Choose section:",
    ["Dashboard", "Customer Management", "Product Management", "Sales Management", "Analytics & Reports"]
)

# Dashboard
if menu_option == "Dashboard":
    st.header("📊 Dashboard")
    st.write("Welcome to the Smart Inventory and Billing System!")
    st.write("Use the navigation menu to manage customers, products, and sales.")
    
    # Show some statistics
    try:
        # Count customers
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) FROM customers')
        customer_count = cur.fetchone()[0]
        
        # Count products
        cur.execute('SELECT COUNT(*) FROM products')
        product_count = cur.fetchone()[0]

        # Product stock value
        cur.execute('SELECT COALESCE(SUM(price * quantity), 0) FROM products')
        inventory_value = cur.fetchone()[0]
        
        # Count sales
        cur.execute('SELECT COUNT(*) FROM sales')
        sales_count = cur.fetchone()[0]

        # Revenue from completed/created sales
        cur.execute('SELECT COALESCE(SUM(total_amount), 0) FROM sales')
        total_revenue = cur.fetchone()[0]
        
        cur.close()
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Customers", customer_count)
        col2.metric("Total Products", product_count)
        col3.metric("Total Sales", sales_count)
        col4.metric("Total Revenue", format_currency(total_revenue))

        st.metric("Inventory Value", format_currency(inventory_value))
	        
    except Exception as e:
        st.warning("Database statistics not available yet.")

# Customer Management
elif menu_option == "Customer Management":
    st.header("👥 Customer Management")
    
    customer_action = st.radio("Select Action:", ["View All Customers", "Add New Customer", "Update Customer", "Delete Customer"])
    
    if customer_action == "View All Customers":
        st.subheader("All Customers")
        try:
            customers = Customer.get_all_customers()
            if customers:
                for customer in customers:
                    st.write(f"ID: {customer[0]}, Name: {customer[1]}, Contact: {customer[2]}")
            else:
                st.info("No customers found.")
        except Exception as e:
            st.error(f"Error retrieving customers: {e}")
    
    elif customer_action == "Add New Customer":
        st.subheader("Add New Customer")
        with st.form("add_customer_form"):
            name = st.text_input("Customer Name")
            contact = st.text_input("Contact Information")
            submitted = st.form_submit_button("Add Customer")
            
            if submitted:
                if name and contact:
                    try:
                        Customer.insert_customer(name, contact)
                        st.success(f"Customer '{name}' added successfully!")
                        # Refresh sequence
                        refresh_sequence('customers_id_seq', 'customers')
                    except Exception as e:
                        st.error(f"Error adding customer: {e}")
                else:
                    st.warning("Please fill in all fields.")
    
    elif customer_action == "Update Customer":
        st.subheader("Update Customer")
        try:
            customers = Customer.get_all_customers()
            if customers:
                customer_ids = [customer[0] for customer in customers]
                selected_id = st.selectbox("Select Customer to Update", customer_ids)
                
                if selected_id:
                    # Get current customer data
                    cur = conn.cursor()
                    cur.execute('SELECT * FROM customers WHERE id = %s', (selected_id,))
                    customer = cur.fetchone()
                    cur.close()
                    
                    if customer:
                        with st.form("update_customer_form"):
                            name = st.text_input("Customer Name", value=customer[1])
                            contact = st.text_input("Contact Information", value=customer[2])
                            submitted = st.form_submit_button("Update Customer")
                            
                            if submitted:
                                try:
                                    Customer.update_customer(selected_id, name, contact)
                                    st.success(f"Customer '{name}' updated successfully!")
                                except Exception as e:
                                    st.error(f"Error updating customer: {e}")
            else:
                st.info("No customers available to update.")
        except Exception as e:
            st.error(f"Error retrieving customers: {e}")
    
    elif customer_action == "Delete Customer":
        st.subheader("Delete Customer")
        try:
            customers = Customer.get_all_customers()
            if customers:
                customer_options = {f"{customer[1]} (ID: {customer[0]})": customer[0] for customer in customers}
                selected_customer = st.selectbox("Select Customer to Delete", list(customer_options.keys()))
                
                if st.button("Delete Customer"):
                    if selected_customer:
                        customer_id = customer_options[selected_customer]
                        try:
                            Customer.delete_customer(customer_id)
                            st.success(f"Customer '{selected_customer}' deleted successfully!")
                            # Refresh sequence
                            refresh_sequence('customers_id_seq', 'customers')
                        except Exception as e:
                            st.error(f"Error deleting customer: {e}")
                    else:
                        st.warning("Please select a customer to delete.")
            else:
                st.info("No customers available to delete.")
        except Exception as e:
            st.error(f"Error retrieving customers: {e}")

# Product Management
elif menu_option == "Product Management":
    st.header("📦 Product Management")
    
    product_action = st.radio("Select Action:", ["View All Products", "Add New Product", "Update Product", "Delete Product"])
    
    if product_action == "View All Products":
        st.subheader("All Products")
        try:
            products = Product.view_products()
            if products:
                for product in products:
                    stock_value = float(product[3]) * int(product[4])
                    st.write(f"ID: {product[0]}, Name: {product[1]}, Description: {product[2]}, Price: {format_currency(product[3])}, Quantity: {product[4]}, Stock Value: {format_currency(stock_value)}")
            else:
                st.info("No products found.")
        except Exception as e:
            st.error(f"Error retrieving products: {e}")
    
    elif product_action == "Add New Product":
        st.subheader("Add New Product")
        with st.form("add_product_form"):
            name = st.text_input("Product Name")
            description = st.text_area("Description")
            price = st.number_input("Price (Rs.)", min_value=0.0, value=1.0, step=0.01)
            quantity = st.number_input("Quantity", min_value=1, value=1, step=1)
            submitted = st.form_submit_button("Add Product")
            
            if submitted:
                if name and price > 0 and quantity > 0:
                    try:
                        Product.insert_product(name, description, price, quantity)
                        st.success(f"Product '{name}' added successfully!")
                        # Refresh sequence
                        refresh_sequence('products_id_seq', 'products')
                    except Exception as e:
                        st.error(f"Error adding product: {e}")
                else:
                    st.warning("Please enter product name, price greater than 0, and quantity greater than 0.")
    
    elif product_action == "Update Product":
        st.subheader("Update Product")
        try:
            products = Product.view_products()
            if products:
                product_ids = [product[0] for product in products]
                selected_id = st.selectbox("Select Product to Update", product_ids)
                
                if selected_id:
                    # Get current product data
                    product = Product.view_product_id(selected_id)
                    
                    if product:
                        with st.form("update_product_form"):
                            name = st.text_input("Product Name", value=product[1])
                            description = st.text_area("Description", value=product[2])
                            price = st.number_input("Price (Rs.)", min_value=0.0, step=0.01, value=float(product[3]))
                            quantity = st.number_input("Quantity", min_value=0, step=1, value=int(product[4]))
                            submitted = st.form_submit_button("Update Product")
                            
                            if submitted:
                                try:
                                    Product.update_product(selected_id, name, description, price, quantity)
                                    st.success(f"Product '{name}' updated successfully!")
                                except Exception as e:
                                    st.error(f"Error updating product: {e}")
            else:
                st.info("No products available to update.")
        except Exception as e:
            st.error(f"Error retrieving products: {e}")
    
    elif product_action == "Delete Product":
        st.subheader("Delete Product")
        try:
            products = Product.view_products()
            if products:
                product_options = {f"{product[1]} (ID: {product[0]})": product[0] for product in products}
                selected_product = st.selectbox("Select Product to Delete", list(product_options.keys()))
                
                if st.button("Delete Product"):
                    if selected_product:
                        product_id = product_options[selected_product]
                        try:
                            Product.delete_product(product_id)
                            st.success(f"Product '{selected_product}' deleted successfully!")
                            # Refresh sequence
                            refresh_sequence('products_id_seq', 'products')
                        except Exception as e:
                            st.error(f"Error deleting product: {e}")
                    else:
                        st.warning("Please select a product to delete.")
            else:
                st.info("No products available to delete.")
        except Exception as e:
            st.error(f"Error retrieving products: {e}")

# Sales Management
elif menu_option == "Sales Management":
    st.header("💰 Sales Management")
    
    sales_action = st.radio("Select Action:", ["Create New Sale", "View All Sales", "Generate Bill"])
    
    if sales_action == "Create New Sale":
        st.subheader("Create New Sale")
        
        # Get customers for selection
        try:
            customers = Customer.get_all_customers()
            if customers:
                customer_dict = {f"{customer[1]} (ID: {customer[0]})": customer[0] for customer in customers}
                selected_customer = st.selectbox("Select Customer", list(customer_dict.keys()))
                
                if selected_customer:
                    customer_id = customer_dict[selected_customer]
                    
                    # Create sale form
                    with st.form("create_sale_form"):
                        sale_date = st.date_input("Sale Date", date.today())
                        submitted = st.form_submit_button("Create Sale")
                        
                        if submitted:
                            try:
                                # Insert sale
                                cur = conn.cursor()
                                cur.execute('''INSERT INTO sales (customer_id, date, total_amount)
                                               VALUES (%s, %s, %s) RETURNING id''',
                                            (customer_id, sale_date, 0.0))
                                sale_id = cur.fetchone()[0]
                                conn.commit()
                                cur.close()
                                
                                # Refresh sequence
                                refresh_sequence('sales_id_seq', 'sales')
                                
                                st.success(f"Sale created successfully with ID: {sale_id}")
                                st.session_state.new_sale_id = sale_id
                            except Exception as e:
                                st.error(f"Error creating sale: {e}")
                                
                    # Add items to sale
                    if 'new_sale_id' in st.session_state:
                        st.markdown("---")
                        st.subheader("Add Items to Sale")
                        
                        # Get products for selection
                        products = Product.view_products()
                        if products:
                            product_dict = {f"{product[1]} (ID: {product[0]})": product[0] for product in products}
                            selected_product = st.selectbox("Select Product", list(product_dict.keys()))
                            
                            if selected_product:
                                product_id = product_dict[selected_product]
                                
                                # Get product details for price
                                product_details = Product.view_product_id(product_id)
                                if product_details:
                                    default_price = float(product_details[3])  # price
                                    default_quantity = 1
                                    
                                    with st.form("add_item_form"):
                                        quantity = st.number_input("Quantity", min_value=1, value=default_quantity)
                                        price = st.number_input("Price per Item (Rs.)", min_value=0.0, value=default_price, step=0.01)
                                        submitted_item = st.form_submit_button("Add Item to Sale")
                                        
                                        if submitted_item:
                                            try:
                                                # Add item to sale
                                                cur = conn.cursor()
                                                cur.execute('''INSERT INTO sale_items (sale_id, product_id, quantity, price)
                                                               VALUES (%s, %s, %s, %s)''',
                                                            (st.session_state.new_sale_id, product_id, quantity, price))
                                                conn.commit()
                                                cur.close()
                                                
                                                # Refresh sequence
                                                refresh_sequence('sale_items_id_seq', 'sale_items')
                                                
                                                # Update product quantity
                                                new_quantity = product_details[4] - quantity
                                                Product.update_product(product_id, quantity=new_quantity)

                                                total_amount = update_sale_total(st.session_state.new_sale_id)
                                                
                                                st.success(f"Item added to sale successfully! Sale total: {format_currency(total_amount)}")
                                            except Exception as e:
                                                st.error(f"Error adding item to sale: {e}")
                                            
                                    # Option to finish sale
                                    if st.button("Finish Sale"):
                                        try:
                                            total_amount = update_sale_total(st.session_state.new_sale_id)
                                            
                                            st.success(f"Sale completed! Total amount: {format_currency(total_amount)}")
                                            del st.session_state.new_sale_id
                                        except Exception as e:
                                            st.error(f"Error finalizing sale: {e}")
                        else:
                            st.info("No products available. Please add products first.")
                else:
                    st.info("Please select a customer.")
            else:
                st.info("No customers available. Please add customers first.")
        except Exception as e:
            st.error(f"Error retrieving data: {e}")
    
    elif sales_action == "View All Sales":
        st.subheader("All Sales")
        try:
            cur = conn.cursor()
            cur.execute('''SELECT s.id, c.name, s.date,
                                  COALESCE(STRING_AGG(TRIM(p.name), ', ' ORDER BY TRIM(p.name)), 'No product') AS product_names,
                                  s.total_amount
                          FROM sales s
                          JOIN customers c ON s.customer_id = c.id
                          LEFT JOIN sale_items si ON si.sale_id = s.id
                          LEFT JOIN products p ON p.id = si.product_id
                          GROUP BY s.id, c.name, s.date, s.total_amount
                          ORDER BY s.date DESC, s.id DESC''')
            sales = cur.fetchall()
            cur.close()
            
            if sales:
                sales_df = [{"Sale ID": sale[0], "Customer": sale[1], "Date": str(sale[2]), "Product Name": sale[3], "Amount (Rs.)": format_currency(sale[4])}
                            for sale in sales]
                st.table(sales_df)
            else:
                st.info("No sales found.")
        except Exception as e:
            st.error(f"Error retrieving sales: {e}")
    
    elif sales_action == "Generate Bill":
        st.subheader("Generate Bill")
        try:
            # Get sales for selection
            cur = conn.cursor()
            cur.execute('SELECT id FROM sales ORDER BY id DESC')
            sales = cur.fetchall()
            cur.close()
            
            if sales:
                sale_ids = [sale[0] for sale in sales]
                selected_sale_id = st.selectbox("Select Sale ID", sale_ids)
                
                if st.button("Generate Bill"):
                    try:
                        # Get sale details
                        cur = conn.cursor()
                        cur.execute('''SELECT s.id, c.name, s.date, s.total_amount 
                                      FROM sales s JOIN customers c ON s.customer_id = c.id 
                                      WHERE s.id = %s''', (selected_sale_id,))
                        sale = cur.fetchone()
                        
                        if sale:
                            st.markdown("---")
                            st.subheader("BILL")
                            st.write(f"Sale ID: {sale[0]}")
                            st.write(f"Customer: {sale[1]}")
                            st.write(f"Date: {sale[2]}")
                            st.markdown("---")
                            
                            # Get sale items
                            cur.execute('''SELECT p.name, si.quantity, si.price, (si.quantity * si.price) as total
                                          FROM sale_items si JOIN products p ON si.product_id = p.id
                                          WHERE si.sale_id = %s''', (selected_sale_id,))
                            items = cur.fetchall()
                            
                            if items:
                                for item in items:
                                    st.write(f"{item[0]} - Qty: {item[1]}, Price: {format_currency(item[2])}, Total: {format_currency(item[3])}")
                                
                                st.markdown("---")
                                st.write(f"**TOTAL AMOUNT: {format_currency(sale[3])}**")
                            else:
                                st.info("No items found for this sale.")
                        else:
                            st.warning("Sale not found.")
                        cur.close()
                    except Exception as e:
                        st.error(f"Error generating bill: {e}")
            else:
                st.info("No sales available.")
        except Exception as e:
            st.error(f"Error retrieving sales: {e}")

# Analytics & Reports
elif menu_option == "Analytics & Reports":
    st.header("📈 Analytics & Reports")
    
    analytics_action = st.radio("Select Report:", ["Sales Summary", "Sales by Date Range", "Top Selling Products", "Low Stock Alert", "Customer Purchase History"])
    
    # Sales Summary
    if analytics_action == "Sales Summary":
        st.subheader("Sales Summary")
        try:
            # Get total sales
            cur = conn.cursor()
            cur.execute('SELECT COUNT(*), SUM(total_amount) FROM sales')
            result = cur.fetchone()
            total_sales = result[0] or 0
            total_revenue = result[1] or 0.0

            cur.execute('SELECT COALESCE(SUM(price * quantity), 0) FROM products')
            inventory_value = cur.fetchone()[0]
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Sales", total_sales)
            col2.metric("Total Revenue", format_currency(total_revenue))
            col3.metric("Inventory Value", format_currency(inventory_value))
            
            # Sales by date
            cur.execute('''SELECT date, SUM(total_amount) as daily_total
                          FROM sales 
                          GROUP BY date 
                          ORDER BY date''')
            sales_data = cur.fetchall()
            cur.close()
            
            if sales_data:
                # Prepare data for chart
                dates = [str(row[0]) for row in sales_data]
                amounts = [float(row[1]) for row in sales_data]
                
                # Create bar chart
                st.write("Daily Sales Trend")
                st.line_chart(dict(zip(dates, amounts)))
            else:
                st.info("No sales data available for chart.")
                
        except Exception as e:
            st.error(f"Error generating sales summary: {e}")
    
    # Sales by Date Range
    elif analytics_action == "Sales by Date Range":
        st.subheader("Sales by Date Range")
        try:
            # Date range selector
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Start Date", date.today())
            with col2:
                end_date = st.date_input("End Date", date.today())
            
            if st.button("Get Sales Report"):
                if start_date <= end_date:
                    cur = conn.cursor()
                    cur.execute('''SELECT s.id, c.name, s.date,
                                          COALESCE(STRING_AGG(TRIM(p.name), ', ' ORDER BY TRIM(p.name)), 'No product') AS product_names,
                                          s.total_amount
                                  FROM sales s
                                  JOIN customers c ON s.customer_id = c.id
                                  LEFT JOIN sale_items si ON si.sale_id = s.id
                                  LEFT JOIN products p ON p.id = si.product_id
                                  WHERE s.date BETWEEN %s AND %s
                                  GROUP BY s.id, c.name, s.date, s.total_amount
                                  ORDER BY s.date DESC, s.id DESC''', (start_date, end_date))
                    sales_data = cur.fetchall()
                    cur.close()
                    
                    if sales_data:
                        # Display sales in table
                        st.write(f"Sales from {start_date} to {end_date}:")
                        sales_df = [{"Sale ID": row[0], "Customer": row[1], "Date": str(row[2]), "Product Name": row[3], "Amount (Rs.)": format_currency(row[4])} 
                                   for row in sales_data]
                        st.table(sales_df)
                        
                        # Calculate totals
                        total_sales_count = len(sales_data)
                        total_amount = sum([float(row[4]) for row in sales_data])
                        
                        # Display metrics
                        col1, col2 = st.columns(2)
                        col1.metric("Total Sales", total_sales_count)
                        col2.metric("Total Revenue", format_currency(total_amount))
                    else:
                        st.info("No sales found for the selected date range.")
                else:
                    st.warning("End date must be after start date.")
        except Exception as e:
            st.error(f"Error retrieving sales data: {e}")
    
    # Top Selling Products
    elif analytics_action == "Top Selling Products":
        st.subheader("Top Selling Products")
        try:
            # Get top selling products
            cur = conn.cursor()
            cur.execute('''SELECT p.name, SUM(si.quantity) as total_quantity
                          FROM sale_items si 
                          JOIN products p ON si.product_id = p.id
                          GROUP BY p.name, p.id
                          ORDER BY total_quantity DESC
                          LIMIT 10''')
            top_products = cur.fetchall()
            cur.close()
            
            if top_products:
                for product in top_products:
                    st.write(f"{product[0]}: {product[1]} units sold")
                
                # Create bar chart
                product_names = [row[0] for row in top_products]
                quantities = [int(row[1]) for row in top_products]
                
                st.bar_chart(dict(zip(product_names, quantities)))
            else:
                st.info("No sales data available.")
        except Exception as e:
            st.error(f"Error retrieving top selling products: {e}")
    
    # Low Stock Alert
    elif analytics_action == "Low Stock Alert":
        st.subheader("Low Stock Alert")
        try:
            cur = conn.cursor()
            cur.execute('SELECT name, quantity FROM products WHERE quantity < 10 ORDER BY quantity ASC')
            low_stock = cur.fetchall()
            cur.close()
            
            if low_stock:
                for item in low_stock:
                    st.write(f"{item[0]}: {item[1]} units remaining")
            else:
                st.success("No low stock items. All products are well-stocked!")
        except Exception as e:
            st.error(f"Error retrieving low stock products: {e}")
    
    # Customer Purchase History
    elif analytics_action == "Customer Purchase History":
        st.subheader("Customer Purchase History")
        try:
            customers = Customer.get_all_customers()
            if customers:
                customer_dict = {f"{customer[1]}": customer[0] for customer in customers}
                selected_customer = st.selectbox("Select Customer", list(customer_dict.keys()), key="analytics_customer")
                
                if selected_customer:
                    customer_id = customer_dict[selected_customer]
                    cur = conn.cursor()
                    cur.execute('''SELECT s.id, s.date,
                                          COALESCE(STRING_AGG(TRIM(p.name), ', ' ORDER BY TRIM(p.name)), 'No product') AS product_names,
                                          s.total_amount
                                  FROM sales s
                                  LEFT JOIN sale_items si ON si.sale_id = s.id
                                  LEFT JOIN products p ON p.id = si.product_id
                                  WHERE s.customer_id = %s 
                                  GROUP BY s.id, s.date, s.total_amount
                                  ORDER BY s.date DESC, s.id DESC''', (customer_id,))
                    customer_sales = cur.fetchall()
                    cur.close()
                    
                    if customer_sales:
                        st.table({"Sale ID": [row[0] for row in customer_sales],
                                 "Date": [str(row[1]) for row in customer_sales],
                                 "Product Name": [row[2] for row in customer_sales],
                                 "Amount (Rs.)": [format_currency(row[3]) for row in customer_sales]})
                        
                        # Calculate total purchases
                        total_purchases = sum([float(row[3]) for row in customer_sales])
                        st.metric("Total Purchases by Customer", format_currency(total_purchases))
                    else:
                        st.info("This customer has no purchase history.")
            else:
                st.info("No customers available.")
        except Exception as e:
            st.error(f"Error retrieving customer purchase history: {e}")
