import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import hashlib

# Koneksi Database
def connect_db():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='tugas_akhir'
        )
        return conn
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Gagal koneksi: {e}")

# Fungsi Hash Password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def login_admin(id_staff, username, password):
    conn = connect_db()
    cursor = conn.cursor()
    hashed_password = hash_password(password)
    cursor.execute("SELECT * FROM staff WHERE id_staff = %s AND nama_staff = %s AND password_staff = %s",
                   (id_staff, username, hashed_password))
    result = cursor.fetchone()
    conn.close()
    return result

def daftar_admin(id_staff, nama, nomor, password):
    conn = connect_db()
    cursor = conn.cursor()
    hashed_password = hash_password(password)
    cursor.execute("INSERT INTO staff (id_staff, nama_staff, nomor_staff, password_staff) VALUES (%s, %s, %s, %s)",
                   (id_staff, nama, nomor, hashed_password))
    conn.commit()
    conn.close()

def login_gui():
    def login():
        id_staff = entry_id.get()
        username = entry_username.get()
        password = entry_password.get()
        if login_admin(id_staff, username, password):
            messagebox.showinfo("Login Berhasil", "Selamat datang, " + username)
            root.destroy()
            root_main = tk.Tk()
            root_main.title("Menu Utama")
            root_main.geometry("300x200")
            ttk.Label(root_main, text="Selamat Datang di Sistem").pack(pady=20)
            root_main.mainloop()
        else:
            messagebox.showerror("Login Gagal", "ID Staff, Username, atau Password salah")

    def open_signup():
        signup_gui()

    root = tk.Tk()
    root.title("Login Admin")
    root.geometry("300x300")

    ttk.Label(root, text="ID Staff:").pack(pady=5)
    entry_id = ttk.Entry(root)
    entry_id.pack(pady=5)

    ttk.Label(root, text="Username:").pack(pady=5)
    entry_username = ttk.Entry(root)
    entry_username.pack(pady=5)

    ttk.Label(root, text="Password:").pack(pady=5)
    entry_password = ttk.Entry(root, show="*")
    entry_password.pack(pady=5)

    ttk.Button(root, text="Login", command=login).pack(pady=5)
    ttk.Button(root, text="Sign Up", command=open_signup).pack(pady=5)

    root.mainloop()

def signup_gui():
    def signup():
        id_staff = entry_id.get()
        nama = entry_nama.get()
        nomor = entry_nomor.get()
        password = entry_password.get()
        if id_staff and nama and nomor and password:
            daftar_admin(id_staff, nama, nomor, password)
            messagebox.showinfo("Sign Up Berhasil", "Akun berhasil dibuat, silakan login.")
            signup_window.destroy()
        else:
            messagebox.showerror("Error", "Semua field harus diisi.")

    signup_window = tk.Toplevel()
    signup_window.title("Sign Up Admin")
    signup_window.geometry("300x300")

    ttk.Label(signup_window, text="ID Staff:").pack(pady=5)
    entry_id = ttk.Entry(signup_window)
    entry_id.pack(pady=5)

    ttk.Label(signup_window, text="Nama Admin:").pack(pady=5)
    entry_nama = ttk.Entry(signup_window)
    entry_nama.pack(pady=5)

    ttk.Label(signup_window, text="Nomor Telepon:").pack(pady=5)
    entry_nomor = ttk.Entry(signup_window)
    entry_nomor.pack(pady=5)

    ttk.Label(signup_window, text="Password:").pack(pady=5)
    entry_password = ttk.Entry(signup_window, show="*")
    entry_password.pack(pady=5)

    ttk.Button(signup_window, text="Sign Up", command=signup).pack(pady=10)

# Bagian yang diperbaiki (penting!)
if __name__ == "__main__":
    login_gui()
