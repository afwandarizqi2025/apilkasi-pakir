import customtkinter as ctk
from tkinter import messagebox, ttk
import mysql.connector
from datetime import datetime
import math

# --- KONFIGURASI DATABASE ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',      # Sesuaikan username MySQL Anda
    'password': '',      # Sesuaikan password MySQL Anda
    'database': 'parkir_db'
}

# --- TARIF PARKIR PER JAM ---
TARIF = {
    'Motor': 2000,
    'Mobil': 5000
}

def get_db_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Gagal terhubung ke MySQL: {err}")
        return None

class ParkingApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sistem Manajemen Parkir")
        self.geometry("850 x 550")
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # Layout Utama
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Panel Kiri (Form Input)
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=10)
        self.sidebar.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

        # Title Sidebar
        self.lbl_title = ctk.CTkLabel(self.sidebar, text="Aplikasi Parkir", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_title.pack(padx=20, pady=(20, 10))

        # Input Plat Nomor
        self.lbl_plat = ctk.CTkLabel(self.sidebar, text="Nomor Plat Kendaraan:")
        self.lbl_plat.pack(padx=20, pady=(10, 0), anchor="w")
        
        self.entry_plat = ctk.CTkEntry(self.sidebar, placeholder_text="Contoh: B 1234 ABC")
        self.entry_plat.pack(padx=20, pady=(5, 10), fill="x")

        # Input Jenis Kendaraan
        self.lbl_jenis = ctk.CTkLabel(self.sidebar, text="Jenis Kendaraan:")
        self.lbl_jenis.pack(padx=20, pady=(5, 0), anchor="w")

        self.combo_jenis = ctk.CTkComboBox(self.sidebar, values=["Motor", "Mobil"])
        self.combo_jenis.pack(padx=20, pady=(5, 15), fill="x")

        # Tombol Aksi
        self.btn_masuk = ctk.CTkButton(self.sidebar, text="Kendaraan Masuk", command=self.kendaraan_masuk, fg_color="green", hover_color="darkgreen")
        self.btn_masuk.pack(padx=20, pady=5, fill="x")

        self.btn_keluar = ctk.CTkButton(self.sidebar, text="Kendaraan Keluar", command=self.kendaraan_keluar, fg_color="red", hover_color="darkred")
        self.btn_keluar.pack(padx=20, pady=5, fill="x")

        self.btn_refresh = ctk.CTkButton(self.sidebar, text="Refresh Data", command=self.load_data)
        self.btn_refresh.pack(padx=20, pady=(15, 5), fill="x")

        # Panel Kanan (Tabel Data)
        self.content = ctk.CTkFrame(self, corner_radius=10)
        self.content.grid(row=0, column=1, padx=(0, 15), pady=15, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        # Tabel menggunakan Treeview
        columns = ("id", "plat", "jenis", "masuk", "keluar", "tarif", "status")
        self.tree = ttk.Treeview(self.content, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("id", text="ID")
        self.tree.heading("plat", text="Plat Nomor")
        self.tree.heading("jenis", text="Jenis")
        self.tree.heading("masuk", text="Waktu Masuk")
        self.tree.heading("keluar", text="Waktu Keluar")
        self.tree.heading("tarif", text="Tarif (Rp)")
        self.tree.heading("status", text="Status")

        self.tree.column("id", width=40, anchor="center")
        self.tree.column("plat", width=110, anchor="center")
        self.tree.column("jenis", width=80, anchor="center")
        self.tree.column("masuk", width=140, anchor="center")
        self.tree.column("keluar", width=140, anchor="center")
        self.tree.column("tarif", width=90, anchor="e")
        self.tree.column("status", width=80, anchor="center")

        self.tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Event Klik pada Tabel
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        self.load_data()

    def kendaraan_masuk(self):
        plat = self.entry_plat.get().strip().upper()
        jenis = self.combo_jenis.get()

        if not plat:
            messagebox.showwarning("Peringatan", "Nomor plat tidak boleh kosong!")
            return

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            # Cek apakah plat sedang parkir
            cursor.execute("SELECT id FROM parkir WHERE plat_nomor = %s AND status = 'Parkir'", (plat,))
            if cursor.fetchone():
                messagebox.showwarning("Peringatan", f"Kendaraan dengan plat {plat} sudah terdaftar sedang parkir!")
            else:
                waktu_sekarang = datetime.now()
                cursor.execute(
                    "INSERT INTO parkir (plat_nomor, jenis_kendaraan, waktu_masuk, status) VALUES (%s, %s, %s, 'Parkir')",
                    (plat, jenis, waktu_sekarang)
                )
                conn.commit()
                messagebox.showinfo("Sukses", f"Kendaraan {plat} berhasil masuk.")
                self.entry_plat.delete(0, 'end')
                self.load_data()
            cursor.close()
            conn.close()

    def kendaraan_keluar(self):
        plat = self.entry_plat.get().strip().upper()

        if not plat:
            messagebox.showwarning("Peringatan", "Masukkan nomor plat kendaraan yang akan keluar!")
            return

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM parkir WHERE plat_nomor = %s AND status = 'Parkir'", (plat,))
            data = cursor.fetchone()

            if not data:
                messagebox.showwarning("Peringatan", f"Kendaraan dengan plat {plat} tidak ditemukan sedang parkir.")
            else:
                waktu_masuk = data['waktu_masuk']
                waktu_keluar = datetime.now()
                jenis = data['jenis_kendaraan']

                # Hitung durasi jam (pembulatan ke atas)
                selisih = waktu_keluar - waktu_masuk
                jam = math.ceil(selisih.total_seconds() / 3600)
                if jam < 1:
                    jam = 1

                total_tarif = jam * TARIF.get(jenis, 2000)

                # Update data parkir
                cursor.execute(
                    "UPDATE parkir SET waktu_keluar = %s, total_tarif = %s, status = 'Selesai' WHERE id = %s",
                    (waktu_keluar, total_tarif, data['id'])
                )
                conn.commit()

                info_pesan = (
                    f"Plat Nomor: {plat}\n"
                    f"Durasi: {jam} jam\n"
                    f"Total Tarif: Rp {total_tarif:,}"
                )
                messagebox.showinfo("Pembayaran Parkir", info_pesan)
                self.entry_plat.delete(0, 'end')
                self.load_data()

            cursor.close()
            conn.close()

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, plat_nomor, jenis_kendaraan, waktu_masuk, waktu_keluar, total_tarif, status FROM parkir ORDER BY id DESC")
            rows = cursor.fetchall()

            for row in rows:
                waktu_masuk = row[3].strftime("%Y-%m-%d %H:%M") if row[3] else "-"
                waktu_keluar = row[4].strftime("%Y-%m-%d %H:%M") if row[4] else "-"
                tarif = f"{row[5]:,}" if row[5] else "0"

                self.tree.insert("", "end", values=(row[0], row[1], row[2], waktu_masuk, waktu_keluar, tarif, row[6]))

            cursor.close()
            conn.close()

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            plat_nomor = item['values'][1]
            self.entry_plat.delete(0, 'end')
            self.entry_plat.insert(0, plat_nomor)

if __name__ == "__main__":
    app = ParkingApp()
    app.mainloop()
