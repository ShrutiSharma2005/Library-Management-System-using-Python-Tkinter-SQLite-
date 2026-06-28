import mysql.connector
from tkinter import *
from tkinter import messagebox, simpledialog, ttk
import subprocess

# MySQL Database setup
conn = mysql.connector.connect(
     host="localhost",
    user="root",
    password="Shruti@123",
    database="library_db"
)
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS library_log (
        Reg_No INT AUTO_INCREMENT PRIMARY KEY,
        User_ID VARCHAR(10),
        Book_ID VARCHAR(10),
        Action VARCHAR(10),
        Date DATETIME
    )
''')
conn.commit()

# GUI setup
root = Tk()
root.title("Library Log CRUD")
root.geometry("800x600")
root.configure(bg="#f0f4f7")

style = ttk.Style()
style.configure("Treeview", font=('Helvetica', 10), rowheight=25)
style.configure("Treeview.Heading", font=('Helvetica', 10, 'bold'))

# Title Label
Label(root, text="Library Transaction", font=("Helvetica", 16, "bold"), bg="#f0f4f7").grid(row=0, column=0, columnspan=2, pady=10)

# Labels and Entry widgets
Label(root, text="User ID", font=("Helvetica", 10), bg="#f0f4f7").grid(row=1, column=0, sticky=W, padx=10)
Label(root, text="Book ID", font=("Helvetica", 10), bg="#f0f4f7").grid(row=2, column=0, sticky=W, padx=10)
Label(root, text="Action", font=("Helvetica", 10), bg="#f0f4f7").grid(row=3, column=0, sticky=W, padx=10)
Label(root, text="Date (YYYY-MM-DD HH:MM:SS)", font=("Helvetica", 10), bg="#f0f4f7").grid(row=4, column=0, sticky=W, padx=10)

user_id = Entry(root, width=30, font=("Helvetica", 10))
book_id = Entry(root, width=30, font=("Helvetica", 10))
action = Entry(root, width=30, font=("Helvetica", 10))
date = Entry(root, width=30, font=("Helvetica", 10))

user_id.grid(row=1, column=1, padx=10, pady=2)
book_id.grid(row=2, column=1, padx=10, pady=2)
action.grid(row=3, column=1, padx=10, pady=2)
date.grid(row=4, column=1, padx=10, pady=2)

# Table display setup
tree = ttk.Treeview(root, columns=("Reg_No", "User_ID", "Book_ID", "Action", "Date"), show='headings')
tree.heading("Reg_No", text="Reg_No")
tree.heading("User_ID", text="User_ID")
tree.heading("Book_ID", text="Book_ID")
tree.heading("Action", text="Action")
tree.heading("Date", text="Date")
tree.grid(row=8, column=0, columnspan=2, padx=10, pady=10)

# Add vertical scrollbar to Treeview
scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
scrollbar.grid(row=8, column=2, sticky='ns', pady=10)

# CRUD Functions
def insert_data():
    cursor.execute("INSERT INTO library_log (User_ID, Book_ID, Action, Date) VALUES (%s, %s, %s, %s)",
                   (user_id.get(), book_id.get(), action.get(), date.get()))
    conn.commit()
    messagebox.showinfo("Success", "Record inserted successfully")
    view_data()

def view_data():
    cursor.execute("SELECT * FROM library_log")
    records = cursor.fetchall()
    tree.delete(*tree.get_children())
    for record in records:
        tree.insert("", END, values=record)

def update_data():
    reg_no = simpledialog.askinteger("Input", "Enter Reg_No of record to update:")
    cursor.execute("""
        UPDATE library_log SET User_ID=%s, Book_ID=%s, Action=%s, Date=%s
        WHERE Reg_No=%s
    """, (user_id.get(), book_id.get(), action.get(), date.get(), reg_no))
    conn.commit()
    messagebox.showinfo("Success", "Record updated successfully")
    view_data()

def delete_data():
    reg_no = simpledialog.askinteger("Input", "Enter Reg_No of record to delete:")
    cursor.execute("DELETE FROM library_log WHERE Reg_No=%s", (reg_no,))
    conn.commit()
    messagebox.showinfo("Success", "Record deleted successfully")
    view_data()

def open_staff():
    subprocess.run(["python", "staff.py"])

def open_publisher():
    subprocess.run(["python", "pub.py"])
def open_main():
    subprocess.run(["python", "test.py"])
# Buttons
button_style = {'font': ("Helvetica", 10), 'width': 15, 'bg': '#4caf50', 'fg': 'white', 'activebackground': '#45a049'}
Button(root, text="Insert", command=insert_data, **button_style).grid(row=6, column=0, pady=5)
Button(root, text="View", command=view_data, **button_style).grid(row=6, column=1, pady=5)
Button(root, text="Update", command=update_data, **button_style).grid(row=7, column=0, pady=5)
Button(root, text="Delete", command=delete_data, **button_style).grid(row=7, column=1, pady=5)
Button(root, text="Open Staff", command=open_staff, **button_style).grid(row=9, column=0, pady=10)
Button(root, text="Open Publisher", command=open_publisher, **button_style).grid(row=9, column=1, pady=10)
Button(root, text="Open Dashboard", command=open_main, **button_style).grid(row=9, column=2, pady=10)

root.mainloop()
