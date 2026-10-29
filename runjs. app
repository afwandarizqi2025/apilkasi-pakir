function hitungBiayaParkir(jenisKendaraan, jamMasuk, jamKeluar) {
    // Tarif dasar per jenis kendaraan
    const tarif = {
        motor: { jamPertama: 2000, jamBerikutnya: 1000 },
        mobil: { jamPertama: 5000, jamBerikutnya: 2000 },
        truk:  { jamPertama: 10000, jamBerikutnya: 5000 }
    };

    // Validasi jenis kendaraan
    const tipe = jenisKendaraan.toLowerCase();
    if (!tarif[tipe]) {
        return "Jenis kendaraan tidak valid!";
    }

    // Hitung durasi parkir
    let durasi = jamKeluar - jamMasuk;
    if (durasi < 0) {
        durasi += 24; // Penanganan jika parkir melewati tengah malam
    }
    if (durasi === 0) {
        durasi = 1; // Minimal parkir dihitung 1 jam
    }

    // Hitung total biaya
    const tarifKendaraan = tarif[tipe];
    let totalBiaya = tarifKendaraan.jamPertama;

    if (durasi > 1) {
        totalBiaya += (durasi - 1) * tarifKendaraan.jamBerikutnya;
    }

    return {
        jenisKendaraan: tipe,
        durasiParkir: `${durasi} jam`,
        totalBiaya: `Rp ${totalBiaya.toLocaleString('id-ID')}`
    };
}

// Contoh Penggunaan:
console.log(hitungBiayaParkir('mobil', 8, 12)); 
// Output: Mobil parkir 4 jam (5000 + 3 * 2000) = Rp 11.000

console.log(hitungBiayaParkir('motor', 22, 2));  
// Output: Motor parkir lewat tengah malam 4 jam (2000 + 3 * 1000) = Rp 5.000
