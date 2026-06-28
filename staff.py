import mysql.connector
import subprocess
from tkinter import *
from tkinter import messagebox, simpledialog, ttk

# MySQL Database setup
try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Shruti@123",
        database="library_db"
    )
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS staff (
            Staff_ID VARCHAR(10) PRIMARY KEY,
            Name VARCHAR(255),
            DOB DATE,
            Join_Year INT,
            Address VARCHAR(255)
        )
    ''')
    conn.commit()
except mysql.connector.Error as err:
    messagebox.showerror("Database Error", str(err))
    exit()

# GUI setup
root = Tk()
root.title("Staff Management")
root.geometry("850x600")
root.configure(bg="#eaf6f6")

style = ttk.Style()
style.configure("Treeview", font=('Helvetica', 10), rowheight=25)
style.configure("Treeview.Heading", font=('Helvetica', 10, 'bold'))

Label(root, text="Staff Management", font=("Helvetica", 16, "bold"), bg="#eaf6f6").grid(row=0, column=0, columnspan=3, pady=10)

# Entry fields
labels = ["Staff ID", "Name", "DOB (YYYY-MM-DD)", "Join Year", "Address"]
entries = {}

for i, label in enumerate(labels):
    Label(root, text=label, font=("Helvetica", 10), bg="#eaf6f6").grid(row=i+1, column=0, sticky=W, padx=10)
    entry = Entry(root, width=30, font=("Helvetica", 10))
    entry.grid(row=i+1, column=1, padx=10, pady=2)
    entries[label] = entry

# Treeview
tree = ttk.Treeview(root, columns=labels, show='headings')
for label in labels:
    tree.heading(label, text=label)
    tree.column(label, width=120)
tree.grid(row=8, column=0, columnspan=3, padx=10, pady=10)

scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
scrollbar.grid(row=8, column=3, sticky='ns')

# Populate entry fields on row select
def on_row_select(event):
    selected = tree.focus()
    values = tree.item(selected, 'values')
    if values:
        for i, key in enumerate(labels):
            entries[key].delete(0, END)
            entries[key].insert(0, values[i])

tree.bind('<<TreeviewSelect>>', on_row_select)

# Validation
def validate_inputs():
    for label, entry in entries.items():
        if not entry.get().strip():
            messagebox.showwarning("Input Error", f"{label} is required.")
            return False
    return True

# CRUD Functions
def insert_staff():
    if not validate_inputs():
        return
    staff_id = entries["Staff ID"].get().strip()
    try:
        cursor.execute("SELECT * FROM staff WHERE Staff_ID = %s", (staff_id,))
        if cursor.fetchone():
            messagebox.showerror("Error", "Staff ID already exists.")
            return
        cursor.execute("INSERT INTO staff (Staff_ID, Name, DOB, Join_Year, Address) VALUES (%s, %s, %s, %s, %s)",
                       tuple(e.get() for e in entries.values()))
        conn.commit()
        messagebox.showinfo("Success", "Staff added successfully")
        view_staff()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))

def view_staff():
    try:
        cursor.execute("SELECT * FROM staff")
        records = cursor.fetchall()
        tree.delete(*tree.get_children())
        for record in records:
            tree.insert("", END, values=record)
    except mysql.connector.Error as err:
        messagebox.showerror("Error", str(err))

def update_staff():
    if not validate_inputs():
        return
    staff_id = entries["Staff ID"].get().strip()
    try:
        cursor.execute("SELECT * FROM staff WHERE Staff_ID = %s", (staff_id,))
        if not cursor.fetchone():
            messagebox.showerror("Error", "Staff ID not found.")
            return
        cursor.execute('''
            UPDATE staff SET Name=%s, DOB=%s, Join_Year=%s, Address=%s
            WHERE Staff_ID=%s
        ''', (entries["Name"].get(), entries["DOB (YYYY-MM-DD)"].get(),
              entries["Join Year"].get(), entries["Address"].get(), staff_id))
        conn.commit()
        messagebox.showinfo("Success", "Staff record updated")
        view_staff()
    except mysql.connector.Error as err:
        messagebox.showerror("Error", str(err))

def delete_staff():
    staff_id = simpledialog.askstring("Input", "Enter Staff ID to delete:")
    if not staff_id:
        return
    try:
        cursor.execute("SELECT * FROM staff WHERE Staff_ID = %s", (staff_id,))
        if not cursor.fetchone():
            messagebox.showerror("Error", "Staff ID not found.")
            return
        cursor.execute("DELETE FROM staff WHERE Staff_ID=%s", (staff_id,))
        conn.commit()
        messagebox.showinfo("Success", "Staff record deleted")
        view_staff()
    except mysql.connector.Error as err:
        messagebox.showerror("Error", str(err))

# External scripts
def open_tran():
    subprocess.run(["python", "tran.py"])

def open_publisher():
    subprocess.run(["python", "pub.py"])

def open_dash():
    subprocess.run(["python", "test.py"])

# Buttons
button_style = {'font': ("Helvetica", 10), 'width': 15, 'bg': '#00796b', 'fg': 'white', 'activebackground': '#004d40'}

Button(root, text="Insert", command=insert_staff, **button_style).grid(row=6, column=0, pady=5)
Button(root, text="View", command=view_staff, **button_style).grid(row=6, column=1, pady=5)
Button(root, text="Update", command=update_staff, **button_style).grid(row=7, column=0, pady=5)
Button(root, text="Delete", command=delete_staff, **button_style).grid(row=7, column=1, pady=5)

Button(root, text="Open Transaction", command=open_tran, **button_style).grid(row=9, column=0, pady=5)
Button(root, text="Open Publisher", command=open_publisher, **button_style).grid(row=9, column=1, pady=5)
Button(root, text="Open Dashboard", command=open_dash, **button_style).grid(row=9, column=2, pady=5)

# Enable column resize
root.grid_columnconfigure(1, weight=1)

root.mainloop()
