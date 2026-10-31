"""Script to generate the complete enterprise document corpus for Institut Teknologi Del.

Generates:
- 7 Markdown documents (.md)
- 5 Plain text documents (.txt)
- 3 Formal PDF documents (.pdf) via ReportLab
- data/corpus_manifest.json and data/corpus_manifest.csv
"""

import os
import json
import csv
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

BASE_DIR = Path(__file__).resolve().parent.parent
CORPUS_DIR = BASE_DIR / "data" / "corpus"
MANIFEST_JSON = BASE_DIR / "data" / "corpus_manifest.json"
MANIFEST_CSV = BASE_DIR / "data" / "corpus_manifest.csv"

DOCUMENTS = [
    {
        "doc_id": "SOP-AKD-01",
        "filename": "SOP-AKD-01_Penjadwalan_Kuliah_Pengganti.md",
        "format": "md",
        "category": "SOP_AKADEMIK",
        "title": "SOP Penjadwalan Perkuliahan Pengganti (Make-Up Class) dan Utilisasi Ruangan",
        "created_date": "2026-09-01",
        "content": """# STANDAR OPERASIONAL PROSEDUR PENJADWALAN KULIAH PENGGANTI (MAKE-UP CLASS)
**Nomor Dokumen:** SOP-AKD-01-ITDEL-2026  
**Edisi/Revisi:** Gasal 2026/2027  
**Unit Penerbit:** Bagian Administrasi Akademik dan Kemahasiswaan (BAAK) & Program Studi Sarjana Sistem Informasi  
**Pernyataan Kepatuhan:** Dokumen ini merupakan simulasi operasional akademik berstandar enterprise fiktif dan mematuhi UU PDP No. 27/2022 tanpa data pribadi riil.

---

## BAB I: KETENTUAN UMUM DAN PRINSIP DASAR
1. Perkuliahan pengganti (*make-up class*) diselenggarakan untuk memenuhi capaian minimal 14 sesi tatap muka per semester di luar Ujian Tengah Semester (UTS) dan Ujian Akhir Semester (UAS).
2. Seluruh kegiatan akademik di Institut Teknologi Del (IT Del) terikat pada ritme kehidupan asrama (*boarding campus*) dengan nilai luhur "MarTuhan, Marroha, Marbisuk".
3. Penjadwalan ulang dilarang menimbulkan konflik waktu (*zero-conflict principle*) dengan jadwal perkuliahan paralel, jadwal praktikum laboratorium, dan jam ibadah/makan asrama.

## BAB II: PROSEDUR DAN TENGGANG WAKTU PENGAJUAN (ATURAN H-2)
1. Dosen Pengampu wajib mengajukan permohonan kuliah pengganti paling lambat **H-2 (dua hari kerja)** sebelum pelaksanaan sesi pengganti.
2. Pengajuan perkuliahan mendadak (< H-2) dikategorikan sebagai pelanggaran administratif berat, kecuali disertai surat keterangan darurat medis atau disposisi resmi Rektorat.
3. Permohonan diajukan melalui sistem Del-Academic Navigator Copilot atau portal Sistem Informasi Akademik (SIA) dengan melampirkan alasan ketidakhadiran sebelumnya.
4. Persetujuan jadwal melibatkan verifikasi otomatis bebas bentrok oleh mesin inferensi serta otorisasi digital dari Koordinator Program Studi.

## BAB III: ALOKASI DAN UTILISASI RUANGAN
1. **Kelas Gabungan Paralel (> 40 Mahasiswa):**
   - Wajib menempati ruang kelas berkapasitas besar di Gedung 7, yaitu **GD721** (kapasitas 80 kursi) atau **GD722** (kapasitas 75 kursi).
   - Penggunaan ruangan kelas reguler seperti GD512 (kapasitas 40 kursi) atau GD935 dilarang keras untuk rombel gabungan guna mencegah kelebihan kapasitas (*overcrowding*).
2. **Sesi Praktikum Laboratorium Komputer:**
   - Perkuliahan praktikum pemrograman atau kecerdasan buatan wajib dialokasikan pada laboratorium komputer resmi (GD911, Lab AI, atau Lab Jaringan).
3. **Batasan Waktu Operasional:**
   - Perkuliahan hanya boleh dilaksanakan pada rentang pukul 08:00 hingga 17:00 WIB.
   - Pukul 12:00 hingga 13:00 WIB merupakan waktu istirahat makan siang wajib terpusat di kantin kampus dan tidak boleh digunakan untuk perkuliahan.
   - Pukul 17:00 hingga 19:30 WIB dialokasikan untuk kegiatan apel sore, olahraga, makan malam, dan ibadah malam asrama.
   - Pukul 19:30 hingga 22:00 WIB adalah jam belajar mandiri terawasi (*compulsory study time*) di ruang belajar asrama.

## BAB IV: PENGESAHAN DAN NOTIFIKASI
1. Berita acara perkuliahan pengganti diterbitkan otomatis setelah disetujui BAAK.
2. Seluruh mahasiswa peserta kelas menerima notifikasi terjadwal melalui aplikasi kampus selambat-lambatnya 24 jam sebelum kuliah dimulai.
"""
    },
    {
        "doc_id": "SOP-AKD-02",
        "filename": "SOP-AKD-02_Layanan_Bimbingan_Akademik_Dosen_PA.md",
        "format": "md",
        "category": "SOP_AKADEMIK",
        "title": "SOP Layanan Bimbingan Akademik Dosen Pembimbing Akademik (Dosen PA)",
        "created_date": "2026-09-05",
        "content": """# STANDAR OPERASIONAL PROSEDUR BIMBINGAN AKADEMIK DOSEN PEMBIMBING AKADEMIK (PA)
**Nomor Dokumen:** SOP-AKD-02-ITDEL-2026  
**Edisi/Revisi:** Gasal 2026/2027  
**Unit Penerbit:** Fakultas Informatika dan Teknik Elektro (FITE) IT Del  
**Pernyataan Privasi:** Dokumen fiktif operasional untuk riset kecerdasan buatan, selaras UU Perlindungan Data Pribadi No. 27/2022.

---

## 1. TUJUAN DAN RUANG LINGKUP
Prosedur ini menetapkan tata kelola pembimbingan akademik antara mahasiswa dan Dosen Pembimbing Akademik (Dosen PA) guna memastikan ketercapaian target kelulusan tepat waktu, pemantauan Indeks Prestasi Kumulatif (IPK), dan pembinaan karakter MarTuhan, Marroha, Marbisuk.

## 2. FREKUENSI DAN WAKTU PELAKSANAAN
1. Setiap mahasiswa wajib mengikuti sesi konsultasi tatap muka dengan Dosen PA minimal **3 (tiga) kali dalam satu semester**:
   - **Sesi I (Awal Semester):** Konsultasi rencana studi, peninjauan prasyarat mata kuliah, dan persetujuan Kartu Rencana Studi (KRS).
   - **Sesi II (Pertengahan Semester / Pasca-UTS):** Evaluasi hasil Ujian Tengah Semester, deteksi dini mahasiswa berisiko akademik (*early warning*), dan review kehadiran presensi.
   - **Sesi III (Akhir Semester / Pra-UAS):** Evaluasi kesiapan menghadapi Ujian Akhir Semester dan konseling perkembangan kepribadian/asrama.
2. Mahasiswa yang memiliki IPK di bawah 2.00 atau absensi di atas 15% wajib menghadiri bimbingan intensif tambahan setiap dua pekan sekali.

## 3. KUOTA DAN DURASI KONSULTASI
1. **Kuota Peserta per Sesi:** Untuk menjamin kualitas diskusi dan kedalaman evaluasi, kuota konsultasi dibatasi maksimal **5 (lima) mahasiswa per sesi**.
2. **Durasi Waktu:** Setiap sesi bimbingan berlangsung antara 45 hingga 60 menit.
3. **Lokasi Bimbingan:** Pertemuan dilaksanakan di ruang kerja Dosen PA di Gedung 9 lantai 2 atau ruang konsultasi akademik fakultas. Konsultasi tidak diizinkan dilakukan di kafetaria atau ruang publik informal.

## 4. KEWAJIBAN MAHASISWA DAN DOSEN
1. Mahasiswa wajib membawa lembar cetak Kartu Hasil Studi (KHS) terakhir dan rekapitulasi kehadiran dari portal akademik.
2. Dosen PA berhak menolak persetujuan KRS apabila mahasiswa tidak hadir pada sesi bimbingan awal semester tanpa alasan yang sah.
3. Segala catatan bimbingan dicatat secara digital pada logbook portal akademik IT Del dan terhubung ke Del-Academic Navigator.
"""
    },
    {
        "doc_id": "SOP-LAB-01",
        "filename": "SOP-LAB-01_Peminjaman_dan_Penggunaan_Laboratorium_Komputer.md",
        "format": "md",
        "category": "SOP_FASILITAS",
        "title": "SOP Peminjaman dan Penggunaan Laboratorium Komputer dan AI",
        "created_date": "2026-09-08",
        "content": """# STANDAR OPERASIONAL PROSEDUR PENGGUNAAN LABORATORIUM KOMPUTER & ARTIFICIAL INTELLIGENCE
**Nomor Dokumen:** SOP-LAB-01-ITDEL-2026  
**Edisi/Revisi:** Gasal 2026/2027  
**Unit Penerbit:** Unit Pengelola Laboratorium Komputer & Komputasi Awan IT Del  
**Status Kerahasiaan:** Dokumen Terbuka Fiktif Akademik (UU PDP No. 27/2022 compliant).

---

## PASAL 1: KETENTUAN FASILITAS DAN HAK AKSES
1. Laboratorium Komputer IT Del (mencakup GD911, Lab AI, Lab Jaringan, dan Lab Rekayasa Perangkat Lunak) diperuntukkan bagi kegiatan praktikum kurikuler, riset tugas akhir, dan pelatihan resmi institusi.
2. Fasilitas laboratorium mencakup 40 unit workstation berperforma tinggi dengan kartu grafis akselerasi GPU, koneksi gigabit ethernet, dan sistem pendingin ruangan terstandarisasi.
3. Mahasiswa berhak mengakses laboratorium sesuai jadwal praktikum resmi atau jadwal peminjaman mandiri yang telah disetujui Kepala Laboratorium.

## PASAL 2: TATA CARA PEMINJAMAN DI LUAR JADWAL KULIAH
1. Peminjaman laboratorium di luar jam praktikum wajib diajukan paling lambat **H-1** kerja melalui Sistem Informasi Peminjaman Sarana Kampus.
2. Permohonan harus didukung oleh Dosen Pembimbing Mata Kuliah atau Dosen Pembina Organisasi Kemahasiswaan.
3. Jam operasional peminjaman mandiri dibatasi maksimal hingga pukul 17:00 WIB pada hari kerja. Peminjaman pada malam hari memerlukan izin khusus dari Koordinator Asrama dan BAAK.

## PASAL 3: KETERTIBAN DAN LARANGAN
1. Pengguna dilarang membawa makanan, minuman berpemanis, atau benda cair ke dalam area workstation laboratorium.
2. Dilarang mengubah konfigurasi sistem operasi, melepas kabel periferal, atau mengunduh perangkat lunak tanpa izin Asisten Laboratorium.
3. Dilarang keras menggunakan perangkat laboratorium untuk bermain game daring, memutar media hiburan komersial, atau melakukan aktivitas penambangan aset kripto (*cryptocurrency mining*).
4. Pelanggaran terhadap tata tertib ini dikenakan sanksi pencabutan izin akses laboratorium selama 1 (satu) semester penuh dan denda penggantian kerugian jika terjadi kerusakan perangkat.
"""
    },
    {
        "doc_id": "SOP-KMS-01",
        "filename": "SOP-KMS-01_Tata_Tertib_dan_Disiplin_Kehidupan_Asrama.md",
        "format": "md",
        "category": "SOP_KEMAHASISWAAN",
        "title": "SOP Tata Tertib, Disiplin, dan Peribadatan Kehidupan Asrama Mahasiswa",
        "created_date": "2026-09-10",
        "content": """# STANDAR OPERASIONAL PROSEDUR TATA TERTIB DAN DISIPLIN KEHIDUPAN ASRAMA MAHASISWA
**Nomor Dokumen:** SOP-KMS-01-ITDEL-2026  
**Edisi/Revisi:** Gasal 2026/2027  
**Unit Penerbit:** Direktorat Pendidikan dan Pembinaan Karakter Asrama IT Del  
**Landasan Nilai:** Nilai Dasar MarTuhan, Marroha, Marbisuk. Kepatuhan Regulasi Privasi UU PDP No. 27/2022.

---

## BAGIAN I: RUTINITAS HARIAN ASRAMA
1. **Bangun Pagi dan Ibadah (05:30 - 06:00 WIB):** Seluruh mahasiswa wajib bangun pagi, merapikan tempat tidur dengan standar militer asrama, dan melaksanakan doa/ibadah pagi pribadi.
2. **Apel Pagi dan Sarapan Bersama (06:00 - 07:15 WIB):** Mahasiswa berkumpul di lapangan asrama untuk apel pengecekan kelengkapan seragam dan kebersihan, dilanjutkan makan pagi bersama di ruang makan kampus.
3. **Keberangkatan Menuju Kampus (07:30 WIB):** Mahasiswa wajib telah meninggalkan lingkungan asrama menuju gedung perkuliahan selambat-lambatnya pukul 07:45 WIB.
4. **Makan Siang dan Istirahat (12:00 - 13:00 WIB):** Jam makan siang terpusat di ruang makan. Tidak diperbolehkan menyelenggarakan rapat atau kelas tambahan pada jendela waktu ini.
5. **Apel Sore dan Ibadah Malam (17:30 - 19:00 WIB):** Kegiatan olahraga sore, pembersihan kamar asrama, makan malam, dan ibadah malam bersama per asrama.

## BAGIAN II: JAM BELAJAR MANDIRI TERAWASI (STUDY TIME)
1. **Waktu Pelaksanaan:** Jam belajar mandiri wajib (*compulsory study time*) dilaksanakan setiap hari Senin hingga Jumat pukul **19:30 hingga 22:00 WIB**.
2. **Lokasi Belajar:** Mahasiswa wajib berada di ruang belajar bersama (*study hall*) asrama masing-masing atau di laboratorium yang telah memperoleh izin resmi.
3. **Ketertiban:** Selama study time, suasana wajib dijaga dalam kondisi hening (*silent atmosphere*). Penggunaan ponsel cerdas dibatasi khusus untuk referensi akademik.

## BAGIAN III: JAM MALAM DAN PEMADAMAN LAMPU (CURFEW)
1. Pintu gerbang asrama dikunci tepat pada pukul **22:00 WIB**.
2. Pemadaman lampu utama kamar tidur (*lights off*) diberlakukan pukul **23:00 WIB** guna menjamin kecukupan istirahat mahasiswa.
3. Mahasiswa dilarang meninggalkan area asrama setelah jam malam tanpa izin kedaruratan dari Pembina Asrama (Pamong).
"""
    },
    {
        "doc_id": "SOP-BAAK-01",
        "filename": "SOP-BAAK-01_Prosedur_Cuti_Akademik_dan_Pengunduran_Diri.md",
        "format": "md",
        "category": "SOP_AKADEMIK",
        "title": "SOP Prosedur Pengajuan Cuti Akademik dan Pengunduran Diri Mahasiswa",
        "created_date": "2026-09-12",
        "content": """# STANDAR OPERASIONAL PROSEDUR PENGAJUAN CUTI AKADEMIK DAN PENGUNDURAN DIRI
**Nomor Dokumen:** SOP-BAAK-01-ITDEL-2026  
**Edisi/Revisi:** Gasal 2026/2027  
**Unit Penerbit:** Bagian Administrasi Akademik dan Kemahasiswaan (BAAK) IT Del  
**Kepatuhan Hukum:** Dokumen fiktif operasional untuk riset kecerdasan buatan, selaras UU PDP No. 27/2022.

---

## 1. PERSYARATAN CUTI AKADEMIK
1. Cuti akademik adalah masa penghentian studi sementara dengan izin resmi dari Rektor IT Del melalui Dekan Fakultas.
2. Mahasiswa berhak mengajukan cuti akademik setelah menempuh minimal **2 (dua) semester pertama** perkuliahan reguler.
3. Mahasiswa tahun pertama (semester 1 dan 2) tidak diperkenankan mengambil cuti akademik kecuali karena alasan medis darurat yang mengancam jiwa.
4. Cuti akademik diberikan paling banyak **2 (dua) semester berturut-turut** atau akumulasi total 2 semester selama masa studi.
5. Masa cuti akademik **tidak diperhitungkan** ke dalam batas maksimum masa studi mahasiswa.

## 2. PROSEDUR DAN TENGGANG WAKTU PERMOHONAN
1. Pengajuan cuti akademik wajib dilakukan sebelum batas akhir pembayaran Sumbangan Pembinaan Pendidikan (SPP) semester yang bersangkutan, atau selambat-lambatnya 2 minggu sebelum perkuliahan perdana dimulai.
2. Mahasiswa mengunduh Formulir Permohonan Cuti Akademik dari portal BAAK dan melampirkan:
   - Surat persetujuan bermaterai dari orang tua / wali mahasiswa.
   - Rekomendasi tertulis dari Dosen Pembimbing Akademik dan Ketua Program Studi.
   - Surat Keterangan Bebas Pustaka dari Perpustakaan IT Del.
   - Surat Keterangan Bebas Tanggungan Keuangan dari Bagian Keuangan Institusi.
   - Surat Keterangan Bebas Asrama dari Direktorat Kemahasiswaan.

## 3. PROSEDUR PENGUNDURAN DIRI (RESIGNATION)
1. Pengunduran diri atas kehendak sendiri wajib diajukan secara formal kepada Rektor IT Del.
2. Seluruh kewajiban finansial dan pengembalian aset milik kampus (buku perpustakaan, kunci loker, inventaris asrama) harus diselesaikan sebelum penerbitan Surat Keputusan Pemberhentian Studi dan Transkrip Akademik Terakhir.
"""
    },
    {
        "doc_id": "SOP-BAAK-02",
        "filename": "SOP-BAAK-02_Evaluasi_Keberlanjutan_Studi_dan_Drop_Out.md",
        "format": "md",
        "category": "SOP_AKADEMIK",
        "title": "SOP Evaluasi Keberlanjutan Studi (Tahap I, Tahap II) dan Putus Studi (Drop Out)",
        "created_date": "2026-09-15",
        "content": """# STANDAR OPERASIONAL PROSEDUR EVALUASI KEBERLANJUTAN STUDI DAN PUTUS STUDI (DROP OUT)
**Nomor Dokumen:** SOP-BAAK-02-ITDEL-2026  
**Edisi/Revisi:** Gasal 2026/2027  
**Unit Penerbit:** Senat Akademik dan Bagian Administrasi Akademik (BAAK) IT Del  
**Status Etika:** Fiktif akademik terstruktur, tanpa data personal riil, selaras UU PDP No. 27/2022.

---

## PASAL 1: TAHAPAN EVALUASI KEBERLANJUTAN STUDI
Institut Teknologi Del menerapkan evaluasi keberlanjutan studi ketat bertingkat (*academic gate system*) bagi seluruh program sarjana:

1. **Evaluasi Tahap I (Akhir Semester 2 / Tahun Pertama):**
   - Mahasiswa wajib mengumpulkan minimal **24 Satuan Kredit Semester (SKS)** mata kuliah lulus tanpa nilai E.
   - Indeks Prestasi Kumulatif (IPK) minimal adalah **2.00**.
   - Mahasiswa yang tidak memenuhi kriteria ini menerima Surat Peringatan Akademik Pertama (SP-1) dan masa percobaan studi selama satu semester.

2. **Evaluasi Tahap II (Akhir Semester 4 / Tahun Kedua):**
   - Mahasiswa wajib mengumpulkan minimal **48 SKS** mata kuliah lulus.
   - IPK minimal adalah **2.00**.
   - Apabila mahasiswa gagal mencapai syarat ini, mahasiswa dinyatakan kehilangan hak melanjutkan studi (Drop Out / Putus Studi) dari IT Del.

3. **Evaluasi Tahap Akhir (Batas Maksimum Masa Studi):**
   - Masa studi maksimum program Sarjana (S1) adalah **7 (tujuh) tahun akademik** atau 14 semester.
   - Kegagalan menyelesaikan seluruh kurikulum dalam batas masa studi mengakibatkan pemutusan studi otomatis.

## PASAL 2: MEKANISME PERINGATAN DINI DAN PENDAMPINGAN
1. Sistem Informasi Akademik secara otomatis menerbitkan notifikasi *academic probation* bagi mahasiswa dengan IPK per semester di bawah 2.00.
2. Dosen PA dan Tim Bimbingan Konseling Kampus wajib memanggil mahasiswa bersangkutan untuk menyusun rencana pemulihan akademik (*study remediation plan*).
3. Pengambilan SKS pada semester percobaan dibatasi maksimal 15 SKS.

## PASAL 3: PENETAPAN DAN PEMBERHENTIAN
1. Penetapan status Putus Studi (Drop Out) diputuskan melalui Rapat Dewan Dosen Fakultas dan disahkan melalui Surat Keputusan Rektor Institut Teknologi Del.
2. Keputusan Rektor bersifat final dan mengikat.
"""
    },
    {
        "doc_id": "SOP-FITE-01",
        "filename": "SOP-FITE-01_Pedoman_Pelaksanaan_Tugas_Akhir_dan_Sidang.md",
        "format": "md",
        "category": "SOP_AKADEMIK",
        "title": "SOP Pedoman Pelaksanaan Tugas Akhir, Seminar Proposal, dan Sidang Meja Hijau",
        "created_date": "2026-09-18",
        "content": """# STANDAR OPERASIONAL PROSEDUR PELAKSANAAN TUGAS AKHIR DAN SIDANG MEJA HIJAU
**Nomor Dokumen:** SOP-FITE-01-ITDEL-2026  
**Edisi/Revisi:** Gasal 2026/2027  
**Unit Penerbit:** Fakultas Informatika dan Teknik Elektro (FITE) IT Del  
**Disclaimer Privasi:** Dokumen korpus sintetis enterprise untuk pemodelan NLP & RAG (UU PDP No. 27/2022).

---

## 1. PRASYARAT PENDAFTARAN TUGAS AKHIR
1. Mahasiswa telah menyelesaikan sekurang-kurangnya **110 SKS** beban studi kurikulum Sarjana Sistem Informasi / Teknik Informatika.
2. Telah lulus mata kuliah Metodologi Penelitian dan Rekayasa Perangkat Lunak dengan nilai minimal C.
3. Memiliki Indeks Prestasi Kumulatif (IPK) sekurang-kurangnya **2.25**.
4. Tidak memiliki tunggakan biaya perkuliahan atau sanksi disiplin asrama aktif.

## 2. TAHAPAN TUGAS AKHIR
1. **Pengajuan Proposal dan Penetapan Pembimbing:**
   - Mahasiswa mengajukan topik penelitian melalui koordinator TA FITE.
   - Koordinator menetapkan Pembimbing Utama dan Pembimbing Pendamping berdasarkan kesesuaian bidang keahlian (roadmap riset dosen).
2. **Seminar Proposal (Sempro):**
   - Dilaksanakan setelah naskah proposal disetujui para pembimbing.
   - Diuji oleh minimal 2 (dua) orang dosen penguji independen.
3. **Seminar Kemajuan Riset (Pra-Sidang):**
   - Evaluasi kelayakan implementasi perangkat lunak atau model kecerdasan buatan minimal 75% selesai.
4. **Sidang Meja Hijau (Ujian Komprehensif Tugas Akhir):**
   - Ujian lisan tertutup di hadapan 3 dosen penguji dan dosen pembimbing.
   - Penilaian mencakup mutu naskah teknis (35%), demonstrasi perangkat lunak/model (35%), serta penguasaan materi dan argumentasi ilmiah (30%).

## 3. PERSYARATAN YUDISIUM DAN KELULUSAN
1. Naskah final telah melewati uji kemiripan (*similarity check*) Turnitin dengan persentase kemiripan maksimal **20%** di luar daftar pustaka dan lampiran.
2. Mahasiswa wajib mempublikasikan artikel ilmiah pada jurnal nasional terakreditasi SINTA atau konferensi internasional bereputasi IEEE/ACM, atau menyerahkan prototipe paten/HAKI terdaftar.
"""
    },
    {
        "doc_id": "SOP-KMS-02",
        "filename": "SOP-KMS-02_Pengajuan_Beasiswa_dan_Bantuan_Finansial.txt",
        "format": "txt",
        "category": "SOP_KEMAHASISWAAN",
        "title": "SOP Pengajuan Program Beasiswa dan Skema Bantuan Finansial Mahasiswa",
        "created_date": "2026-09-20",
        "content": """STANDAR OPERASIONAL PROSEDUR PENGAJUAN BEASISWA DAN BANTUAN FINANSIAL MAHASISWA
Nomor Dokumen: SOP-KMS-02-ITDEL-2026
Edisi Berlaku: Semester Gasal 2026/2027
Penerbit: Direktorat Kemahasiswaan dan Pengembangan Karir IT Del
Kepatuhan PDP: Dokumen fiktif simulasi enterprise AI, bebas dari data pribadi riil (UU No. 27/2022).

1. JENIS-JENIS PROGRAM BEASISWA
Institut Teknologi Del menyediakan beberapa skema dukungan pembiayaan pendidikan:
a. Beasiswa Prestasi Akademik Yayasan Pembina Del: Diberikan kepada mahasiswa peraih peringkat tertinggi paralel di setiap angkatan dengan IPK minimal 3.50.
b. Beasiswa Bantuan Ekonomi (Bursary Finansial): Ditujukan bagi mahasiswa dari keluarga prasejahtera yang berpotensi akademik tinggi dengan IPK minimal 2.75.
c. Beasiswa Kemitraan Industri dan BUMN: Disediakan oleh mitra korporasi terikat program magang dan rekrutmen kerja setelah kelulusan.

2. SYARAT ADMINISTRATIF PENGAJUAN
Mahasiswa pemohon beasiswa wajib melengkapi berkas verifikasi:
- Surat permohonan resmi kepada Direktur Kemahasiswaan.
- Slip gaji atau surat keterangan penghasilan orang tua dari instansi kerja atau kelurahan setempat.
- Fotokopi Kartu Keluarga dan bukti pembayaran rekening listrik/PBB 3 bulan terakhir.
- Salinan Kartu Hasil Studi (KHS) resmi berstempel fakultas.
- Surat rekomendasi dari Dosen Pembimbing Akademik yang menyatakan rekam jejak perilaku santun dan disiplin.

3. TATA CARA PENILAIAN DAN WAWANCARA
- Seleksi administratif dilakukan oleh Panitia Beasiswa Institusi.
- Mahasiswa yang lolos seleksi berkas wajib mengikuti wawancara komitmen karakter MarTuhan, Marroha, Marbisuk.
- Penerima beasiswa wajib mempertahankan capaian IPK minimal 3.00 setiap semester; apabila IPK turun di bawah 3.00 selama dua semester berturut-turut, status beasiswa dapat ditangguhkan atau dicabut permanen.
"""
    },
    {
        "doc_id": "SOP-TI-01",
        "filename": "SOP-TI-01_Kebijakan_Penggunaan_Jaringan_Internet_dan_SSO.txt",
        "format": "txt",
        "category": "SOP_FASILITAS",
        "title": "SOP Kebijakan Penggunaan Jaringan Internet, Akun Single Sign-On (SSO), dan Keamanan Siber",
        "created_date": "2026-09-22",
        "content": """STANDAR OPERASIONAL PROSEDUR KEBIJAKAN PENGGUNAAN JARINGAN INTERNET, AKUN SSO, DAN KEAMANAN SIBER
Nomor Dokumen: SOP-TI-01-ITDEL-2026
Berlaku: Tahun Akademik Gasal 2026/2027
Unit Penerbit: Direktorat Teknologi Informasi dan Komunikasi (DTIK) IT Del
Kepatuhan Regulasi: Simulasi operasional fiktif, selaras UU PDP No. 27/2022 dan SE Menkominfo No. 9/2023.

PASAL 1: IDENTITAS DIGITAL DAN AKUN SINGLE SIGN-ON (SSO)
1. Setiap mahasiswa dan staf resmi IT Del memperoleh akun Single Sign-On (SSO) dengan domain resmi @del.ac.id.
2. Kata sandi akun SSO wajib memiliki kompleksitas minimal 12 karakter yang memadukan huruf kapital, huruf kecil, angka, dan simbol khusus.
3. Pengguna dilarang membagikan kredensial akun kepada pihak lain mana pun. Segala aktivitas yang tercatat atas nama akun pengguna menjadi tanggung jawab hukum pemilik akun.

PASAL 2: PENGGUNAAN JARINGAN KAMPUS (DEL-WIFI & ETHERNET)
1. Jaringan internet kampus diutamakan untuk kepentingan proses belajar-mengajar, riset kecerdasan buatan, dan komunikasi kedinasan.
2. Setiap pengguna dibatasi kuota alokasi bandwidth wajar (Fair Usage Policy - FUP) sebesar 20 GB per hari.
3. Koneksi VPN pihak ketiga tanpa otorisasi DTIK dilarang di lingkungan jaringan intranet kampus.

PASAL 3: AKTIVITAS YANG DILARANG KERAS DAN SANKSI
1. Pengguna dilarang mengunduh atau menyebarkan konten bermuatan pornografi, perjudian daring, ujaran kebencian, atau konten bajakan hak cipta.
2. Dilarang menggunakan jaringan kampus untuk lalu lintas Peer-to-Peer (BitTorrent), penyerangan denial-of-service (DoS), pemindaian port jaringan, atau penambangan mata uang kripto (cryptocurrency mining).
3. Pelanggaran terhadap pasal ini berakibat pemblokiran MAC address perangkat, pencabutan akun SSO, dan pelaporan tindak pidana siber sesuai UU ITE yang berlaku di Republik Indonesia.
"""
    },
    {
        "doc_id": "SOP-PERPUS-01",
        "filename": "SOP-PERPUS-01_Layanan_Sirkulasi_dan_Akses_Repositori_Digital.txt",
        "format": "txt",
        "category": "SOP_FASILITAS",
        "title": "SOP Layanan Sirkulasi Koleksi Fisik dan Akses Repositori Digital Perpustakaan",
        "created_date": "2026-09-25",
        "content": """STANDAR OPERASIONAL PROSEDUR LAYANAN SIRKULASI KOLEKSI FISIK DAN REPOSITORI DIGITAL PERPUSTAKAAN
Nomor Dokumen: SOP-PERPUS-01-ITDEL-2026
Tahun Terbit: 2026
Penerbit: Unit Pelaksana Teknis (UPT) Perpustakaan Institut Teknologi Del
Pernyataan Etika: Dokumen contoh akademik fiktif untuk evaluasi RAG (UU PDP No. 27/2022).

1. JAM OPERASIONAL PERPUSTAKAAN
- Hari Senin s.d. Jumat: Pukul 08.00 - 17.00 WIB (Buka Layanan Penuh).
- Hari Sabtu: Pukul 08.30 - 13.00 WIB (Layanan Sirkulasi Terbatas).
- Hari Minggu dan Hari Libur Nasional: Tutup.

2. ATURAN PEMINJAMAN DAN PERPANJANGAN BUKU CETAK
- Mahasiswa aktif berhak meminjam paling banyak 3 (tiga) judul buku cetak dalam satu waktu peminjaman.
- Durasi peminjaman standar adalah 14 (empat belas) hari kalender.
- Peminjaman dapat diperpanjang sebanyak 1 (satu) kali perpanjangan selama 7 hari tambahan, dengan syarat buku tersebut tidak sedang dipesan (hold/reserved) oleh civitas lain.
- Keterlambatan pengembalian buku dikenakan denda administratif sebesar Rp 2.000 (dua ribu rupiah) per buku per hari keterlambatan.

3. AKSES REPOSITORI DIGITAL DAN TUGAS AKHIR
- Civitas akademika berhak mengakses koleksi e-journal internasional (IEEE Xplore, ScienceDirect, ACM Digital Library) melalui jaringan kampus atau remote access SSO.
- Naskah Tugas Akhir dan Tesis dalam Repositori Digital IT Del dilindungi oleh hak cipta institusi. Pengguna hanya diizinkan membaca bab pendahuluan dan abstrak secara publik; naskah lengkap hanya dapat diakses untuk kepentingan riset internal kampus.
- Mahasiswa tingkat akhir wajib menyerahkan salinan digital final naskah tugas akhir yang telah ditandatangani lengkap sebagai syarat penerbitan Surat Bebas Pustaka untuk yudisium.
"""
    },
    {
        "doc_id": "SOP-KMS-03",
        "filename": "SOP-KMS-03_Layanan_Klinik_Kampus_dan_Surat_Keterangan_Sakit.txt",
        "format": "txt",
        "category": "SOP_KEMAHASISWAAN",
        "title": "SOP Prosedur Pelayanan Kesehatan Klinik Kampus dan Validasi Surat Keterangan Sakit",
        "created_date": "2026-09-28",
        "content": """STANDAR OPERASIONAL PROSEDUR PELAYANAN KESEHATAN KLINIK KAMPUS DAN SURAT DISPENSASI SAKIT
Nomor Dokumen: SOP-KMS-03-ITDEL-2026
Masa Berlaku: Gasal 2026/2027
Unit Penerbit: Unit Pelayanan Kesehatan & Klinik Pratama IT Del
Kepatuhan PDP: Dokumen sintetis operasional institusi kampus, tanpa rekam medis riil (UU PDP No. 27/2022).

BAB I: PELAYANAN MEDIS DASAR
1. Klinik Pratama IT Del melayani rawat jalan medis dasar, pertolongan pertama pada kecelakaan (P3K), dan konsultasi kesehatan bagi seluruh mahasiswa, dosen, dan staf kampus.
2. Jam pelayanan dokter umum rawat jalan berlangsung setiap hari kerja pukul 08:00 - 16:00 WIB.
3. Layanan perawat jaga gawat darurat (emergency unit) dan ambulans kampus siaga selama 24 jam setiap hari untuk menangani kondisi mendesak di lingkungan asrama.

BAB II: TATA CARA PENERBITAN SURAT DISPENSASI SAKIT
1. Mahasiswa yang mengalami gangguan kesehatan sehingga tidak dapat mengikuti perkuliahan atau apel wajib memeriksakan diri langsung ke Klinik IT Del.
2. Surat Keterangan Sakit resmi (Surat Sakit) hanya diterbitkan oleh Dokter Klinik IT Del yang memiliki Surat Izin Praktik (SIP) sah.
3. Surat dispensasi istirahat di asrama (bed rest) berlaku paling lama 2 (dua) hari berturut-turut. Apabila kondisi belum membaik, dokter akan merujuk pasien ke Rumah Sakit Umum Daerah (RSUD) Porsea atau Balige.
4. Mahasiswa wajib menyerahkan salinan Surat Sakit Klinik kepada dosen pengampu mata kuliah dan Pembina Asrama dalam kurun waktu 1x24 jam sejak surat diterbitkan agar absensi kuliah dihitung sebagai izin medis sah.

BAB III: RUJUKAN RUMAH SAKIT DAN BIAYA KESEHATAN
1. Pasien yang memerlukan tindakan rawat inap atau pemeriksaan spesialis dirujuk menggunakan ambulans kampus didampingi oleh petugas medis dan pamong asrama.
2. Biaya pengobatan rujukan di luar tanggungan asuransi mahasiswa menjadi tanggung jawab orang tua / wali mahasiswa bersangkutan.
"""
    },
    {
        "doc_id": "SOP-SDM-01",
        "filename": "SOP-SDM-01_Beban_Kinerja_Dosen_dan_Kode_Etik_Pengajaran.txt",
        "format": "txt",
        "category": "SOP_SDM",
        "title": "SOP Standar Beban Kerja Dosen (BKD) dan Etika Profesional Pengajaran",
        "created_date": "2026-09-30",
        "content": """STANDAR OPERASIONAL PROSEDUR BEBAN KERJA DOSEN (BKD) DAN KODE ETIK PENGAJARAN
Nomor Dokumen: SOP-SDM-01-ITDEL-2026
Berlaku: Tahun Ajaran Gasal 2026/2027
Penerbit: Direktorat Sumber Daya Manusia dan Bagian Penjaminan Mutu IT Del
Kepatuhan Etika: Dokumen simulasi enterprise AI, tanpa data pribadi dosen riil (UU No. 27/2022).

1. DISTRIBUSI BEBAN KERJA DOSEN (BKD)
Sesuai standar pendidikan tinggi nasional dan penjaminan mutu IT Del:
- Setiap dosen tetap wajib menjalankan Tridharma Perguruan Tinggi dengan beban ekuivalen 12 hingga 16 SKS per semester.
- Alokasi beban pengajaran di kelas minimal 6 SKS dan maksimal 10 SKS untuk mempertahankan kualitas interaksi pedagogis.
- Beban penelitian dan pengabdian kepada masyarakat wajib dialokasikan minimal 3 SKS per semester.

2. KEWAJIBAN PERKULIAHAN DAN KEHADIRAN
- Dosen pengampu wajib memenuhi minimal 14 (empat belas) kali tatap muka perkuliahan terstruktur dalam satu semester, tidak termasuk pelaksanaan UTS dan UAS.
- Kehadiran dosen di kelas wajib tepat waktu sesuai jam yang tertera pada jadwal perkuliahan SIA.
- Apabila berhalangan hadir karena tugas kedinasan atau sakit, dosen wajib memberi tahu koordinator prodi dan mengajukan permohonan kelas pengganti minimal H-2 sesuai SOP-AKD-01.

3. KODE ETIK EVALUASI DAN NILAI
- Dosen wajib mengumumkan silabus, rencana pembelajaran semester (RPS), dan bobot penilaian pada minggu pertama perkuliahan.
- Nilai Ujian Tengah Semester (UTS) dan Ujian Akhir Semester (UAS) wajib diinput ke portal SIA IT Del selambat-lambatnya 7 (tujuh) hari kerja setelah ujian mata kuliah bersangkutan diselenggarakan.
- Dosen dilarang mengubah nilai akhir mahasiswa di luar mekanisme komplain nilai resmi yang diawasi oleh tim penjaminan mutu fakultas.
"""
    },
    {
        "doc_id": "REG-AKD-01",
        "filename": "REG-AKD-01_Pedoman_Pelanggaran_Akademik_dan_Sanksi_Disiplin.pdf",
        "format": "pdf",
        "category": "REGULASI",
        "title": "Pedoman Disiplin Akademik, Pencegahan Plagiarisme, dan Penegakan Sanksi Kecurangan",
        "created_date": "2026-10-02",
        "content": """PEDOMAN DISIPLIN AKADEMIK, PENCEGAHAN PLAGIARISME, DAN PENEGAKAN SANKSI KECURANGAN
Nomor Regulasi: REG-AKD-01-ITDEL-2026
Penerbit: Senat Akademik dan Komisi Kehormatan Disiplin Institut Teknologi Del
Pernyataan Privasi: Dokumen pedoman formal sintetis berstandar enterprise (UU PDP No. 27/2022).

BAB I: KLASIFIKASI PELANGGARAN AKADEMIK
1. Pelanggaran Ringan:
   - Terlambat memasuki ruang ujian tanpa alasan sah di atas 15 menit.
   - Tidak mengenakan seragam akademik resmi atau kartu identitas ujian pada saat ujian berlangsung.
   - Mengabaikan instruksi pengawas ujian mengenai penempatan tas dan alat komunikasi di depan kelas.

2. Pelanggaran Sedang:
   - Mencontek pekerjaan kawan atau memberi sontekan saat ujian kuis, UTS, atau UAS berlangsung.
   - Membawa catatan atau contekan ke dalam ruang ujian yang tidak mengizinkan open-book.
   - Melakukan plagiarisme pada tugas esai atau makalah perkuliahan dengan persentase kesamaan 25% hingga 40%.

3. Pelanggaran Berat:
   - Mempekerjakan joki (pihak ketiga) untuk menyelesaikan tugas pemrograman, ujian, atau tugas akhir.
   - Memalsukan tanda tangan dosen, pengesahan nilai, atau surat keterangan izin sakit klinik.
   - Membobol atau memodifikasi data pada basis data Sistem Informasi Akademik (SIA).
   - Melakukan fabrikasi atau falsifikasi data hasil pengujian eksperimen laboratorium.

BAB II: TATA CARA PENETAPAN SANKSI DISIPLIN
1. Sanksi Pelanggaran Ringan: Teguran tertulis oleh Pengawas Ujian dan pengurangan nilai tugas sebesar 20%.
2. Sanksi Pelanggaran Sedang: Pembatalan nilai mata kuliah bersangkutan dengan pemberian nilai akhir E (Gagal Total) pada semester berjalan.
3. Sanksi Pelanggaran Berat: Skorsing akademik selama 1 (satu) hingga 2 (dua) semester penuh, atau pemberhentian tidak dengan hormat (Drop Out permanen) dari IT Del atas rekomendasi Dewan Kehormatan Etik.
"""
    },
    {
        "doc_id": "REG-AKD-02",
        "filename": "REG-AKD-02_Sistem_Penilaian_Konversi_dan_Ujian_Remedial.pdf",
        "format": "pdf",
        "category": "REGULASI",
        "title": "Pedoman Sistem Penilaian, Skala Konversi Huruf Mutu, dan Pelaksanaan Ujian Remedial",
        "created_date": "2026-10-05",
        "content": """PEDOMAN SISTEM PENILAIAN, SKALA KONVERSI HURUF MUTU, DAN UJIAN REMEDIAL
Nomor Regulasi: REG-AKD-02-ITDEL-2026
Penerbit: Bagian Penjaminan Mutu Akademik Institut Teknologi Del
Landasan: Standar Nasional Pendidikan Tinggi (SN-Dikti) & Kepatuhan UU PDP No. 27/2022.

PASAL 1: BOBOT EVALUASI DAN KOMPONEN PENILAIAN
1. Penilaian hasil belajar mahasiswa pada setiap mata kuliah di IT Del bersifat komprehensif dan multi-komponen:
   - Kuis dan Tugas Terstruktur Mandiri: Bobot 20%
   - Praktikum Laboratorium dan Proyek Berkelanjutan: Bobot 25%
   - Ujian Tengah Semester (UTS): Bobot 25%
   - Ujian Akhir Semester (UAS): Bobot 30%
2. Dosen dilarang menentukan kelulusan mahasiswa hanya berdasarkan satu instrumen ujian tunggal.

PASAL 2: SKALA NILAI ANGKA DAN KONVERSI HURUF MUTU
Skala konversi nilai akhir mata kuliah Institut Teknologi Del diatur sebagai berikut:
- Nilai Angka 85.00 - 100.00 : Huruf Mutu A (Bobot 4.00 - Sangat Istimewa)
- Nilai Angka 77.50 - 84.99  : Huruf Mutu AB (Bobot 3.50 - Istimewa)
- Nilai Angka 70.00 - 77.49  : Huruf Mutu B (Bobot 3.00 - Sangat Baik)
- Nilai Angka 62.50 - 69.99  : Huruf Mutu BC (Bobot 2.50 - Baik)
- Nilai Angka 55.00 - 62.49  : Huruf Mutu C (Bobot 2.00 - Cukup / Batas Lulus)
- Nilai Angka 40.00 - 54.99  : Huruf Mutu D (Bobot 1.00 - Kurang / Tidak Lulus)
- Nilai Angka 0.00 - 39.99   : Huruf Mutu E (Bobot 0.00 - Gagal Mutlak)

PASAL 3: KETENTUAN UJIAN REMEDIAL (PERBAIKAN NILAI)
1. Ujian remedial hanya diberikan kepada mahasiswa yang memperoleh huruf mutu D atau C pada semester reguler.
2. Mahasiswa dengan nilai E atau memiliki kehadiran di bawah 75% tidak berhak mengikuti remedial dan wajib mengulang mata kuliah secara penuh di semester reguler berikutnya.
3. Nilai akhir maksimum yang dapat diperoleh setelah menempuh ujian remedial adalah nilai C (bobot 2.00).
"""
    },
    {
        "doc_id": "PANDUAN-KMS-01",
        "filename": "PANDUAN-KMS-01_Tata_Cara_Izin_Bermalam_dan_Pesiar.pdf",
        "format": "pdf",
        "category": "PANDUAN",
        "title": "Panduan Prosedur Pengajuan Izin Bermalam (IB) dan Pesiar Akhir Pekan Mahasiswa",
        "created_date": "2026-10-08",
        "content": """PANDUAN PROSEDUR PENGAJUAN IZIN BERMALAM (IB) DAN PESIAR AKHIR PEKAN MAHASISWA
Nomor Panduan: PANDUAN-KMS-01-ITDEL-2026
Penerbit: Bagian Pembinaan Asrama dan Kedisiplinan Mahasiswa IT Del
Landasan Privasi: Simulasi panduan kampus asrama, tanpa data personal riil, selaras UU PDP No. 27/2022.

BAGIAN I: KETENTUAN PESIAR AKHIR PEKAN
1. Pesiar adalah izin meninggalkan lingkungan kampus IT Del pada akhir pekan tanpa menginap di luar asrama.
2. Waktu pelaksanaan pesiar dibuka pada hari Sabtu mulai pukul 13:00 WIB (setelah apel siang) hingga pukul 17:30 WIB.
3. Seluruh mahasiswa peserta pesiar wajib kembali ke dalam gerbang kampus dan melakukan pencatatan sidik jari/kartu asrama sebelum pukul 17:30 WIB.
4. Keterlambatan kepulangan pesiar dikategorikan sebagai pelanggaran disiplin jam masuk gerbang (Gate Violation).

BAGIAN II: KETENTUAN IZIN BERMALAM (IB)
1. Izin Bermalam (IB) adalah dispensasi resmi menginap di luar asrama bersama orang tua atau wali resmi pada akhir pekan atau libur nasional yang disetujui.
2. Frekuensi IB reguler diberikan maksimal 1 (satu) kali per bulan untuk mahasiswa tahun pertama, dan maksimal 2 (dua) kali per bulan untuk mahasiswa tingkat atas.
3. Pengajuan IB wajib dilakukan secara daring melalui modul e-Permit pada aplikasi kampus selambat-lambatnya hari Kamis pukul 15:00 WIB.
4. Mahasiswa wajib melampirkan konfirmasi persetujuan dari orang tua/wali via pesan resmi atau panggilan telepon verifikasi oleh pamong asrama.
5. Waktu kembali ke asrama pasca-IB selambat-lambatnya hari Minggu pukul 17:30 WIB sebelum apel malam asrama dimulai.

BAGIAN III: SANKSI KETERLAMBATAN DAN PELANGGARAN IB
1. Mahasiswa yang terlambat kembali ke asrama tanpa pemberitahuan sah dikenakan sanksi denda poin pelanggaran kedisiplinan dan pencabutan hak pesiar selama 2 pekan berturut-turut.
2. Mahasiswa yang terbukti bermalam di luar asrama tanpa surat izin resmi IB dijatuhi sanksi disiplin asrama tingkat sedang berupa penugasan pembinaan fisik dan pemanggilan orang tua ke kampus.
"""
    }
]


