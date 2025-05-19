import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from db_connection import connect_db

# === BASE FORM CLASS (FOR REUSE / INHERITANCE) ===
class BaseForm(tk.Toplevel):
    def __init__(self, master, db_connection): 
        super().__init__(master)
        self.conn = db_connection
        self.cursor = self.conn.cursor()
        self.geometry("450x600")

# === MAIN FORM WITH INHERITANCE, OVERRIDING, POLYMORPHISM ===
class AddBookForm(BaseForm):
    def __init__(self, master, db_connector):
        super().__init__(master, db_connector)
        self.title("Tambah Buku")
        self.build_form()
        self.load_existing_data()

    def build_form(self):
        self.cursor = self.conn.cursor()
        self.entries = {}

        def add_field(label, key, is_combobox=False, values=None):
            tk.Label(self, text=label).pack()
            if is_combobox:
                cb = ttk.Combobox(self, values=values or [], state="readonly")
                cb.pack()
                self.entries[key] = cb
            else:
                entry = tk.Entry(self)
                entry.pack()
                self.entries[key] = entry

        # Buku
        add_field("ID Buku", "id_buku")
        add_field("Judul Buku", "judul")

        add_field("ID Kategori", "id_kategori", True)
        self.entries["id_kategori"].bind("<<ComboboxSelected>>", self.fill_kategori)
        add_field("Jenis Kategori", "jenis_kategori")

        add_field("ID Penulis", "id_penulis", True)
        self.entries["id_penulis"].bind("<<ComboboxSelected>>", self.fill_penulis)
        add_field("Nama Penulis", "nama_penulis")

        add_field("ID Penerbit", "id_penerbit", True)
        self.entries["id_penerbit"].bind("<<ComboboxSelected>>", self.fill_penerbit)
        add_field("Nama Penerbit", "nama_penerbit")
        add_field("Alamat Penerbit", "alamat_penerbit")
        add_field("Telepon Penerbit", "telepon_penerbit")

        add_field("Tahun Terbit", "tahun")
        add_field("Sumber", "sumber", True, ["Pembelian", "Hibah Mahasiswa"])
        self.entries["sumber"].current(0)

        tk.Button(self, text="Submit", command=self.submit).pack(pady=10)

    def load_existing_data(self):
        def load_and_set(combo, query):
            self.cursor.execute(query)
            items = [row[0] for row in self.cursor.fetchall()]
            items.append("Tambah Baru...")
            combo['values'] = items

        load_and_set(self.entries["id_kategori"], "SELECT ID_Kategori FROM kategori")
        load_and_set(self.entries["id_penulis"], "SELECT ID_Penulis FROM penulis")
        load_and_set(self.entries["id_penerbit"], "SELECT ID_Penerbit FROM penerbit")

    # === POLYMORPHISM (method overloading simulation by conditional branching) ===
    def fill_kategori(self, event):
        id_kategori = self.entries["id_kategori"].get()
        if id_kategori == "Tambah Baru...":
            new_id = simpledialog.askstring("ID Kategori Baru", "Masukkan ID Kategori Baru:")
            new_jenis = simpledialog.askstring("Jenis Kategori Baru", "Masukkan Jenis Kategori Baru:")
            if new_id and new_jenis:
                current_values = list(self.entries["id_kategori"]["values"][:-1]) + [new_id, "Tambah Baru..."]
                self.entries["id_kategori"]["values"] = current_values
                self.entries["id_kategori"].set(new_id)
                self.entries["jenis_kategori"].delete(0, tk.END)
                self.entries["jenis_kategori"].insert(0, new_jenis)
        else:
            self.cursor.execute("SELECT Jenis_Kategori FROM kategori WHERE ID_Kategori=%s", (id_kategori,))
            row = self.cursor.fetchone()
            if row:
                self.entries["jenis_kategori"].delete(0, tk.END)
                self.entries["jenis_kategori"].insert(0, row[0])

    def fill_penulis(self, event):
        id_penulis = self.entries["id_penulis"].get()
        if id_penulis == "Tambah Baru...":
            new_id = simpledialog.askstring("ID Penulis Baru", "Masukkan ID Penulis Baru:")
            new_nama = simpledialog.askstring("Nama Penulis Baru", "Masukkan Nama Penulis Baru:")
            if new_id and new_nama:
                current_values = list(self.entries["id_penulis"]["values"][:-1]) + [new_id, "Tambah Baru..."]
                self.entries["id_penulis"]["values"] = current_values
                self.entries["id_penulis"].set(new_id)
                self.entries["nama_penulis"].delete(0, tk.END)
                self.entries["nama_penulis"].insert(0, new_nama)
        else:
            self.cursor.execute("SELECT Nama_Penulis FROM penulis WHERE ID_Penulis=%s", (id_penulis,))
            row = self.cursor.fetchone()
            if row:
                self.entries["nama_penulis"].delete(0, tk.END)
                self.entries["nama_penulis"].insert(0, row[0])

    def fill_penerbit(self, event):
        id_penerbit = self.entries["id_penerbit"].get()
        if id_penerbit == "Tambah Baru...":
            new_id = simpledialog.askstring("ID Penerbit Baru", "Masukkan ID Penerbit Baru:")
            new_nama = simpledialog.askstring("Nama Penerbit Baru", "Masukkan Nama Penerbit Baru:")
            new_alamat = simpledialog.askstring("Alamat Penerbit Baru", "Masukkan Alamat:")
            new_telepon = simpledialog.askstring("Telepon Penerbit Baru", "Masukkan Telepon:")
            if new_id and new_nama:
                current_values = list(self.entries["id_penerbit"]["values"][:-1]) + [new_id, "Tambah Baru..."]
                self.entries["id_penerbit"]["values"] = current_values
                self.entries["id_penerbit"].set(new_id)
                self.entries["nama_penerbit"].delete(0, tk.END)
                self.entries["nama_penerbit"].insert(0, new_nama)
                self.entries["alamat_penerbit"].delete(0, tk.END)
                self.entries["alamat_penerbit"].insert(0, new_alamat or "")
                self.entries["telepon_penerbit"].delete(0, tk.END)
                self.entries["telepon_penerbit"].insert(0, new_telepon or "")
        else:
            self.cursor.execute("SELECT Nama_Penerbit, Alamat_Penerbit, Telepon_Penerbit FROM penerbit WHERE ID_Penerbit=%s", (id_penerbit,))
            row = self.cursor.fetchone()
            if row:
                self.entries["nama_penerbit"].delete(0, tk.END)
                self.entries["nama_penerbit"].insert(0, row[0])
                self.entries["alamat_penerbit"].delete(0, tk.END)
                self.entries["alamat_penerbit"].insert(0, row[1])
                self.entries["telepon_penerbit"].delete(0, tk.END)
                self.entries["telepon_penerbit"].insert(0, row[2])

    # === OVERRIDING (method overriding dari BaseForm/Window if needed) ===
    def submit(self):
        try:
            data = {k: v.get().strip() for k, v in self.entries.items()}
            required_fields = ["id_buku", "judul", "id_kategori", "jenis_kategori",
                               "id_penulis", "nama_penulis", "id_penerbit", "nama_penerbit",
                               "tahun", "sumber"]
            if not all(data[k] for k in required_fields):
                messagebox.showerror("Error", "Field wajib tidak boleh kosong.")
                return

            # Simpan atau update data terkait
            self.cursor.execute("SELECT * FROM kategori WHERE ID_Kategori=%s", (data["id_kategori"],))
            if not self.cursor.fetchone():
                self.cursor.execute("INSERT INTO kategori VALUES (%s, %s)", (data["id_kategori"], data["jenis_kategori"]))
            else:
                self.cursor.execute("UPDATE kategori SET Jenis_Kategori=%s WHERE ID_Kategori=%s", (data["jenis_kategori"], data["id_kategori"]))

            self.cursor.execute("SELECT * FROM penulis WHERE ID_Penulis=%s", (data["id_penulis"],))
            if not self.cursor.fetchone():
                self.cursor.execute("INSERT INTO penulis VALUES (%s, %s)", (data["id_penulis"], data["nama_penulis"]))
            else:
                self.cursor.execute("UPDATE penulis SET Nama_Penulis=%s WHERE ID_Penulis=%s", (data["nama_penulis"], data["id_penulis"]))

            self.cursor.execute("SELECT * FROM penerbit WHERE ID_Penerbit=%s", (data["id_penerbit"],))
            if not self.cursor.fetchone():
                self.cursor.execute("INSERT INTO penerbit VALUES (%s, %s, %s, %s)", 
                    (data["id_penerbit"], data["nama_penerbit"], data["alamat_penerbit"], data["telepon_penerbit"]))
            else:
                self.cursor.execute("UPDATE penerbit SET Nama_Penerbit=%s, Alamat_Penerbit=%s, Telepon_Penerbit=%s WHERE ID_Penerbit=%s",
                    (data["nama_penerbit"], data["alamat_penerbit"], data["telepon_penerbit"], data["id_penerbit"]))

            # Insert buku
            self.cursor.execute("INSERT INTO buku (ID_Buku, Judul_Buku, ID_Kategori, ID_Penulis, ID_Penerbit, Tahun_Terbit, Sumber) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                                (data["id_buku"], data["judul"], data["id_kategori"], data["id_penulis"], data["id_penerbit"], data["tahun"], data["sumber"]))

            self.conn.commit()
            messagebox.showinfo("Sukses", "Buku berhasil ditambahkan.")
            self.destroy()

        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Gagal", str(e))

# === MAIN WINDOW TEST ===
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    db = connect_db()
    form = AddBookForm(root, db)
    form.mainloop()
