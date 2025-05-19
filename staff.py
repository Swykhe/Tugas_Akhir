import tkinter as tk
from tkinter import ttk, messagebox
from db_connection import connect_db

# ===== Logic Layer =====
class User:
    def __init__(self, id_staff, nama, nomor):
        self._id_staff = id_staff
        self._nama = nama
        self._nomor = nomor

    def tampilkan_info(self):
        return f"ID: {self._id_staff}, Nama: {self._nama}, Nomor: {self._nomor}"

    def get_id(self):
        return self._id_staff

    def get_nama(self):
        return self._nama

    def get_nomor(self):
        return self._nomor

    def set_nama(self, nama):
        self._nama = nama

    def set_nomor(self, nomor):
        self._nomor = nomor


class Admin(User):
    def __init__(self, id_staff, nama, nomor, password):
        super().__init__(id_staff, nama, nomor)
        self.__password = password  # private attribute

    def get_password(self):
        return self.__password

    def set_password(self, new_password):
        self.__password = new_password
        self._update_password_db()

    def _update_password_db(self):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE staff SET Password = %s WHERE ID_Staff = %s", (self.__password, self._id_staff))
        conn.commit()
        conn.close()

    def tampilkan_info(self):  # overriding
        return f"[Admin] {super().tampilkan_info()}"

    def ganti_admin(self, nama_baru, nomor_baru, password_baru):
        self.set_nama(nama_baru)
        self.set_nomor(nomor_baru)
        self.__password = password_baru
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE staff SET Nama_Staff = %s, Nomor_Staff = %s, Password = %s WHERE ID_Staff = %s",
            (nama_baru, nomor_baru, password_baru, self._id_staff)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def lihat_data_admin():
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT ID_Staff, Nama_Staff, Nomor_Staff FROM staff")
        data = cursor.fetchall()
        conn.close()
        return data


# ===== GUI Layer =====
class BaseAdminGUI(tk.Toplevel):
    def __init__(self, root):
        super().__init__(root)
        self._frame = ttk.Frame(self, padding=10)
        self._frame.pack(fill="both", expand=True)


class AdminPanel(BaseAdminGUI):
    def __init__(self, root, id_staff):
        super().__init__(root)
        self.title("Kelola Akun Admin")
        self.geometry("500x450")

        admin = self._load_admin_data(id_staff)
        if not admin:
            messagebox.showerror("Error", "Admin tidak ditemukan")
            self.destroy()
            return

        self._admin = admin
        self._build_interface()

    def _load_admin_data(self, id_staff):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM staff WHERE ID_Staff = %s", (id_staff,))
        row = cursor.fetchone()
        conn.close()
        return Admin(*row) if row else None

    def _build_interface(self):
        ttk.Label(self._frame, text="Data Admin Saat Ini", font=("Arial", 12, "bold")).pack(pady=10)

        self._info_text = tk.Text(self._frame, height=4, width=50, state="normal")
        self._info_text.insert(tk.END, self._admin.tampilkan_info())
        self._info_text.config(state="disabled")
        self._info_text.pack()

        # Ganti password
        ttk.Label(self._frame, text="Ganti Password", font=("Arial", 10, "bold")).pack(pady=(20, 5))
        self._password_entry = ttk.Entry(self._frame, show="*")
        self._password_entry.pack()
        ttk.Button(self._frame, text="Ubah Password", command=self._ubah_password).pack(pady=5)

        # Ganti data admin
        ttk.Label(self._frame, text="Ganti Data Admin", font=("Arial", 10, "bold")).pack(pady=(20, 5))
        self._nama_entry = ttk.Entry(self._frame)
        self._nama_entry.insert(0, self._admin.get_nama())
        self._nama_entry.pack()

        self._nomor_entry = ttk.Entry(self._frame)
        self._nomor_entry.insert(0, self._admin.get_nomor())
        self._nomor_entry.pack()

        self._password_baru_entry = ttk.Entry(self._frame, show="*")
        self._password_baru_entry.insert(0, self._admin.get_password())
        self._password_baru_entry.pack()

        ttk.Button(self._frame, text="Ganti Admin", command=self._ganti_data_admin).pack(pady=5)
        ttk.Button(self._frame, text="Lihat Semua Admin", command=self._lihat_semua_admin).pack(pady=10)

    def _ubah_password(self):
        new_pw = self._password_entry.get()
        if new_pw:
            self._admin.set_password(new_pw)
            messagebox.showinfo("Berhasil", "Password berhasil diubah!")
            self._password_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Input Kosong", "Masukkan password baru!")

    def _ganti_data_admin(self):
        nama = self._nama_entry.get()
        nomor = self._nomor_entry.get()
        pw = self._password_baru_entry.get()
        if nama and nomor and pw:
            self._admin.ganti_admin(nama, nomor, pw)
            self._update_info_text()
            messagebox.showinfo("Berhasil", "Data admin berhasil diganti!")
        else:
            messagebox.showwarning("Input Kosong", "Semua data harus diisi!")

    def _update_info_text(self):
        self._info_text.config(state="normal")
        self._info_text.delete(1.0, tk.END)
        self._info_text.insert(tk.END, self._admin.tampilkan_info())
        self._info_text.config(state="disabled")

    def _lihat_semua_admin(self):
        semua = Admin.lihat_data_admin()
        if semua:
            result = "\n".join([f"{id_} | {nama} | {nomor}" for id_, nama, nomor in semua])
            messagebox.showinfo("Data Semua Admin", result)
        else:
            messagebox.showinfo("Kosong", "Tidak ada data admin.")
