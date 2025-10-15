import sqlite3

def create_database():
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            category TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database created successfully!")

def add_product(name, price, quantity, category):

    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM products WHERE name = ?', (name,))
    existing = cursor.fetchone()
    
    if existing:
        print(f"Product '{name}' already exists in the database!")
        conn.close()
        return False
    
    cursor.execute('''
        INSERT INTO products (name, price, quantity, category)
        VALUES (?, ?, ?, ?)
    ''', (name, price, quantity, category))
    
    conn.commit()
    conn.close()
    print(f"Product '{name}' added successfully!")
    return True

def view_all_products():

    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    
    if not products:
        print("\nNo products found.")
    else:
        print("\n" + "="*75)
        print(f"{'ID':<5} {'Name':<25} {'Price':<10} {'Quantity':<10} {'Category'}")
        print("="*75)
        for product in products:
            print(f"{product[0]:<5} {product[1]:<25} ${product[2]:<9.2f} {product[3]:<10} {product[4]}")
        print("="*75)
    
    conn.close()

def search_products(keyword):

    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM products 
        WHERE name LIKE ? OR category LIKE ?
    ''', (f'%{keyword}%', f'%{keyword}%'))
    
    products = cursor.fetchall()
    
    if not products:
        print(f"\nNo products found matching '{keyword}'")
    else:
        print(f"\nSearch results for '{keyword}':")
        print("="*75)
        print(f"{'ID':<5} {'Name':<25} {'Price':<10} {'Quantity':<10} {'Category'}")
        print("="*75)
        for product in products:
            print(f"{product[0]:<5} {product[1]:<25} ${product[2]:<9.2f} {product[3]:<10} {product[4]}")
        print("="*75)
    
    conn.close()

def update_product(product_id, name, price, quantity, category):
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id FROM products WHERE name = ? AND id != ?', (name, product_id))
    existing = cursor.fetchone()
    
    if existing:
        print(f"Product name '{name}' already exists! Please choose a different name.")
        conn.close()
        return False
    
    cursor.execute('''
        UPDATE products 
        SET name = ?, price = ?, quantity = ?, category = ?
        WHERE id = ?
    ''', (name, price, quantity, category, product_id))
    
    if cursor.rowcount > 0:
        print(f"Product ID {product_id} updated successfully!")
    else:
        print(f"No product found with ID {product_id}")
    
    conn.commit()
    conn.close()
    return True

def delete_product(product_id):

    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
    
    if cursor.rowcount > 0:
        print(f"Product ID {product_id} deleted successfully!")
        

        cursor.execute('SELECT id, name, price, quantity, category FROM products WHERE id > ? ORDER BY id', (product_id,))
        products_to_update = cursor.fetchall()
        

        for product in products_to_update:
            old_id = product[0]
            new_id = old_id - 1
            cursor.execute('''
                UPDATE products 
                SET id = ?
                WHERE id = ?
            ''', (new_id, old_id))
        
        cursor.execute('SELECT MAX(id) FROM products')
        max_id = cursor.fetchone()[0]
        
        if max_id is None:
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='products'")
            print("ID counter has been reset.")
        else:
            cursor.execute("UPDATE sqlite_sequence SET seq = ? WHERE name='products'", (max_id,))
        
        print("All IDs reorganized successfully!")
    else:
        print(f"No product found with ID {product_id}")
    
    conn.commit()
    conn.close()

def main_menu():
    create_database()
    
    while True:
        print("\n--- Product Database Menu ---")
        print("1. Add Product")
        print("2. View All Products")
        print("3. Search Products")
        print("4. Update Product")
        print("5. Delete Product")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ")
        
        if choice == '1':
            name = input("Enter product name: ")
            price = float(input("Enter price: "))
            quantity = int(input("Enter quantity: "))
            category = input("Enter category: ")
            add_product(name, price, quantity, category)
            
        elif choice == '2':
            view_all_products()
            
        elif choice == '3':
            keyword = input("Enter search keyword: ")
            search_products(keyword)
            
        elif choice == '4':
            product_id = int(input("Enter product ID to update: "))
            name = input("Enter new product name: ")
            price = float(input("Enter new price: "))
            quantity = int(input("Enter new quantity: "))
            category = input("Enter new category: ")
            update_product(product_id, name, price, quantity, category)
            
        elif choice == '5':
            product_id = int(input("Enter product ID to delete: "))
            delete_product(product_id)
            
        elif choice == '6':
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice. Please try again.")

main_menu()
