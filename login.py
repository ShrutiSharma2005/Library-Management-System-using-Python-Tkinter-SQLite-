import tkinter as tk
from tkinter import messagebox
import mysql.connector
import hashlib
import subprocess

# Database connection
def connect_db():
    return mysql.connector.connect(
        host="localhost",
    user="root",
    password="Shruti@123",
    database="library_db"
    )

# Hash password using SHA-256
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Register a librarian
def register():
    username = entry_user.get()
    password = entry_pass.get()

    if not username or not password:
        messagebox.showwarning("Input Error", "Username and password are required.")
        return

    hashed_password = hash_password(password)

    try:
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO librarians (username, password) VALUES (%s, %s)", (username, hashed_password))
        db.commit()
        messagebox.showinfo("Success", "Librarian registered successfully.")
    except mysql.connector.IntegrityError:
        messagebox.showerror("Error", "Username already exists.")
    finally:
        db.close()

# Login librarian
def login():
    username = entry_user.get()
    password = entry_pass.get()

    if not username or not password:
        messagebox.showwarning("Input Error", "Username and password are required.")
        return

    hashed_password = hash_password(password)

    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT password FROM librarians WHERE username = %s", (username,))
    result = cursor.fetchone()
    db.close()

    if result and hashed_password == result[0]:
        messagebox.showinfo("Login Success", f"Welcome, {username}!")
        root.destroy()  # Close login window
        subprocess.run(["python", "test.py"])  # Adjust path if test.py is in another folder
    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")

# GUI setup
root = tk.Tk()
root.title("Librarian Login")
root.geometry("300x200")

tk.Label(root, text="Username").pack(pady=5)
entry_user = tk.Entry(root)
entry_user.pack()

tk.Label(root, text="Password").pack(pady=5)
entry_pass = tk.Entry(root, show="*")
entry_pass.pack()

tk.Button(root, text="Login", command=login).pack(pady=5)
tk.Button(root, text="Register", command=register).pack()

root.mainloop()
