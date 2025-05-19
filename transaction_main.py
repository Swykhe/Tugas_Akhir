import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from db_connection import connect_db

class BaseForm:
    def __init__(self):
        self._conn = connect_db()

    def test_db_connection(self):
        try:
            conn = connect_db()
            if conn.is_connected():
                print("Koneksi database berhasil!")
            else:
                print("Koneksi database gagal.")
        except Exception as e:
            print(f"Error koneksi: {e}")

    def _check_and_reconnect(self):
        if self._conn is None or not self._conn.is_connected():
            self._conn = connect_db()


    def _execute_query(self, query, params=()):
        try:
            with self._conn.cursor() as cursor:
                cursor.execute(query, params)
                if query.lower().startswith("select"):
                    result = cursor.fetchall()  # Pastikan hasil SELECT dibaca
                    print(f"Query Result: {result}")
                    return result
                else:
                    self._conn.commit()  # Commit untuk query selain SELECT
                    return []
        except Exception as e:
            print(f"[QUERY ERROR] {query} | params={params} | error={e}")
            messagebox.showerror("Database Error", str(e))
            return []


    def _fetchone_query(self, query, params=()):
        try:
            with self._conn.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchone()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
            return None

    def _insert_query(self, query, params=()):
        try:
            with self._conn.cursor() as cursor:
                cursor.execute(query, params)
                self._conn.commit()
        except Exception as e:
            messagebox.showerror("Insert Error", str(e))

