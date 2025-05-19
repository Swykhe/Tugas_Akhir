import tkinter as tk
from tkinter import messagebox
from db_connection import connect_db


# Base class for category logic
class Category:
    def __init__(self, name):
        self._name = name  # Encapsulated attribute

    def get_name(self):
        return self._name

    def get_book_count(self):
        return 0  # To be overridden


# Subclass for real categories (with DB logic)
class SpecificCategory(Category):
    def __init__(self, name, db_connection):
        super().__init__(name)
        self._db = db_connection

    def get_book_count(self):  # Overriding
        cursor = self._db.cursor()
        cursor.execute("SELECT COUNT(*) FROM buku WHERE ID_Kategori = %s", (self._name,))
        result = cursor.fetchone()
        return result[0] if result else 0


# Base GUI class with database connection
class BaseApp(tk.Toplevel):
    def __init__(self, root):
        super().__init__(root)
        self._db = connect_db()
        self._cursor = self._db.cursor()


# Final app GUI for showing categories
class CategoryApp(BaseApp):
    def __init__(self, root):
        super().__init__(root)
        self.title("Kategori Buku")
        self.geometry("300x300")

        self._categories = []
        self._load_categories()

    def _load_categories(self):
        self._cursor.execute("SELECT DISTINCT ID_Kategori FROM buku")
        category_rows = self._cursor.fetchall()

        for row in category_rows:
            cat = SpecificCategory(row[0], self._db)
            self._categories.append(cat)
            button = tk.Button(self, text=cat.get_name(), command=lambda c=cat: self._show_book_count(c))
            button.pack(pady=5)

    def _show_book_count(self, category: Category):  # Polymorphic
        count = category.get_book_count()
        messagebox.showinfo("Jumlah Buku", f"Kategori {category.get_name()} memiliki {count} buku.")


# Untuk menjalankan langsung
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    CategoryApp(root)
    root.mainloop()
