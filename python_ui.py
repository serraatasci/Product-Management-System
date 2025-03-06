import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import sqlite3
import ctypes
import os

if os.name == "nt":  # Windows
    lib_path = os.path.expanduser("~/Desktop/mylib.dll")
elif os.name == "posix":  # macOS ve Linux
    lib_path = os.path.expanduser("~/Desktop/mylib.dylib") if "darwin" in os.sys.platform else os.path.expanduser("~/Desktop/mylib.so")

#Kütüphane kontrolü
if os.path.exists(lib_path):
    mylib = ctypes.CDLL(lib_path)
    mylib.add_product.argtypes = [
        ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p,
        ctypes.c_int, ctypes.c_float, ctypes.c_char_p,
        ctypes.c_char_p, ctypes.c_char_p
    ]
else:
    messagebox.showerror("Error", f"C Library not found! ({lib_path})")
    mylib = None

# **Veritabanı Bağlantısı**
conn = sqlite3.connect("product_Management.db")
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS products (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               product_name TEXT NOT NULL,
               category TEXT,
               stock INTEGER NOT NULL,
               price REAL NOT NULL,
               entry_date TEXT NOT NULL,
               warehouse TEXT NOT NULL,
               warehouse_id INTEGER NOT NULL)''')
conn.commit()

# **Ana Pencere**
root = tk.Tk()
root.title("Product Management System")
root.geometry("1000x800")

welcome_label = tk.Label(root, text="Welcome! Select the operation that you want to perform.", 
                         padx=1000, pady=50, bg="pink", font=("Arial", 20, "bold"))
welcome_label.pack(pady=30)

frame_table = tk.Frame(root)
frame_table.pack(fill="both", expand=True, padx=10, pady=10)

product_table = ttk.Treeview(frame_table, columns=("id", "name", "category", "stock", "price", "date", "warehouse", "warehouse_id"), show="headings")
product_table.pack(fill="both", expand=True)

columns = [("id", "ID"), ("name", "Product Name"), ("category", "Category"),
           ("stock", "Stock"), ("price", "Price"), ("date", "Entry Date"),
           ("warehouse", "Warehouse"), ("warehouse_id", "Warehouse ID")]

for col, text in columns:
    product_table.heading(col, text=text)
    product_table.column(col, width=120, anchor="center")

categories = ["Electronics", "Clothing", "Furniture", "Books", "Food", "Sports"]

# **Ürün Ekleme Fonksiyonu**
def add_product():
    add_window = tk.Toplevel(root)
    add_window.title("Add Product")
    add_window.geometry("500x500")

    selected_category = tk.StringVar(add_window)
    selected_category.set(categories[0])

    labels = ["Product Name", "Category", "Stock", "Price", "Entry Date (YYYY-MM-DD)", "Warehouse", "Warehouse ID"]
    entries = {}

    for i, label_text in enumerate(labels):
        tk.Label(add_window, text=label_text, font=("Arial", 10, "bold")).grid(row=i, column=0, padx=10, pady=10)

        if label_text == "Category":
            entry = tk.OptionMenu(add_window, selected_category, *categories)
            entry.grid(row=i, column=1, padx=10, pady=10)
            entries[label_text] = selected_category
        else:
            entry = tk.Entry(add_window)
            entry.grid(row=i, column=1, padx=10, pady=10)
            entries[label_text] = entry

    def save_product():
        try:
            values = [
                entries["Product Name"].get(),
                selected_category.get(),
                int(entries["Stock"].get()),
                float(entries["Price"].get()),
                entries["Entry Date (YYYY-MM-DD)"].get(),
                entries["Warehouse"].get(),
                int(entries["Warehouse ID"].get()),
            ]
            cursor.execute("INSERT INTO products (product_name, category, stock, price, entry_date, warehouse, warehouse_id) VALUES (?,?,?,?,?,?,?)", tuple(values))
            conn.commit()
            messagebox.showinfo("Success", "Product added successfully.")
            add_window.destroy()
            list_products()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numerical values for Stock, Price, and Warehouse ID.")

    tk.Button(add_window, text="SAVE", font=("Arial", 11, "bold"), command=save_product, bg="lightgrey", width=15).grid(row=len(labels), column=1, pady=15)

# **Ürün Güncelleme Fonksiyonu**
def update_product():
    update_window = tk.Toplevel(root)
    update_window.title("Update Product")
    update_window.geometry("300x250")

    tk.Label(update_window, text="Product ID:", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=10, pady=10)
    entry_id = tk.Entry(update_window)
    entry_id.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(update_window, text="New Stock:", font=("Arial", 10, "bold")).grid(row=1, column=0, padx=10, pady=10)
    entry_stock = tk.Entry(update_window)
    entry_stock.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(update_window, text="New Price:", font=("Arial", 10, "bold")).grid(row=2, column=0, padx=10, pady=10)
    entry_price = tk.Entry(update_window)
    entry_price.grid(row=2, column=1, padx=10, pady=5)

    def save_update():
        try:
            product_id = int(entry_id.get())
            new_stock = int(entry_stock.get())
            new_price = float(entry_price.get())

            cursor.execute("UPDATE products SET stock = ?, price = ? WHERE id = ?", (new_stock, new_price, product_id))
            conn.commit()
            messagebox.showinfo("Success", "Product updated successfully.")
            update_window.destroy()
            list_products()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numerical values for Stock and Price.")

    tk.Button(update_window, text="SAVE", font=("Arial", 9, "bold"), command=save_update, bg="lightgrey", width=15).grid(row=3, column=1, pady=10)

# **Ürün Silme Fonksiyonu**
def delete_product():
    delete_id = simpledialog.askinteger("Input", "Enter the product ID to delete:")
    
    if delete_id is None:
        return

    # Önce ID'nin var olup olmadığını kontrol edelim
    cursor.execute("SELECT COUNT(*) FROM products WHERE id = ?", (delete_id,))
    result = cursor.fetchone()

    if result[0] == 0:  # Eğer sonuç 0 ise, ürün yok demektir
        messagebox.showerror("Error", f"Product with ID {delete_id} not found!")
        return

    # Eğer ürün varsa, silme işlemini yap
    cursor.execute("DELETE FROM products WHERE id = ?", (delete_id,))
    conn.commit()
    messagebox.showinfo("Success", f"Product with ID {delete_id} deleted successfully!")
    
    list_products()  # Listeyi güncelle


# **Ürün Listeleme Fonksiyonu**
def list_products():
    for row in product_table.get_children():
        product_table.delete(row)
    cursor.execute("SELECT * FROM products")
    for product in cursor.fetchall():
        product_table.insert("", "end", values=product)

# **Buton Çerçevesi ve Butonlar**
button_frame = tk.Frame(root)
button_frame.pack(pady=5)

btn_add = tk.Button(button_frame, text="Add Product", font=("Calibri", 11, "bold"), bg="lightgreen", width=15, command=add_product)
btn_add.grid(row=0, column=0, padx=15, pady=10)  

btn_update = tk.Button(button_frame, text="Update Product", font=("Calibri", 11, "bold"), bg="lightblue", width=15, command=update_product)
btn_update.grid(row=0, column=1, padx=15, pady=10)

btn_delete = tk.Button(button_frame, text="Delete Product", font=("Calibri", 11, "bold"), bg="lightpink", width=15, command=delete_product)
btn_delete.grid(row=0, column=2, padx=15, pady=10)

btn_list = tk.Button(button_frame, text="List Products", font=("Calibri", 11, "bold"), bg="lightyellow", width=15, command=list_products)
btn_list.grid(row=0, column=3, padx=15, pady=10)

# **Başlangıçta Ürünleri Listele**
list_products()

root.mainloop()