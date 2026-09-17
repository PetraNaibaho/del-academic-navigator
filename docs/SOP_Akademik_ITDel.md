# Standar Operasional Prosedur (SOP) Akademik & Penjadwalan Institut Teknologi Del
**Nomor Dokumen:** SOP-AKD-ITDEL-2026-V1  
**Berlaku Efektif:** Tahun Ajaran Gasal 2026/2027  
**Penerbit:** Bagian Administrasi Akademik & Kemahasiswaan (BAAK) & Program Studi Sarjana Sistem Informasi  

---

## 1. Latar Belakang & Filosofi Akademik IT Del
Institut Teknologi Del (IT Del) menerapkan sistem pendidikan berasrama (*boarding campus*) berbasis nilai dasar **"MarTuhan, Marroha, Marbisuk"**. Seluruh aktivitas perkuliahan, praktikum, bimbingan akademik, serta kegiatan kemahasiswaan terikat pada jadwal harian yang ketat (*structured schedule*), mulai dari apel pagi, perkuliahan formal (08:00 - 17:00), hingga jam belajar mandiri terawasi di malam hari (*study time* 19:30 - 22:00).

Oleh karena itu, setiap perubahan alokasi waktu dan ruangan wajib mematuhi standar operasional agar tidak mengganggu keharmonisan ekosistem asrama dan jadwal angkatan lain.

---

## 2. Ketentuan Penjadwalan Ulang Kuliah (Make-Up Class)

### 2.1. Syarat & Waktu Pengajuan
1. Pengajuan perkuliahan pengganti oleh Dosen Pengampu wajib dilakukan minimal **H-2** hari kerja sebelum rencana tanggal perkuliahan dilaksanakan.
2. Pengajuan mendadak (< H-2) hanya diperbolehkan dalam kondisi darurat medis atau tugas kedinasan mendesak dari Rektorat dengan persetujuan Ketua Program Studi.

### 2.2. Pencegahan Bentrok Jadwal (*Zero-Conflict Constraint*)
1. Slot waktu kuliah pengganti dilarang bertabrakan dengan:
   - Mata kuliah wajib atau pilihan lain pada kurikulum angkatan mahasiswa yang bersangkutan.
   - Sesi praktikum laboratorium yang telah terjadwal di SIA IT Del.
   - Waktu istirahat wajib kampus (makan siang pukul 12:00 - 13:00) dan kegiatan apel/asrama pukul 17:00 ke atas.

### 2.3. Alokasi dan Utilisasi Ruangan Kuliah
1. **Kelas Gabungan & Kapasitas Besar (> 40 Mahasiswa):**
   - Wajib dialokasikan ke ruangan berkapasitas besar, yaitu **GD721** (kapasitas 80 mahasiswa) atau **GD722** (kapasitas 75 mahasiswa).
   - Penggunaan ruangan kelas reguler seperti **GD512** (kapasitas 40 mahasiswa) dilarang untuk kelas paralel gabungan guna mencegah *overcrowding*.
2. **Kelas Praktikum Berbasis Lab:**
   - Wajib dialokasikan di Laboratorium Komputer (GD911, Lab AI, Lab Jaringan) dengan ketersediaan perangkat *workstation* mencukupi.

### 2.4. Persetujuan & Notifikasi
1. Sistem menerbitkan draf berita acara pengganti yang disetujui secara digital oleh Koordinator Program Studi dan BAAK.
2. Informasi disiarkan secara otomatis kepada mahasiswa melalui kanal resmi ECourse / notifikasi Del Copilot.

---

## 3. Ketentuan Layanan Bimbingan Akademik (Dosen PA)

### 3.1. Hakikat dan Frekuensi Bimbingan
1. Bimbingan Pembimbing Akademik (PA) bertujuan memantau indeks prestasi (IP/IPK), evaluasi kehadiran, perencanaan Kartu Rencana Studi (KRS), serta pembinaan karakter mahasiswa.
2. Bimbingan wajib dilaksanakan minimal **3 kali per semester**:
   - Awal Semester: Perencanaan dan *approval* KRS.
   - Tengah Semester: Evaluasi nilai Ujian Tengah Semester (UTS) dan *early-warning* absensi.
   - Akhir Semester: Refleksi persiapan Ujian Akhir Semester (UAS).

### 3.2. Kuota & Durasi Sesi
1. **Batas Kuota Sesi:** Dosen PA dibatasi membuka kuota konsultasi maksimal **5 mahasiswa per sesi** agar interaksi berlangsung mendalam dan personal.
2. **Durasi Sesi:** Durasi setiap sesi bimbingan adalah **45 hingga 60 menit**.
3. **Lokasi Bimbingan:** Dilaksanakan di Ruang Dosen Gedung 9 atau ruang diskusi akademik yang ditentukan.

### 3.3. Persyaratan Mahasiswa
1. Mahasiswa wajib membawa draf KRS atau riwayat indeks prestasi dari SIA Del.
2. Mahasiswa yang memiliki absensi mendekati batas kritis (toleransi ketidakhadiran maksimal 25%) wajib melampirkan surat peringatan akademik.

---

## 4. Matriks Ringkasan Penalti Penjadwalan (Cost Matrix)

| Parameter Perubahan | Kondisi | Bobot Biaya Penalti ($C$) | Keterangan SOP |
|---|---|---|---|
| **Pergeseran Hari ($\Delta \text{Day}$)** | $H+1$ (Terlalu cepat) | $8.0$ | Melanggar aturan notice H-2 |
| | $H+2$ (Tepat SOP) | $2.0$ | Sesuai SOP minimal H-2 |
| | $H+3$ s.d. $H+4$ | $3.5 - 5.0$ | Diterima namun menunda materi |
| **Pergeseran Jam ($\Delta \text{Hour}$)** | Jam sama (Preferensi Dosen) | $0.0$ | Paling disukai |
| | Selisih $1-2$ jam | $1.0 - 2.0$ | Dapat diterima |
| | Selisih $\ge 3$ jam / Sore | $4.0 - 6.0$ | Menambah kelelahan mahasiswa |
| **Kesesuaian Ruangan** | Ruang kapasitas sesuai | $0.0$ | GD721/GD722 untuk $>40$ mhs |
| | Ruang *under-capacity* | $\infty$ (*Forbidden/Conflict*) | Melanggar kapasitas fisik |
| | Pindah gedung berbeda | $2.0$ | Penalti waktu jalan antar gedung |

Dokumen ini menjadi acuan tunggal (*single source of truth*) dalam perumusan batasan (*constraints*), evaluasi ruang keadaan, dan penghitungan fungsi biaya penalti pada **Del-Academic Navigator**.