def create_pdf(filename: Path, title: str, text_content: str):
    """Generate a clean, structured PDF using ReportLab with headers and footers."""
    doc = SimpleDocTemplate(
        str(filename),
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#004B87'),
        spaceAfter=12
    )
    
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        spaceAfter=8,
        textColor=colors.HexColor('#222222')
    )
    
    header_style = ParagraphStyle(
        'DocHeader',
        parent=styles['Heading2'],
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#1E3A8A'),
        spaceBefore=10,
        spaceAfter=6
    )

    story = []
    story.append(Paragraph(f"<b>INSTITUT TEKNOLOGI DEL</b> - DOKUMEN RESMI", ParagraphStyle('InstHeader', parent=styles['Normal'], fontSize=8, textColor=colors.gray, spaceAfter=8)))
    story.append(Paragraph(f"<b>{title}</b>", title_style))
    story.append(Spacer(1, 10))

    lines = text_content.strip().split("\n")
    for line in lines:
        line_str = line.strip()
        if not line_str:
            story.append(Spacer(1, 4))
            continue
        if line_str.startswith("BAB ") or line_str.startswith("PASAL ") or line_str.startswith("BAGIAN "):
            story.append(Paragraph(f"<b>{line_str}</b>", header_style))
        elif line_str.startswith("Nomor ") or line_str.startswith("Penerbit:") or line_str.startswith("Pernyataan"):
            story.append(Paragraph(f"<i>{line_str}</i>", ParagraphStyle('SubMeta', parent=body_style, fontSize=8, textColor=colors.darkgray)))
        else:
            # Escape XML entities for ReportLab
            clean_line = line_str.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(clean_line, body_style))

    # Add repeated footer text on document for realistic header/footer cleaning test
    def add_page_decorations(canvas, document):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.gray)
        canvas.drawString(54, 30, "Institut Teknologi Del - Sistem Manajemen Pengetahuan Enterprise")
        canvas.drawRightString(612 - 54, 30, f"Halaman {canvas.getPageNumber()} dari 2")
        canvas.restoreState()

    doc.build(story, onFirstPage=add_page_decorations, onLaterPages=add_page_decorations)


