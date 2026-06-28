import mysql.connector
import subprocess
from tkinter import *
from tkinter import messagebox, simpledialog, ttk

# MySQL Database setup
conn = mysql.connector.connect(
      host="localhost",
    user="root",
    password="Shruti@123",
    database="library_db"
)
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS publisher (
        Publisher_ID VARCHAR(10) PRIMARY KEY,
        Name VARCHAR(255),
        Location VARCHAR(255),
        Year_of_Publication INT
    )
''')
conn.commit()

# GUI setup
root = Tk()
root.title("Publisher Management")
root.geometry("800x600")
root.configure(bg="#f9f9f9")

style = ttk.Style()
style.configure("Treeview", font=('Helvetica', 10), rowheight=25)
style.configure("Treeview.Heading", font=('Helvetica', 10, 'bold'))

Label(root, text="Publisher Management", font=("Helvetica", 16, "bold"), bg="#f9f9f9").grid(row=0, column=0, columnspan=2, pady=10)

# Entry fields
labels = ["Publisher ID", "Name", "Location", "Year of Publication"]
entries = {}

for i, label in enumerate(labels):
    Label(root, text=label, font=("Helvetica", 10), bg="#f9f9f9").grid(row=i+1, column=0, sticky=W, padx=10)
    entry = Entry(root, width=30, font=("Helvetica", 10))
    entry.grid(row=i+1, column=1, padx=10, pady=2)
    entries[label] = entry

# Treeview for display
tree = ttk.Treeview(root, columns=labels, show='headings')
for label in labels:
    tree.heading(label, text=label)
tree.grid(row=7, column=0, columnspan=2, padx=10, pady=10)

scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
scrollbar.grid(row=7, column=2, sticky='ns')

# CRUD Functions
def insert_publisher():
    cursor.execute("INSERT INTO publisher (Publisher_ID, Name, Location, Year_of_Publication) VALUES (%s, %s, %s, %s)",
                   tuple(e.get() for e in entries.values()))
    conn.commit()
    messagebox.showinfo("Success", "Publisher added successfully")
    view_publishers()

def view_publishers():
    cursor.execute("SELECT * FROM publisher")
    records = cursor.fetchall()
    tree.delete(*tree.get_children())
    for record in records:
        tree.insert("", END, values=record)

def update_publisher():
    publisher_id = simpledialog.askstring("Input", "Enter Publisher ID to update:")
    cursor.execute('''
        UPDATE publisher SET Name=%s, Location=%s, Year_of_Publication=%s
        WHERE Publisher_ID=%s
    ''', (entries["Name"].get(), entries["Location"].get(),
          entries["Year of Publication"].get(), publisher_id))
    conn.commit()
    messagebox.showinfo("Success", "Publisher record updated")
    view_publishers()

def delete_publisher():
    publisher_id = simpledialog.askstring("Input", "Enter Publisher ID to delete:")
    cursor.execute("DELETE FROM publisher WHERE Publisher_ID=%s", (publisher_id,))
    conn.commit()
    messagebox.showinfo("Success", "Publisher record deleted")
    view_publishers()

# External script buttons
def open_tran():
    subprocess.run(["python", "tran.py"])

def open_staff():
    subprocess.run(["python", "staff.py"])

# Buttons
button_style = {'font': ("Helvetica", 10), 'width': 15, 'bg': '#2e86c1', 'fg': 'white', 'activebackground': '#1b4f72'}
Button(root, text="Insert", command=insert_publisher, **button_style).grid(row=6, column=0, pady=5)
Button(root, text="View", command=view_publishers, **button_style).grid(row=6, column=1, pady=5)
Button(root, text="Update", command=update_publisher, **button_style).grid(row=8, column=0, pady=5)
Button(root, text="Delete", command=delete_publisher, **button_style).grid(row=8, column=1, pady=5)
Button(root, text="Open Tran", command=open_tran, **button_style).grid(row=9, column=0, pady=5)
Button(root, text="Open Staff", command=open_staff, **button_style).grid(row=9, column=1, pady=5)

root.mainloop()
