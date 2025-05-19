import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from db_connection import connect_db
import add_book
import read_book
import update_book
import delete_book
from categori_book import CategoryApp
from transaction_main import TransactionForm
from detail_transaction import DetailTransactionForm
from staff import AdminPanel
from background import BlurredBackground

# Kelas Dasar (Super Class)
class AppWindow:
    def __init__(self, root, title, geometry="1200x600"):
        self.root = root
        self.root.title(title)
        self.root.geometry(geometry)
        self.root.configure(background="#ffffff")

    def setup_background(self, bg_path):
        bg = BlurredBackground(self.root, bg_path)
        bg.set_background()
        self.bg_label = bg.get_label()
        self.bg_label.lower()

    def create_welcome_message(self, username):
        welcome_label = tk.Label(self.root, text=f"Explore, Learn, Innovate – Welcome to the Library Services, {username}!", font=("Times New Roman", 18, "bold"))
        welcome_label.pack(pady=(20, 10))

    def create_logo(self, logo_path):
        try:
            img = Image.open(logo_path)
            img = img.resize((150, 150))
            photo = ImageTk.PhotoImage(img)
            label_logo = tk.Label(self.root, image=photo, borderwidth=0, highlightthickness=0)
            label_logo.image = photo  # mencegah garbage collection
            label_logo.pack(pady=(0, 10))
        except Exception as e:
            tk.Label(self.root, text="Logo tidak ditemukan").pack()

    def create_footer(self):
        frame_scrolling = tk.Frame(self.root)
        frame_scrolling.pack(side="bottom", fill="x")

        scrolling_text = tk.Label(frame_scrolling, text="Selamat datang di Perpustakaan DTEI. Jelajahi berbagai buku dan jurnal.", 
                                  font=("Times New Roman", 11))
        scrolling_text.pack()

        def scroll_text():
            current_text = scrolling_text.cget("text")
            scrolling_text.config(text=current_text[1:] + current_text[0])
            self.root.after(100, scroll_text)

        scroll_text()

# Kelas Turunan (Subclass) untuk Dashboard
class DashboardApp(AppWindow):
    def __init__(self, root, id_staff, username):
        super().__init__(root, "Sistem Manajemen Perpustakaan - Admin")
        self.id_staff = id_staff
        self.username = username
        self.bg_path = "C:/Users/Swykhe Galeh Wahyu P/OneDrive/ドキュメント/TUGAS AKHIR/dtei gedung.jpg"
        self.logo_path = "C:/Users/Swykhe Galeh Wahyu P/OneDrive/ドキュメント/TUGAS AKHIR/dtei.png"  # ganti dengan path logo kamu
        self.sidebar_width = 200
        self.setup_dashboard()

    def setup_dashboard(self):
        self.setup_background(self.bg_path)
        self.create_welcome_message(self.username)
        self.create_logo(self.logo_path)
        self.create_sidebar()
        self.create_menu_button()

        # Add specific methods like description, statistics, etc.
        self.create_description()
        self.create_contact_info()
        self.create_statistics()
        self.create_footer()

        self.sidebar.place_forget()

    def create_sidebar(self):
        self.sidebar = tk.Frame(self.root, bg="#2c3e50", width=self.sidebar_width, height=600)
        self.sidebar.place(x=0, y=0)  # posisi di luar jendela (kanan)

        id_transaksi = "TRX001"

        buttons = [
            ("Tambah Buku", lambda: add_book.AddBookForm(self.root, connect_db())),
            ("Lihat Buku", lambda: read_book.ReadBookForm(self.root, connect_db())),
            ("Update Buku", lambda: update_book.UpdateBookForm(self.root, connect_db())),
            ("Hapus Buku", lambda: delete_book.DeleteBookForm(self.root)),
            ("Tambah Transaksi", lambda: TransactionForm(self.root, self.id_staff)),
            ("Detail Transaksi", lambda: DetailTransactionForm(self.root, id_transaksi)),
            ("Lihat Kategori", lambda: CategoryApp(self.root)),
            ("Akun Admin", lambda: AdminPanel(self.root, self.id_staff)),
            ("Logout", self.logout),
        ]
        self.create_sidebar_buttons(buttons)

    def create_sidebar_buttons(self, buttons):
        btn_style = {"font": ("Times New Roman", 12), "bg": "#34495e", "fg": "white", "bd": 0, "activebackground": "#1abc9c", "activeforeground": "white", "cursor": "hand2"}
        
        for i, (text, cmd) in enumerate(buttons):
            b = tk.Button(self.sidebar, text=text, command=cmd, **btn_style)
            b.pack(fill="x", padx=10, pady=5)

    def create_menu_button(self):
        # Tombol hamburger untuk membuka sidebar
        self.menu_button = tk.Button(self.root, text="☰", command=self.toggle_sidebar)
        self.menu_button.place(x=10, y=10)

    def toggle_sidebar(self):
        if self.sidebar.winfo_ismapped():
            self.sidebar.place_forget()  # Menyembunyikan sidebar
        else:
            self.sidebar.place(x=0, y=0)

    def create_description(self):
        desc_text = (
            "Perpustakaan DTEI adalah pusat informasi dan sumber belajar utama\n"
            "bagi mahasiswa dan staf Departemen Teknik Elektro dan Informatika.\n\n"
            "Kami menyediakan koleksi buku, jurnal, dan bahan referensi yang lengkap\n"
            "untuk mendukung kegiatan akademik dan penelitian.\n\n"
            "Layanan kami meliputi peminjaman buku, akses digital, serta ruang belajar nyaman."
        )

        tk.Label(self.root, text="Perpustakaan DTEI", font=("Times New Roman", 14, "bold")).pack()
        tk.Label(self.root, text=desc_text, font=("Times New Roman", 11), justify="center").pack(pady=(5, 15))

    def create_contact_info(self):
        contact_text = (
            "📞 Kontak: 0812-3456-7890   |   ✉️ Email: perpustakaan@dtei.ac.id\n"
            "🕐 Jam Operasional: Senin - Jumat, 08.00 - 16.00"
        )

        tk.Label(self.root, text=contact_text, font=("Times New Roman", 11, "italic")).pack(pady=(0, 15))

    def create_statistics(self):
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM buku")
        total_buku = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM mahasiswa")
        total_peminjam = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM detail_transaksi WHERE Status = 'Terlambat'")
        total_terlambat = cursor.fetchone()[0]

        # Statistik
        frame_stats = tk.Frame(self.root)
        frame_stats.pack(pady=(5, 10))

        for i, (label_text, value) in enumerate([
            ("Total Buku", total_buku),
            ("Total Peminjam", total_peminjam),
            ("Buku Terlambat", total_terlambat),
        ]):
            stat_label = tk.Label(frame_stats, text=f"{label_text}: {value}", font=("Arial", 12))
            stat_label.grid(row=0, column=i, padx=20)

    def logout(self):
        print("Logout clicked")
        self.root.destroy()

# Kode Utama untuk Menjalankan Aplikasi
if __name__ == '__main__':
    root = tk.Tk()
    dashboard = DashboardApp(root, id_staff="123", username="admin")
