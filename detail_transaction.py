import tkinter as tk
from tkinter import ttk, messagebox
from db_connection import connect_db


class BaseForm:
    def __init__(self):
        self._conn = connect_db()
        self._cursor = self._conn.cursor()

    def fetchall(self, query, params=()):
        self._cursor.execute(query, params)
        return self._cursor.fetchall()

    def execute(self, query, params=()):
        self._cursor.execute(query, params)

    def commit(self):
        self._conn.commit()


class DetailTransactionForm(BaseForm):
    def __init__(self, root, id_transaksi):
        super().__init__()
        self._root = tk.Toplevel(root)
        self._root.title("Semua Detail Transaksi")
        self._id_transaksi = id_transaksi if id_transaksi else "TRX001"
        self._selected_detail = None
        self._detail_data = []

        self._build_widgets()
        self._load_transaksi()

    def _build_widgets(self):
        tk.Label(self._root, text="Pilih ID Transaksi:").pack(anchor='w')

        self._transaksi_listbox = tk.Listbox(self._root, height=10)
        self._transaksi_listbox.pack(fill='both', expand=True)
        self._transaksi_listbox.bind("<<ListboxSelect>>", self._on_select_transaksi)

        self._detail_frame = tk.Frame(self._root)
        self._detail_frame.pack(fill='both', expand=True, pady=10)

        self._detail_listbox = tk.Listbox(self._detail_frame, height=10)
        self._detail_listbox.pack(fill='both', expand=True)
        self._detail_listbox.bind("<<ListboxSelect>>", self._on_select_detail)

        self._status_frame = tk.Frame(self._root)
        self._status_frame.pack(fill='x', pady=10)

        tk.Label(self._status_frame, text="Ubah Status:").pack(side='left')
        self._status_var = tk.StringVar()
        self._status_combo = ttk.Combobox(self._status_frame, textvariable=self._status_var, state='readonly')
        self._status_combo['values'] = ['Dalam Peminjaman', 'Sudah Dikembalikan']
        self._status_combo.pack(side='left')

        self._update_btn = tk.Button(self._status_frame, text="Update Status", command=self.update_status, state='disabled')
        self._update_btn.pack(side='left', padx=5)

    def _load_transaksi(self):
        transaksi_rows = self.fetchall("SELECT DISTINCT ID_Transaksi FROM detail_transaksi ORDER BY ID_Transaksi")
        self._transaksi_listbox.delete(0, tk.END)
        for row in transaksi_rows:
            self._transaksi_listbox.insert(tk.END, row[0])

    def _on_select_transaksi(self, event):
        selected_idx = self._transaksi_listbox.curselection()
        if not selected_idx:
            return
        id_transaksi = self._transaksi_listbox.get(selected_idx[0])
        self.load_detail_transaksi(id_transaksi)

    def load_detail_transaksi(self, id_transaksi):  # Bisa di-override
        rows = self.fetchall(
            "SELECT ID_Detail, Nama_Mahasiswa, Judul_Buku, Status, Akumulasi_Keterlambatan FROM v_detail_transaksi WHERE ID_Transaksi = %s",
            (id_transaksi,)
        )

        self._detail_listbox.delete(0, tk.END)
        self._detail_data = []

        for row in rows:
            self._detail_listbox.insert(tk.END, f"{row[0]} - {row[1]} - {row[2]} | Status: {row[3]} | Keterlambatan: {row[4]}")
            self._detail_data.append(row)

    def _on_select_detail(self, event):
        selected_idx = self._detail_listbox.curselection()
        if not selected_idx:
            self._update_btn.config(state='disabled')
            return

        id_detail, _, _, status, _ = self._detail_data[selected_idx[0]]
        self._selected_detail = id_detail

        self._status_combo.set(status)
        if status == "Terlambat":
            self._status_combo.config(state='disabled')
            self._update_btn.config(state='disabled')
        else:
            self._status_combo.config(state='readonly')
            self._update_btn.config(state='normal')

    def update_status(self):  # Bisa di-override
        if not self._selected_detail:
            messagebox.showwarning("Peringatan", "Pilih detail transaksi dahulu.")
            return

        new_status = self._status_var.get()
        try:
            self.execute("UPDATE detail_transaksi SET Status = %s WHERE ID_Detail = %s", (new_status, self._selected_detail))
            self.commit()
            messagebox.showinfo("Sukses", "Status berhasil diupdate.")
            selected_transaksi = self._transaksi_listbox.get(self._transaksi_listbox.curselection())
            self.load_detail_transaksi(selected_transaksi)
        except Exception as e:
            messagebox.showerror("Error", f"Gagal update status: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    DetailTransactionForm(root)
    root.mainloop()
