import requests
from bs4 import BeautifulSoup
import mysql.connector

import tkinter as tk
from tkinter import Label, Entry, Button, ttk

# Product class
class Product():
    def __init__(self, name = None, price = None, amazon_url = None):
        self.name = name
        self.price = price
        self.amazon_url = amazon_url

# Define an empty array of Product objects
products = []

# Export array of Product objects to backend database using an SQL INSERT statement
def export_to_database(products):
    cursor.execute("DELETE FROM Products;")
    for product in products:
        query = "INSERT INTO Products (name, price, amazon_url) VALUES (%s, %s, %s)"
        values = (product.name, product.price, product.amazon_url)
        cursor.execute(query, values)

    connection.commit()

    # Close connection to database
    cursor.close()
    connection.close()

# Insertion sort algorithms for sorting the array of Product objects in ascending or descending order
def sort_products_dsc(products):
    for i in range(1, len(products)):
        current_product = products[i]
        j = i - 1
        while j >= 0 and current_product.price > products[j].price:
            products[j + 1] = products[j]
            j -= 1
        products[j + 1] = current_product

    # Update the table UI    
    display_products(products)

def sort_products_asc(products):
    for i in range(1, len(products)):
        current_product = products[i]
        j = i - 1
        while j >= 0 and current_product.price < products[j].price:
            products[j + 1] = products[j]
            j -= 1
        products[j + 1] = current_product

    # Update the table UI
    display_products(products)

# Display the array of Product objects in the table UI
def display_products(products):
    # Print the array of Product objects into the console for testing purposes
    print("<------------------Products------------------>")
    print("")
    for product in products:
        print(f"Product Name: {product.name}")
        print(f"Product Price: £{product.price}")
        print(f"Amazon URL: {product.amazon_url}")
        print("")

    # Refresh and redraw the updated table
    tree.delete(*tree.get_children())
    for product in products:
        name = product.name
        price = product.price
        amazon_url = product.amazon_url

        tree.insert("", "end", values=(name, price, amazon_url))

# Go to the input product page and fetch the name and price data
def fetch_data(product_link):
    # Set headers to mimic a web browser to avoid being blocked
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

    # Send an HTTP GET request to the Amazon URL
    try:
        response = requests.get(product_link, headers=headers)
        # Raise an exception for HTTP errors
        # Returns error if the user input is not a valid web url (user input validation) or if the page cannot be accessed
        response.raise_for_status()
    except requests.RequestException as e:
        product_price_label.config(text=f"Error: {str(e)}")

    # Parse the HTML content of the page using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract product name from page
    product_name = soup.find("span", {"class": "a-size-large product-title-word-break"}).get_text(strip=True)
    # Display product name to user for verification it is the product they intended to log
    product_name_label.config(text=product_name)

    # Extract product price from page
    product_price = soup.find("div", {"class": "a-section a-spacing-none aok-align-center aok-relative"}).find("span", {"class": "aok-offscreen"}).get_text(strip=True)
    # Display product price to user
    product_price_label.config(text=f"Price: {product_price}")
    # Remove £ sign from price
    product_price = product_price.replace('£', '')

    # Instantiate a new product object and add it to the array of objects with this scraped data (price converted to float from string)
    products.append(Product(product_name, float(product_price), product_link))

# Search for the product and add it to the table
def search_product():
    product_link = entry.get()
    fetch_data(product_link)
    
    # Unhide the product name and price labels to display the product logged to the user
    product_name_label.grid(row=2, column=0, columnspan=2, pady=10)
    product_price_label.grid(row=3, column=0, columnspan=2, pady=10)

    display_products(products)

# Establish connection to the database (integration)
connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="webscraper"
    )

# Create Product objects with data from database
# Create cursor object to execute SQL queries
cursor = connection.cursor()
# Execute SELECT query to fetch data from the database
cursor.execute("SELECT name, price, amazon_url FROM products")
# Fetch all rows from the result set
rows = cursor.fetchall()
# Iterate over the rows and create Product objects
for row in rows:
    name, price, amazon_url = row
    products.append(Product(name, price, amazon_url))

# UI
root = tk.Tk()
root.title("Amazon Price Scraper")

# Product link entry field
label = tk.Label(root, text="Enter Product Link:")
label.grid(row=0, column=0, padx=10, pady=10, sticky='w')

entry = tk.Entry(root, width=90)
entry.grid(row=0, column=1, padx=10, pady=10, sticky='e')

search_button = tk.Button(root, text="Search", command=search_product)
search_button.grid(row=1, column=0, columnspan=2, pady=10)

# Labels for the product name and price just entered (not visible until user input)
product_name_label = tk.Label(root, text="Product Name", wraplength=300, bd=2, relief="solid")
product_price_label = tk.Label(root, text="Price", bd=2, relief="solid")

# Display the table of products
tree = ttk.Treeview(root, columns=("Product Name", "Price", "URL"), show="headings")
tree.heading("Product Name", text="Product Name")
tree.heading("Price", text="Price")
tree.heading("URL", text="URL")
tree.column("Product Name", width=500)
tree.column("Price", width=40)
tree.column("URL", width=150)
tree.grid(row=4, column=0, columnspan=2, padx=10, pady=0)

# Add the products stored in the database to the table now that it has been drawn
display_products(products)

# Sort ascending/descending buttons
sort_asc_button = tk.Button(root, text="Sort Ascending", command=lambda: sort_products_asc(products))
sort_asc_button.grid(row=5, column=0, padx=(10, 5), pady=10, sticky='e')

sort_desc_button = tk.Button(root, text="Sort Descending", command=lambda: sort_products_dsc(products))
sort_desc_button.grid(row=5, column=1, padx=(5, 10), pady=10, sticky='w')

# Export to database button
export_to_db_button = tk.Button(root, text="Export to database", command=lambda: export_to_database(products))
export_to_db_button.grid(row=5, column=1, padx=(5, 10), pady=10, sticky='e')

root.mainloop()

# Link to view database contents http://localhost/phpmyadmin/