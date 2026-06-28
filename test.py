import mysql.connector
from tkinter import *
from tkinter import messagebox as mb
from tkinter import simpledialog as sd
from datetime import datetime
import re
import subprocess
import tkinter as tk
# MySQL connection setup
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Shruti@123"
)
cursor = db.cursor()

# Create database if not exists
cursor.execute("CREATE DATABASE IF NOT EXISTS library_db")
db.commit()

# Reconnect to use the new DB
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Shruti@123",
    database="library_db"
)
cursor = db.cursor()

# Create tables if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS Books (
    Book_ID VARCHAR(10) PRIMARY KEY,
    Title VARCHAR(255),
    Author VARCHAR(255),
    Status VARCHAR(10),
    Issuer_ID VARCHAR(10)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Readers (
    User_ID VARCHAR(10) PRIMARY KEY,
    Name VARCHAR(255),
    Email VARCHAR(255),
    Address VARCHAR(255),
    Phone VARCHAR(15)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Staff (
    Staff_ID VARCHAR(10) PRIMARY KEY,
    Name VARCHAR(255),
    DOB DATE,
    Join_Year INT,
    Address VARCHAR(255)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Auth (
    Login_ID VARCHAR(10) PRIMARY KEY,
    Password VARCHAR(100),
    Role VARCHAR(20),
    Last_Login DATETIME
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Transactions (
    Reg_No INT AUTO_INCREMENT PRIMARY KEY,
    User_ID VARCHAR(10),
    Book_ID VARCHAR(10),
    Action VARCHAR(20),
    Date DATETIME
)
""")
db.commit()

# ================== GUI Setup ==================

root = Tk()
root.title("Library Management System - MySQL Enhanced")
root.geometry("1100x700")
root.configure(bg="#f0f4f7")
font_title = ("Segoe UI", 16, "bold")
font_label = ("Segoe UI", 11)
font_button = ("Segoe UI", 10, "bold")

# =============== Variables =================
book_id = StringVar()
title = StringVar()
author = StringVar()
status = StringVar(value="Available")
issuer_id = StringVar()

reader_id = StringVar()
reader_name = StringVar()
reader_email = StringVar()
reader_address = StringVar()
reader_phone = StringVar()

search_book_term = StringVar()
search_reader_term = StringVar()

# ============ Helper Functions ==================

def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email) is not None

def is_valid_phone(phone):
    """Validate phone: only digits and length between 7 and 15"""
    pattern = r'^\d{7,15}$'
    return re.match(pattern, phone) is not None

def clear_book_fields():
    book_id.set("")
    title.set("")
    author.set("")
    status.set("Available")
    issuer_id.set("")

def clear_reader_fields():
    reader_id.set("")
    reader_name.set("")
    reader_email.set("")
    reader_address.set("")
    reader_phone.set("")

def log_transaction(user_id, book_id, action):
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO Transactions (User_ID, Book_ID, Action, Date) VALUES (%s, %s, %s, %s)",
                       (user_id, book_id, action, now))
        db.commit()
    except Exception as e:
        print(f"Failed to log transaction: {e}")

# ============ Book Management Functions ==================

def add_book():
    # Validate inputs
    if not book_id.get() or not title.get() or not author.get():
        mb.showerror("Error", "Book ID, Title, and Author fields cannot be empty.")
        return

    if status.get() == "Issued":
        issuer = sd.askstring("Issuer ID", "Enter Issuer (Reader) ID")
        if not issuer:
            mb.showerror("Error", "Issuer ID cannot be empty for issued books.")
            return
        # Check if issuer exists before assigning
        cursor.execute("SELECT COUNT(*) FROM Readers WHERE User_ID=%s", (issuer,))
        if cursor.fetchone()[0] == 0:
            mb.showerror("Error", "Issuer Reader ID does not exist.")
            return
        issuer_id.set(issuer)
    else:
        issuer_id.set("N/A")

    try:
        cursor.execute("INSERT INTO Books VALUES (%s, %s, %s, %s, %s)",
                       (book_id.get(), title.get(), author.get(), status.get(), issuer_id.get()))
        db.commit()
        log_transaction(issuer_id.get(), book_id.get(), f"Added-{status.get()}")
        mb.showinfo("Success", "Book added successfully!")
        clear_book_fields()
        view_books()
    except mysql.connector.IntegrityError:
        mb.showerror("Error", "Book ID already exists!")
    except Exception as e:
        mb.showerror("Error", f"Failed to add book: {e}")

def view_books():
    book_listbox.delete(0, END)
    term = search_book_term.get().strip()
    try:
        if term:
            sql = """SELECT * FROM Books WHERE Book_ID LIKE %s OR Title LIKE %s OR Author LIKE %s"""
            param = (f"%{term}%", f"%{term}%", f"%{term}%")
            cursor.execute(sql, param)
        else:
            cursor.execute("SELECT * FROM Books")
        rows = cursor.fetchall()
        for row in rows:
            # Format row nicely for display
            disp = f"ID: {row[0]} | Title: {row[1]} | Author: {row[2]} | Status: {row[3]} | Issuer ID: {row[4]}"
            book_listbox.insert(END, disp)
    except Exception as e:
        mb.showerror("Error", f"Failed to fetch books: {e}")

def update_book():
    # Validate inputs
    if not book_id.get():
        mb.showerror("Error", "Select a book before updating.")
        return

    if status.get() == "Issued" and (not issuer_id.get() or issuer_id.get() == "N/A"):
        issuer = sd.askstring("Issuer ID", "Enter Issuer (Reader) ID")
        if not issuer:
            mb.showerror("Error", "Issuer ID cannot be empty for issued books.")
            return
        # Validate issuer exists
        cursor.execute("SELECT COUNT(*) FROM Readers WHERE User_ID=%s", (issuer,))
        if cursor.fetchone()[0] == 0:
            mb.showerror("Error", "Issuer Reader ID does not exist.")
            return
        issuer_id.set(issuer)

    if status.get() == "Available":
        issuer_id.set("N/A")

    try:
        cursor.execute("UPDATE Books SET Title=%s, Author=%s, Status=%s, Issuer_ID=%s WHERE Book_ID=%s",
                       (title.get(), author.get(), status.get(), issuer_id.get(), book_id.get()))
        db.commit()
        log_transaction(issuer_id.get(), book_id.get(), f"Updated-{status.get()}")
        mb.showinfo("Updated", "Book updated successfully.")
        clear_book_fields()
        view_books()
    except Exception as e:
        mb.showerror("Error", f"Failed to update book: {e}")

def delete_book():
    if not book_id.get():
        mb.showerror("Error", "Select a book before deleting.")
        return
    if not mb.askyesno("Confirm Delete", "Are you sure you want to delete this book?"):
        return
    try:
        cursor.execute("DELETE FROM Books WHERE Book_ID=%s", (book_id.get(),))
        db.commit()
        mb.showinfo("Deleted", "Book deleted successfully.")
        clear_book_fields()
        view_books()
    except Exception as e:
        mb.showerror("Error", f"Failed to delete book: {e}")

def on_book_select(event):
    selection = book_listbox.curselection()
    if selection:
        selected_text = book_listbox.get(selection)
        # Parse string to get values (since we formatted in a human-readable form)
        try:
            parts = selected_text.split('|')
            book_id_val = parts[0].split(':')[1].strip()
            title_val = parts[1].split(':')[1].strip()
            author_val = parts[2].split(':')[1].strip()
            status_val = parts[3].split(':')[1].strip()
            issuer_val = parts[4].split(':')[1].strip()

            book_id.set(book_id_val)
            title.set(title_val)
            author.set(author_val)
            status.set(status_val)
            issuer_id.set(issuer_val)
        except Exception:
            # Fallback: do nothing if parse fails
            pass

# ============ Reader Management Functions ==================

def add_reader():
    # Validate input fields
    if not reader_id.get() or not reader_name.get() or not reader_email.get():
        mb.showerror("Error", "User ID, Name, and Email fields cannot be empty.")
        return
    if not is_valid_email(reader_email.get()):
        mb.showerror("Error", "Invalid email format.")
        return
    if reader_phone.get() and not is_valid_phone(reader_phone.get()):
        mb.showerror("Error", "Phone number must contain only digits (7 to 15 digits).")
        return

    try:
        cursor.execute("INSERT INTO Readers VALUES (%s, %s, %s, %s, %s)",
                       (reader_id.get(), reader_name.get(), reader_email.get(),
                        reader_address.get(), reader_phone.get()))
        db.commit()
        mb.showinfo("Success", "Reader added successfully.")
        clear_reader_fields()
        view_readers()
    except mysql.connector.IntegrityError:
        mb.showerror("Error", "Reader ID already exists!")
    except Exception as e:
        mb.showerror("Error", f"Failed to add reader: {e}")

def view_readers():
    reader_listbox.delete(0, END)
    term = search_reader_term.get().strip()
    try:
        if term:
            sql = """SELECT * FROM Readers WHERE User_ID LIKE %s OR Name LIKE %s OR Email LIKE %s"""
            param = (f"%{term}%", f"%{term}%", f"%{term}%")
            cursor.execute(sql, param)
        else:
            cursor.execute("SELECT * FROM Readers")
        rows = cursor.fetchall()
        for r in rows:
            disp = f"ID: {r[0]} | Name: {r[1]} | Email: {r[2]} | Address: {r[3]} | Phone: {r[4]}"
            reader_listbox.insert(END, disp)
    except Exception as e:
        mb.showerror("Error", f"Failed to fetch readers: {e}")

def on_reader_select(event):
    selection = reader_listbox.curselection()
    if selection:
        selected_text = reader_listbox.get(selection)
        try:
            parts = selected_text.split('|')
            user_id_val = parts[0].split(':')[1].strip()
            name_val = parts[1].split(':')[1].strip()
            email_val = parts[2].split(':')[1].strip()
            address_val = parts[3].split(':')[1].strip()
            phone_val = parts[4].split(':')[1].strip()

            reader_id.set(user_id_val)
            reader_name.set(name_val)
            reader_email.set(email_val)
            reader_address.set(address_val)
            reader_phone.set(phone_val)
        except Exception:
            pass
def update_reader():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Select Reader", "Please select a reader to update.")
        return

    reader_id = tree.item(selected)['values'][0]  # Assuming ID is in column 0
    new_name = entry_name.get()
    new_email = entry_email.get()

    if not new_name or not new_email:
        messagebox.showwarning("Missing Info", "Please enter both name and email.")
        return

    # Example update logic (replace with your DB or list update)
    for reader in reader_list:
        if reader["id"] == reader_id:
            reader["name"] = new_name
            reader["email"] = new_email
            break

    refresh_tree()
    messagebox.showinfo("Success", "Reader updated successfully.")

def delete_reader():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Select Reader", "Please select a reader to delete.")
        return

    reader_id = tree.item(selected)['values'][0]
    confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this reader?")
    if not confirm:
        return

    # Example delete logic
    global reader_list
    reader_list = [reader for reader in reader_list if reader["id"] != reader_id]

    refresh_tree()
    messagebox.showinfo("Deleted", "Reader deleted successfully.")

# =============== Search Buttons ===================

def search_books():
    view_books()

def search_readers():
    view_readers()

def reset_book_search():
    search_book_term.set("")
    view_books()

def reset_reader_search():
    search_reader_term.set("")
    view_readers()
    

# ==================== GUI Layout ===================

# Frames for organization
frame_books = LabelFrame(root, text="Book Management", font=font_title, bg="#f0f4f7", fg="#333")
frame_books.pack(fill=X, padx=20, pady=10)

frame_readers = LabelFrame(root, text="Reader Management", font=font_title, bg="#f0f4f7", fg="#333")
frame_readers.pack(fill=X, padx=20, pady=10)


# --- Book Management Controls --- #
Label(frame_books, text="Book ID", font=font_label, bg="#f0f4f7").grid(row=0, column=0, padx=5, pady=5, sticky=W)
Entry(frame_books, textvariable=book_id, width=15).grid(row=0, column=1, padx=5, pady=5)

Label(frame_books, text="Title", font=font_label, bg="#f0f4f7").grid(row=1, column=0, padx=5, pady=5, sticky=W)
Entry(frame_books, textvariable=title, width=40).grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky=W)

Label(frame_books, text="Author", font=font_label, bg="#f0f4f7").grid(row=2, column=0, padx=5, pady=5, sticky=W)
Entry(frame_books, textvariable=author, width=40).grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky=W)

Label(frame_books, text="Status", font=font_label, bg="#f0f4f7").grid(row=3, column=0, padx=5, pady=5, sticky=W)
OptionMenu(frame_books, status, "Available", "Issued").grid(row=3, column=1, padx=5, pady=5, sticky=W)

Button(frame_books, text="Add Book", font=font_button, bg="#4caf50", fg="white", command=add_book).grid(row=0, column=4, padx=10, pady=5, sticky=E+W)
Button(frame_books, text="Update Book", font=font_button, bg="#2196f3", fg="white", command=update_book).grid(row=1, column=4, padx=10, pady=5, sticky=E+W)
Button(frame_books, text="Delete Book", font=font_button, bg="#f44336", fg="white", command=delete_book).grid(row=2, column=4, padx=10, pady=5, sticky=E+W)

Label(frame_books, text="Search Books:", font=font_label, bg="#f0f4f7").grid(row=4, column=0, padx=5, pady=10, sticky=W)
Entry(frame_books, textvariable=search_book_term, width=30).grid(row=4, column=1, columnspan=2, padx=5, pady=10, sticky=W)
Button(frame_books, text="Search", font=font_button, command=search_books).grid(row=4, column=3, padx=5, pady=10, sticky=E+W)
Button(frame_books, text="Reset", font=font_button, command=reset_book_search).grid(row=4, column=4, padx=5, pady=10, sticky=E+W)

book_listbox = Listbox(frame_books, width=100, height=10)
book_listbox.grid(row=5, column=0, columnspan=5, padx=5, pady=5)
book_listbox.bind("<<ListboxSelect>>", on_book_select)

# --- Reader Management Controls --- #

Label(frame_readers, text="User ID", font=font_label, bg="#f0f4f7").grid(row=0, column=0, padx=5, pady=5, sticky=W)
Entry(frame_readers, textvariable=reader_id, width=15).grid(row=0, column=1, padx=5, pady=5)

Label(frame_readers, text="Name", font=font_label, bg="#f0f4f7").grid(row=1, column=0, padx=5, pady=5, sticky=W)
Entry(frame_readers, textvariable=reader_name, width=40).grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky=W)

Label(frame_readers, text="Email", font=font_label, bg="#f0f4f7").grid(row=2, column=0, padx=5, pady=5, sticky=W)
Entry(frame_readers, textvariable=reader_email, width=40).grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky=W)

Label(frame_readers, text="Address", font=font_label, bg="#f0f4f7").grid(row=3, column=0, padx=5, pady=5, sticky=W)
Entry(frame_readers, textvariable=reader_address, width=40).grid(row=3, column=1, columnspan=3, padx=5, pady=5, sticky=W)

Label(frame_readers, text="Phone", font=font_label, bg="#f0f4f7").grid(row=4, column=0, padx=5, pady=5, sticky=W)
Entry(frame_readers, textvariable=reader_phone, width=20).grid(row=4, column=1, padx=5, pady=5, sticky=W)

Button(frame_readers, text="Add Reader", font=font_button, bg="#4caf50", fg="white", command=add_reader).grid(row=0, column=4, rowspan=2, padx=10, pady=5, sticky=E+W)
Button(frame_readers, text="Open Transactions", font=font_button, bg="#9c27b0", fg="white",
       command=lambda: subprocess.Popen(["python", "tran.py"])).grid(row=2, column=4, rowspan=2, padx=10, pady=5, sticky=E+W)


Label(frame_readers, text="Search Readers:", font=font_label, bg="#f0f4f7").grid(row=5, column=0, padx=5, pady=10, sticky=W)
Entry(frame_readers, textvariable=search_reader_term, width=30).grid(row=5, column=1, columnspan=2, padx=5, pady=10, sticky=W)
Button(frame_readers, text="Search", font=font_button, command=search_readers).grid(row=5, column=3, padx=5, pady=10, sticky=E+W)
Button(frame_readers, text="Reset", font=font_button, command=reset_reader_search).grid(row=5, column=4, padx=5, pady=10, sticky=E+W)

reader_listbox = Listbox(frame_readers, width=100, height=10)
reader_listbox.grid(row=6, column=0, columnspan=5, padx=5, pady=5)
reader_listbox.bind("<<ListboxSelect>>", on_reader_select)

# Initial Population


view_books()
view_readers()


root.mainloop()