def main():
    CORPUS_DIR.mkdir(parents=True, exist_ok=True)
    manifest_records = []

    print(f"Generating {len(DOCUMENTS)} enterprise documents in {CORPUS_DIR}...")
    for doc in DOCUMENTS:
        file_path = CORPUS_DIR / doc["filename"]
        content = doc["content"].strip()
        
        if doc["format"] in ["md", "txt"]:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content + "\n")
        elif doc["format"] == "pdf":
            create_pdf(file_path, doc["title"], content)

        word_count = len(content.split())
        manifest_records.append({
            "doc_id": doc["doc_id"],
            "title": doc["title"],
            "category": doc["category"],
            "format": doc["format"],
            "filename": doc["filename"],
            "word_count": word_count,
            "created_date": doc["created_date"],
            "source_file": f"data/corpus/{doc['filename']}",
            "organization": "Institut Teknologi Del",
            "compliance": "UU PDP No. 27/2022 (Synthetic Enterprise Data)"
        })
        print(f"  [OK] {doc['doc_id']}: {doc['filename']} ({doc['format'].upper()}, ~{word_count} words)")

    # Save manifest JSON
    with open(MANIFEST_JSON, "w", encoding="utf-8") as f:
        json.dump(manifest_records, f, indent=2, ensure_ascii=False)
    print(f"[OK] Saved JSON manifest: {MANIFEST_JSON}")

    # Save manifest CSV
    fieldnames = ["doc_id", "title", "category", "format", "filename", "word_count", "created_date", "source_file", "organization", "compliance"]
    with open(MANIFEST_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(manifest_records)
    print(f"[OK] Saved CSV manifest: {MANIFEST_CSV}")


if __name__ == "__main__":
    main()
