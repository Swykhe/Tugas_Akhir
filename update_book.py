import tkinter as tk
from tkinter import ttk, messagebox
from db_connection import connect_db

class BookFormBase:
    def __init__(self, master, db_connector, title="Form Buku"):
        self._root = tk.Toplevel(master)
        self._root.title(title)
        self._root.geometry("450x550")

        self._conn = db_connector
        self._cursor = self._conn.cursor()
        self._fields = self._init_fields()

        self._build_form()
    
    def _init_fields(self):
        return {
            "Judul Buku": tk.StringVar(),
            "ID Kategori": tk.StringVar(),
            "Jenis Kategori": tk.StringVar(),
            "ID Penulis": tk.StringVar(),
            "Nama Penulis": tk.StringVar(),
            "ID Penerbit": tk.StringVar(),
            "Nama Penerbit": tk.StringVar(),
            "Alamat Penerbit": tk.StringVar(),
            "Telepon Penerbit": tk.StringVar(),
            "Tahun Terbit": tk.StringVar(),
            "Sumber": tk.StringVar()
        }

    def _build_form(self):
        for key in self._fields:
            frame = ttk.Frame(self._root)
            frame.pack(fill=tk.X, padx=20, pady=3)

            ttk.Label(frame, text=key+":", width=20, anchor=tk.W).pack(side=tk.LEFT)

            if key == "Sumber":
                cb = ttk.Combobox(frame, textvariable=self._fields[key], state="readonly")
                cb['values'] = ("Pembelian", "Hibah Mahasiswa")
                cb.pack(side=tk.LEFT, fill=tk.X, expand=True)
            else:
                ttk.Entry(frame, textvariable=self._fields[key]).pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _get_field_values(self):
        return {k: v.get() for k, v in self._fields.items()}


class UpdateBookForm(BookFormBase):
    def __init__(self, root, db_connector):
        self._conn = db_connector
        self._cursor = self._conn.cursor()
        super().__init__(root, db_connector, "Update Buku")

        ttk.Label(self._root, text="Pilih ID Buku:").pack(pady=(10, 0))
        self.__book_id_var = tk.StringVar()
        self.__book_id_combobox = ttk.Combobox(self._root, textvariable=self.__book_id_var, state="readonly")
        self.__book_id_combobox.pack(fill=tk.X, padx=20)
        self.__book_id_combobox.bind("<<ComboboxSelected>>", self.__load_book_data)

        ttk.Button(self._root, text="Refresh Daftar Buku", command=self.__load_book_ids).pack(pady=5)
        ttk.Button(self._root, text="Update Buku", command=self.__update_book).pack(pady=15)

        self.__load_book_ids()

    def __load_book_ids(self):
        try:
            self._cursor.execute("SELECT ID_Buku FROM buku ORDER BY ID_Buku")
            ids = [row[0] for row in self._cursor.fetchall()]
            self.__book_id_combobox['values'] = ids
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat daftar ID Buku:\n{e}")

    def __load_book_data(self, event=None):
        book_id = self.__book_id_var.get()
        if not book_id:
            return
        try:
            self._cursor.execute("""
                SELECT b.Judul_Buku, b.ID_Kategori, k.Jenis_Kategori,
                       b.ID_Penulis, p.Nama_Penulis,
                       b.ID_Penerbit, pb.Nama_Penerbit, pb.Alamat_Penerbit, pb.Telepon_Penerbit,
                       b.Tahun_Terbit, b.Sumber
                FROM buku b
                LEFT JOIN kategori k ON b.ID_Kategori = k.ID_Kategori
                LEFT JOIN penulis p ON b.ID_Penulis = p.ID_Penulis
                LEFT JOIN penerbit pb ON b.ID_Penerbit = pb.ID_Penerbit
                WHERE b.ID_Buku = %s
            """, (book_id,))
            data = self._cursor.fetchone()
            if data:
                for key, val in zip(self._fields, data):
                    self._fields[key].set(val if val is not None else "")
            else:
                messagebox.showinfo("Info", "Data buku tidak ditemukan.")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengambil data buku:\n{e}")

    def __update_book(self):
        book_id = self.__book_id_var.get()
        if not book_id:
            messagebox.showwarning("Peringatan", "Pilih ID Buku terlebih dahulu.")
            return

        data = self._get_field_values()

        if not all(data.values()):
            messagebox.showwarning("Peringatan", "Semua field harus diisi.")
            return

        try:
            self._cursor.execute("INSERT INTO kategori (ID_Kategori, Jenis_Kategori) VALUES (%s, %s) ON DUPLICATE KEY UPDATE Jenis_Kategori=%s",
                                 (data["ID Kategori"], data["Jenis Kategori"], data["Jenis Kategori"]))

            self._cursor.execute("INSERT INTO penulis (ID_Penulis, Nama_Penulis) VALUES (%s, %s) ON DUPLICATE KEY UPDATE Nama_Penulis=%s",
                                 (data["ID Penulis"], data["Nama Penulis"], data["Nama Penulis"]))

            self._cursor.execute("""INSERT INTO penerbit (ID_Penerbit, Nama_Penerbit, Alamat_Penerbit, Telepon_Penerbit) 
                                    VALUES (%s, %s, %s, %s) 
                                    ON DUPLICATE KEY UPDATE Nama_Penerbit=%s, Alamat_Penerbit=%s, Telepon_Penerbit=%s""",
                                 (data["ID Penerbit"], data["Nama Penerbit"], data["Alamat Penerbit"], data["Telepon Penerbit"],
                                  data["Nama Penerbit"], data["Alamat Penerbit"], data["Telepon Penerbit"]))

            self._cursor.execute("""UPDATE buku SET Judul_Buku=%s, ID_Kategori=%s, ID_Penulis=%s, ID_Penerbit=%s,
                                    Tahun_Terbit=%s, Sumber=%s WHERE ID_Buku=%s""",
                                 (data["Judul Buku"], data["ID Kategori"], data["ID Penulis"], data["ID Penerbit"],
                                  data["Tahun Terbit"], data["Sumber"], book_id))

            self._conn.commit()
            messagebox.showinfo("Sukses", "Data buku berhasil diupdate.")
        except Exception as e:
            self._conn.rollback()
            messagebox.showerror("Error", f"Gagal update data buku:\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = UpdateBookForm(root)
    root.mainloop()
