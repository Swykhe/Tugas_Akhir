import mysql.connector
from tkinter import messagebox

# Koneksi Database
def connect_db():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            port=3306,
            database='tugas_akhir'
        )
        return conn
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Gagal koneksi: {e}")