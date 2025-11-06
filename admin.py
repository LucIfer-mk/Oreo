import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import mysql.connector

# ---------- DB Connection ----------
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="mkkapri",
        database="oreo"
    )

# Predefined Categories
CATEGORIES = [
    "Phone",
    "Laptop",
    "Tablets",
    "Gaming Console",
    "Earphone",
    "PC Accessory"
]

# Fetch or Create Category ID
def get_category_id(category_name):
    db = connect_db()
    cursor = db.cursor()

    cursor.execute("SELECT category_id FROM category WHERE name=%s", (category_name,))
    row = cursor.fetchone()

    if row:
        db.close()
        return row[0]

    # Create new category
    cursor.execute("INSERT INTO category(name) VALUES(%s)", (category_name,))
    db.commit()
    new_id = cursor.lastrowid

    db.close()
    return new_id



# ---------- ADMIN PANEL ----------
class AdminPanel(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Oreo Admin Panel")
        self.state("zoomed")
        self.config(bg="white")

        # Logo
        try:
            img = Image.open("OREO.png")
            img = img.resize((80, 80))
            self.logo = ImageTk.PhotoImage(img)
        except:
            self.logo = None

        # Header
        header = tk.Frame(self, bg="white")
        header.pack(fill="x", padx=20, pady=10)

        if self.logo:
            tk.Label(header, image=self.logo, bg="white").pack(side="left")

        tk.Label(header, text="Oreo Admin", font=("Arial", 22, "bold"),
                 bg="white").pack(side="left", padx=10)

        tk.Button(header, text="Exit", bg="#8B0000", fg="white",
                  font=("Arial", 12, "bold"), command=self.destroy).pack(side="right")

        # Buttons
        btn_frame = tk.Frame(self, bg="white")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Add Product", bg="green", fg="white",
                  font=("Arial", 12, "bold"), command=self.add_product_window).grid(row=0, column=0, padx=10)

        tk.Button(btn_frame, text="Update Product", bg="#B8860B", fg="white",
                  font=("Arial", 12, "bold"), command=self.update_product_window).grid(row=0, column=1, padx=10)

        tk.Button(btn_frame, text="Delete Product", bg="#8B0000", fg="white",
                  font=("Arial", 12, "bold"), command=self.delete_product_window).grid(row=0, column=2, padx=10)

        # Product Table
        table_frame = tk.Frame(self, bg="white")
        table_frame.pack(fill="both", expand=True, padx=20)

        self.tree = ttk.Treeview(table_frame, columns=("ID", "Name", "Price", "Stock"),
                                 show="headings", height=20)
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Price", text="Price")
        self.tree.heading("Stock", text="Stock")

        self.tree.column("ID", width=60)
        self.tree.column("Name", width=300)
        self.tree.column("Price", width=120)
        self.tree.column("Stock", width=120)

        self.tree.pack(fill="both", pady=10)
        self.load_products()



    # Load Products in Table
    def load_products(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT product_id, name, price, stock FROM product")
        rows = cursor.fetchall()
        db.close()

        for row in rows:
            self.tree.insert("", tk.END, values=row)



    # ---------- ADD PRODUCT ----------
    def add_product_window(self):
        win = tk.Toplevel(self)
        win.title("Add Product")
        win.geometry("450x580")

        tk.Label(win, text="Add Product", font=("Arial", 16, "bold")).pack(pady=10)

        fields = ["Name", "Description", "Price", "Stock", "Image URL"]
        entries = {}

        for f in fields:
            tk.Label(win, text=f).pack()
            e = tk.Entry(win, width=35)
            e.pack(pady=3)
            entries[f] = e

        # Category Radio Buttons
        tk.Label(win, text="Category", font=("Arial", 12, "bold")).pack(pady=10)

        category_var = tk.StringVar(value=CATEGORIES[0])
        for c in CATEGORIES:
            tk.Radiobutton(win, text=c, variable=category_var, value=c).pack(anchor="w")

        def save():
            name, description, price, stock, image_url = [entries[f].get() for f in fields]

            if name == "" or price == "" or stock == "":
                messagebox.showerror("Error", "Name, Price, and Stock are required!")
                return

            category_id = get_category_id(category_var.get())

            db = connect_db()
            cursor = db.cursor()

            cursor.execute("""
                INSERT INTO product (name, description, price, stock, category_id, image_url)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (name, description, price, stock, category_id, image_url))

            db.commit()
            db.close()

            messagebox.showinfo("Success", "Product Added Successfully")
            win.destroy()
            self.load_products()

        tk.Button(win, text="Add Product", bg="green", fg="white",
                  font=("Arial", 12, "bold"), command=save).pack(pady=20)



    # ---------- UPDATE PRODUCT ----------
    def update_product_window(self):
        win = tk.Toplevel(self)
        win.title("Update Product")
        win.geometry("450x580")

        tk.Label(win, text="Enter Product ID to Update").pack(pady=5)
        id_entry = tk.Entry(win, width=30)
        id_entry.pack(pady=5)

        fields = ["Name", "Description", "Price", "Stock", "Image URL"]
        entries = {}

        for f in fields:
            tk.Label(win, text=f).pack()
            e = tk.Entry(win, width=35)
            e.pack(pady=3)
            entries[f] = e

        # Category Radio Buttons
        tk.Label(win, text="Category", font=("Arial", 12, "bold")).pack(pady=10)

        category_var = tk.StringVar(value=CATEGORIES[0])
        for c in CATEGORIES:
            tk.Radiobutton(win, text=c, variable=category_var, value=c).pack(anchor="w")

        def update():
            pid = id_entry.get()
            if pid == "":
                messagebox.showerror("Error", "Product ID Required")
                return

            name, description, price, stock, image_url = [entries[f].get() for f in fields]
            category_id = get_category_id(category_var.get())

            db = connect_db()
            cursor = db.cursor()

            cursor.execute("""
                UPDATE product
                SET name=%s, description=%s, price=%s, stock=%s, category_id=%s, image_url=%s
                WHERE product_id=%s
            """, (name, description, price, stock, category_id, image_url, pid))

            db.commit()
            db.close()

            messagebox.showinfo("Updated", "Product Updated Successfully")
            win.destroy()
            self.load_products()

        tk.Button(win, text="Update Product", bg="#B8860B", fg="white",
                  font=("Arial", 12, "bold"), command=update).pack(pady=20)



    # ---------- DELETE PRODUCT ----------
    def delete_product_window(self):
        win = tk.Toplevel(self)
        win.title("Delete Product")
        win.geometry("300x200")

        tk.Label(win, text="Enter Product ID to Delete").pack(pady=10)
        id_entry = tk.Entry(win, width=20)
        id_entry.pack(pady=10)

        def delete():
            pid = id_entry.get()
            if pid == "":
                messagebox.showerror("Error", "Product ID Required")
                return

            db = connect_db()
            cursor = db.cursor()
            cursor.execute("DELETE FROM product WHERE product_id=%s", (pid,))
            db.commit()
            db.close()

            messagebox.showinfo("Deleted", "Product Deleted Successfully")
            win.destroy()
            self.load_products()

        tk.Button(win, text="Delete", bg="#8B0000", fg="white",
                  font=("Arial", 12, "bold"), command=delete).pack(pady=10)

# Run Panel
if __name__ == "__main__":
    app = AdminPanel()
    app.mainloop()
