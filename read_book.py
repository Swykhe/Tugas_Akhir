import tkinter as tk
from tkinter import ttk, messagebox
from db_connection import connect_db

# === BASE FORM (INHERITANCE) ===
class BaseForm(tk.Toplevel):
    def __init__(self, master, db: connect_db, title="Form"):
        super().__init__(master)
        self.conn = db
        self.cursor = db.cursor()
        self.title(title)
        self.geometry("750x500")

# === READ BOOK FORM (INHERITANCE, POLYMORPHISM, OVERRIDING) ===
class ReadBookForm(BaseForm):
    def __init__(self, master, db_connector: connect_db):
        super().__init__(master, db_connector, "Lihat Daftar Buku")
        self.build_ui()
        self.load_books()

    def build_ui(self):
        self.left_frame = ttk.Frame(self)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        ttk.Label(self.left_frame, text="Daftar Buku:").pack(anchor=tk.W)

        self.listbox = tk.Listbox(self.left_frame, width=40, height=25)
        self.listbox.pack(side=tk.LEFT, fill=tk.Y)

        self.scrollbar = ttk.Scrollbar(self.left_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=self.scrollbar.set)

        self.listbox.bind("<<ListboxSelect>>", self.show_detail)

        self.right_frame = ttk.Frame(self)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(self.right_frame, text="Detail Buku:", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0,10))

        self.detail_entries = {}
        self.fields = [
            "ID Buku", "Judul Buku", "ID Kategori", "Jenis Kategori",
            "ID Penulis", "Nama Penulis", "ID Penerbit", "Nama Penerbit",
            "Alamat Penerbit", "Telepon Penerbit", "Tahun Terbit", "Sumber"
        ]

        for field in self.fields:
            frame = ttk.Frame(self.right_frame)
            frame.pack(fill=tk.X, pady=3)

            lbl = ttk.Label(frame, text=field + ":", width=20, anchor=tk.W)
            lbl.pack(side=tk.LEFT)

            entry = ttk.Entry(frame, state="readonly")
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

            self.detail_entries[field] = entry

    # === POLYMORPHISM: load_books() bisa diubah di child lain ===
    def load_books(self):
        try:
            self.cursor.execute("SELECT ID_Buku, Judul_Buku FROM buku ORDER BY Judul_Buku ASC")
            self._book_list = self.cursor.fetchall()
            self.listbox.delete(0, tk.END)
            for book in self._book_list:
                self.listbox.insert(tk.END, f"{book[1]}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengambil data buku:\n{e}")

    # === OVERRIDING base logic untuk tampilkan detail ===
    def show_detail(self, event):
        selected_index = self.listbox.curselection()
        if not selected_index:
            return
        book_id = self._book_list[selected_index[0]][0]

        try:
            query = """
                SELECT 
                    b.ID_Buku, b.Judul_Buku, 
                    b.ID_Kategori, k.Jenis_Kategori,
                    b.ID_Penulis, p.Nama_Penulis,
                    b.ID_Penerbit, pb.Nama_Penerbit, pb.Alamat_Penerbit, pb.Telepon_Penerbit,
                    b.Tahun_Terbit, b.Sumber
                FROM buku b
                LEFT JOIN kategori k ON b.ID_Kategori = k.ID_Kategori
                LEFT JOIN penulis p ON b.ID_Penulis = p.ID_Penulis
                LEFT JOIN penerbit pb ON b.ID_Penerbit = pb.ID_Penerbit
                WHERE b.ID_Buku = %s
            """
            self.cursor.execute(query, (book_id,))
            data = self.cursor.fetchone()

            if data:
                for key, value in zip(self.fields, data):
                    self.set_entry_text(self.detail_entries[key], value if value is not None else "-")
            else:
                for key in self.fields:
                    self.set_entry_text(self.detail_entries[key], "-")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengambil detail buku:\n{e}")

    def set_entry_text(self, entry, text):
        entry.config(state="normal")
        entry.delete(0, tk.END)
        entry.insert(0, text)
        entry.config(state="readonly")


# === TESTING MAIN ===
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    db = connect_db()
    ReadBookForm(root, db)
    root.mainloop()