class TransactionForm(BaseForm):
    def __init__(self, root, id_staff):
        super().__init__()
        self.root = tk.Toplevel(root)
        self.root.title("Form Transaksi Peminjaman Buku")
        self.root.geometry("600x600")

        self._id_staff = id_staff
        self._book_list = []
        self._books_data = {}

        self._build_form()

    def _build_form(self):
        tk.Label(self.root, text="ID Transaksi:").pack(anchor='w')
        self._id_transaksi_entry = tk.Entry(self.root)
        self._id_transaksi_entry.pack(fill='x')

        tk.Label(self.root, text=f"ID Staff (login): {self._id_staff}").pack(anchor='w')

        tk.Label(self.root, text="NIM Mahasiswa:").pack(anchor='w')
        self._nim_combo = ttk.Combobox(self.root)
        self._nim_combo.pack(fill='x')
        self.root.after(100, self._load_mahasiswa_nim)
        self._nim_combo.bind("<<ComboboxSelected>>", self._on_nim_selected)

        tk.Label(self.root, text="Nama Mahasiswa:").pack(anchor='w')
        self._nama_entry = tk.Entry(self.root)
        self._nama_entry.pack(fill='x')

        tk.Label(self.root, text="Nomor Mahasiswa:").pack(anchor='w')
        self._nomor_entry = tk.Entry(self.root)
        self._nomor_entry.pack(fill='x')

        self._tgl_pinjam = datetime.date.today()
        self._tgl_kembali = self._tgl_pinjam + datetime.timedelta(days=2)

        tk.Label(self.root, text=f"Tanggal Pinjam: {self._tgl_pinjam}").pack(anchor='w')
        tk.Label(self.root, text=f"Tanggal Kembali: {self._tgl_kembali}").pack(anchor='w')

        tk.Label(self.root, text="Pilih Buku (multiple):").pack(anchor='w')
        self._books_combo = ttk.Combobox(self.root, state='readonly')
        self._books_combo.pack(fill='x')
        self._load_books()
        

        tk.Button(self.root, text="Tambah Buku", command=self._add_book).pack(pady=5)
        self._book_display = tk.Listbox(self.root)
        self._book_display.pack(fill='x', pady=5)

        tk.Button(self.root, text="Submit Transaksi", command=self.submit).pack(pady=10)

    def _load_mahasiswa_nim(self):
        result = self._execute_query("SELECT NIM FROM mahasiswa")
        if result:
            self._nim_combo['values'] = [row[0] for row in result]  # Menyimpan hanya kolom NIM
        else:
            self._nim_combo['values'] = []

    def _on_nim_selected(self, event):
        nim = self._nim_combo.get()
        if nim:
            row = self._fetchone_query("SELECT Nama_Mahasiswa, Nomor_Mahasiswa FROM mahasiswa WHERE NIM=%s", (nim,))
            if row:
                self._nama_entry.delete(0, tk.END)
                self._nama_entry.insert(0, row[0])
                self._nomor_entry.delete(0, tk.END)
                self._nomor_entry.insert(0, row[1])

    def _load_books(self):
        # Query untuk mengambil buku yang statusnya bukan "Dalam Peminjaman"
        result = self._execute_query("SELECT ID_Buku, Judul_Buku FROM buku WHERE ID_Buku NOT IN (SELECT ID_Buku FROM detail_transaksi WHERE Status = 'Dalam Peminjaman')")
    
        if result:
            self._books_data = {f"{r[0]} - {r[1]}": r[0] for r in result}  # Mapping buku
            self._books_combo['values'] = list(self._books_data.keys())  # Menyimpan daftar buku
        else:
            self._books_combo['values'] = []


    def _add_book(self):
        book = self._books_combo.get()
        if book and book not in self._book_list:
        # Cek apakah buku yang dipilih ada dalam daftar buku yang bisa dipinjam
            if book in self._books_data:
            # Menambahkan buku ke list peminjaman
                self._book_list.append(book)
                self._book_display.insert(tk.END, book)
            
            # Menghapus buku dari combobox (supaya tidak bisa dipilih lagi)
                values = list(self._books_combo['values'])
                values.remove(book)
                self._books_combo['values'] = values
                self._books_combo.set('')  # Reset combobox

    def _generate_id(self, column_name, table_name, prefix):
        result = self._fetchone_query(f"SELECT {column_name} FROM {table_name} ORDER BY {column_name} DESC LIMIT 1")
        if result and result[0].startswith(prefix):
            last_num = int(result[0][len(prefix):])
            return f"{prefix}{last_num + 1:03}"
        return f"{prefix}001"

    def _generate_detail_id(self):
        result = self._fetchone_query("SELECT ID_Detail FROM detail_transaksi ORDER BY ID_Detail DESC LIMIT 1")
        if result:
            try:
                num = int(result[0].split('-')[-1])
                return f"D-{num + 1:02}"
            except:
                return "D-01"
        return "D-01"

    def submit(self):
        id_transaksi = self._generate_id("ID_Transaksi", "transaksi", "TRX")
        print(f"ID Transaksi: {id_transaksi}")
        self._id_transaksi_entry.delete(0, tk.END)
        self._id_transaksi_entry.insert(0, id_transaksi)

        nim = self._nim_combo.get().strip()
        nama = self._nama_entry.get().strip()
        nomor = self._nomor_entry.get().strip()

        if not nim or not nama or not nomor:
            messagebox.showerror("Error", "NIM, Nama, dan Nomor Mahasiswa wajib diisi!")
            return

        existing = self._fetchone_query("SELECT NIM FROM mahasiswa WHERE NIM=%s", (nim,))
        if existing:
            self._insert_query("UPDATE mahasiswa SET Nama_Mahasiswa=%s, Nomor_Mahasiswa=%s WHERE NIM=%s",
                            (nama, nomor, nim))
        else:
            self._insert_query("INSERT INTO mahasiswa (NIM, Nama_Mahasiswa, Nomor_Mahasiswa) VALUES (%s, %s, %s)",
                            (nim, nama, nomor))
            self._nim_combo['values'] = (*self._nim_combo['values'], nim)

        if not self._book_list:
            messagebox.showerror("Error", "Pilih minimal satu buku!")
            return

        self._insert_query("INSERT INTO transaksi (ID_Transaksi, ID_Staff, NIM, TGL_Pinjam, TGL_Kembali) VALUES (%s, %s, %s, %s, %s)",
                       (id_transaksi, self._id_staff, nim, self._tgl_pinjam, self._tgl_kembali))

        for book_str in self._book_list:
            id_detail = self._generate_detail_id()
            id_buku = self._books_data[book_str]
            self._insert_query("INSERT INTO detail_transaksi (ID_Detail, ID_Transaksi, ID_Buku, Status, Akumulasi_Keterlambatan) VALUES (%s, %s, %s, %s, %s)",
                           (id_detail, id_transaksi, id_buku, "Dalam Peminjaman", 0))

        messagebox.showinfo("Sukses", "Transaksi berhasil disimpan!")
        self.root.destroy()



