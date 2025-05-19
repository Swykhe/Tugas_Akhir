import tkinter as tk
from tkinter import messagebox, ttk
from db_connection import connect_db

# Superclass abstrak
class BookOperation:
    def __init__(self, root, title="Operasi Buku", size="400x400"):
        self._root = tk.Toplevel(root)
        self._root.title(title)
        self._root.geometry(size)

        self._conn = connect_db()
        self._cursor = self._conn.cursor()
        self._buku_dict = {}

        self._build_interface()
        self._load_buku()

    def _build_interface(self):
        # Dibuat untuk dioverride di subclass
        raise NotImplementedError("Subclass harus mengimplementasikan _build_interface()")

    def _load_buku(self):
        try:
            self._cursor.execute("SELECT ID_Buku, Judul_Buku FROM buku")
            data = self._cursor.fetchall()
            self._buku_dict = {f"{judul} (ID: {id_})": id_ for id_, judul in data}
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat data buku:\n{e}")

    def execute(self):
        # Polymorphic method - harus dioverride
        raise NotImplementedError("Subclass harus mengimplementasikan method execute()")


class DeleteBookForm(BookOperation):
    def __init__(self, root):
        super().__init__(root, title="Hapus Buku")

    def _build_interface(self):
        tk.Label(self._root, text="Pilih Buku yang ingin dihapus:").pack(pady=10)

        self._buku_list = ttk.Combobox(self._root, state="readonly")
        self._buku_list.pack(pady=5, fill='x', padx=10)

        btn_delete = tk.Button(self._root, text="Hapus Buku", command=self.execute)
        btn_delete.pack(pady=20)

        self._refresh_buku_list()

    def _refresh_buku_list(self):
        self._load_buku()
        if self._buku_dict:
            print("Daftar Buku yang Tersedia:", self._buku_dict)
            self._buku_list['values'] = list(self._buku_dict.keys())
            self._buku_list.set('')
        else:
            messagebox.showwarning("Peringatan!", "Tidak ada buku yang tersedia di database")

    def execute(self):
        selected = self._buku_list.get()
        if not selected:
            messagebox.showwarning("Peringatan", "Pilih buku yang ingin dihapus!")
            return

        id_buku = self._buku_dict.get(selected)
        if not id_buku:
            messagebox.showerror("Error", "ID Buku tidak ditemukan.")
            return

        confirm = messagebox.askyesno("Konfirmasi", f"Yakin ingin menghapus buku:\n{selected}?")
        if confirm:
            try:
                self._cursor.execute("DELETE FROM buku WHERE ID_Buku = %s", (id_buku,))
                self._conn.commit()
                messagebox.showinfo("Sukses", "Buku berhasil dihapus.")
                self._refresh_buku_list()
            except Exception as e:
                self._conn.rollback()
                messagebox.showerror("Error", f"Gagal menghapus buku:\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    DeleteBookForm(root)
    root.mainloop()
