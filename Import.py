import tkinter as tk
from tkinter import ttk, messagebox
import hashlib
from db_connection import connect_db
from dsb import DashboardApp

class Admin:
    def __init__(self, id_staff, username, password, nama=None, nomor=None):
        self.id_staff = id_staff
        self.username = username
        self.password = password
        self.nama = nama
        self.nomor = nomor

    def hash_password(self):
        return hashlib.sha256(self.password.encode()).hexdigest()

    def login(self):
        conn = connect_db()
        cursor = conn.cursor()
        hashed_password = self.hash_password()
        cursor.execute("SELECT * FROM staff WHERE id_staff = %s AND nama_staff = %s AND password = %s", 
                       (self.id_staff, self.username, hashed_password))
        result = cursor.fetchone()
        conn.close()
        return result

    def signup(self):
        conn = connect_db()
        cursor = conn.cursor()
        hashed_password = self.hash_password()
        cursor.execute("INSERT INTO staff (id_staff, nama_staff, nomor_staff, password) VALUES (%s, %s, %s, %s)", 
                       (self.id_staff, self.nama, self.nomor, hashed_password))
        conn.commit()
        conn.close()


class AdminLoginGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Login Admin")
        self.root.geometry("300x300")
        self.setup_widgets()

    def setup_widgets(self):
        ttk.Label(self.root, text="ID Staff:").pack(pady=5)
        self.entry_id = ttk.Entry(self.root)
        self.entry_id.pack(pady=5)

        ttk.Label(self.root, text="Username:").pack(pady=5)
        self.entry_username = ttk.Entry(self.root)
        self.entry_username.pack(pady=5)

        ttk.Label(self.root, text="Password:").pack(pady=5)
        self.entry_password = ttk.Entry(self.root, show="*")
        self.entry_password.pack(pady=5)

        ttk.Button(self.root, text="Login", command=self.login).pack(pady=5)
        ttk.Button(self.root, text="Sign Up", command=self.open_signup).pack(pady=5)

    def login(self):
        id_staff = self.entry_id.get()
        username = self.entry_username.get()
        password = self.entry_password.get()
        admin = Admin(id_staff, username, password)
        
        if admin.login():
            messagebox.showinfo("Login Berhasil", "Selamat datang, " + username)
            self.root.destroy()
            
            new_root = tk.Tk()
            DashboardApp(new_root, id_staff, username)
            new_root.mainloop()
        else:
            messagebox.showerror("Login Gagal", "ID Staff, Username, atau Password salah")

    def open_signup(self):
        SignupWindow(self.root)


class SignupWindow:
    def __init__(self, root):
        self.signup_window = tk.Toplevel(root)
        self.signup_window.title("Sign Up Admin")
        self.signup_window.geometry("300x300")
        self.setup_widgets()

    def setup_widgets(self):
        ttk.Label(self.signup_window, text="ID Staff:").pack(pady=5)
        self.entry_id = ttk.Entry(self.signup_window)
        self.entry_id.pack(pady=5)

        ttk.Label(self.signup_window, text="Nama Admin:").pack(pady=5)
        self.entry_nama = ttk.Entry(self.signup_window)
        self.entry_nama.pack(pady=5)

        ttk.Label(self.signup_window, text="Nomor Telepon:").pack(pady=5)
        self.entry_nomor = ttk.Entry(self.signup_window)
        self.entry_nomor.pack(pady=5)

        ttk.Label(self.signup_window, text="Password:").pack(pady=5)
        self.entry_password = ttk.Entry(self.signup_window, show="*")
        self.entry_password.pack(pady=5)

        ttk.Button(self.signup_window, text="Sign Up", command=self.signup).pack(pady=10)
    
    def signup(self):
        id_staff = self.entry_id.get()
        nama = self.entry_nama.get()
        nomor = self.entry_nomor.get()
        password = self.entry_password.get()

        if id_staff and nama and nomor and password:
            admin = Admin(id_staff, nama, password, nama, nomor)
            admin.signup()
            messagebox.showinfo("Sign Up Berhasil", "Akun berhasil dibuat, silakan login.")
            self.signup_window.destroy()
        else:
            messagebox.showerror("Error", "Semua field harus diisi.")


if __name__ == '__main__':
    root = tk.Tk()
    login_gui = AdminLoginGUI(root)
    root.mainloop()
