# Tugas 02 — Milestone 2: Business Constraint Solver

## Ringkasan solusi

Del-Academic Navigator memodelkan penjadwalan kuliah pengganti sebagai
**Constraint Satisfaction Problem (CSP)** dan mencari penugasan yang memenuhi
seluruh aturan keras menggunakan **AC-3, backtracking, MRV, degree heuristic,
LCV, dan forward checking**. Contoh bisnis dapat dijalankan bersama simulasi
lain melalui `uv run python src/main.py`; pengujian terotomasi dijalankan dengan
`uv run pytest`.

## Formulasi CSP formal

Masalah direpresentasikan sebagai \(P=(X,D,C)\):

| Komponen | Definisi pada penjadwalan akademik |
|---|---|
| Variabel \(X\) | Satu variabel untuk setiap mata kuliah yang perlu dijadwalkan, dengan `course_id` sebagai identitas unik. |
| Domain \(D_i\) | Kandidat `ScheduleSlot` untuk mata kuliah \(i\), setelah kandidat yang melanggar SOP individual dibuang. |
| Batasan \(C\) | Untuk setiap pasangan mata kuliah, slot yang bertabrakan ditolak bila keduanya memakai dosen, cohort mahasiswa, atau ruang yang sama. |

Aturan individual yang membentuk domain:

1. Slot kuliah dimulai paling cepat pukul 08.00 dan berakhir paling lambat
   pukul 17.00.
2. Slot tidak boleh beririsan dengan istirahat wajib 12.00–13.00.
3. Pengajuan harus memiliki tenggang minimal H-2 (`day_offset >= 2`).
4. Kapasitas ruang harus cukup untuk jumlah mahasiswa; untuk ruangan di master
   IT Del, kapasitas slot harus sesuai dengan data master ruangan.
5. Kuliah dengan lebih dari 40 mahasiswa hanya boleh memakai GD721 atau GD722.
6. Kuliah praktikum yang memerlukan laboratorium hanya boleh memakai slot lab.

Aturan antarkuliah untuk slot pada hari yang sama:

\[
\operatorname{conflict}(i,j) =
\operatorname{overlap}(i,j) \land
\bigl(\operatorname{sameLecturer} \lor
\operatorname{sharedCohort} \lor
\operatorname{sameRoom}\bigr)
\]

Solver menerima domain sebagai input CSP umum. Aturan bisnis diterapkan sebelum
pencarian dalam `build_academic_schedule_csp`; constraint antarkuliah
direpresentasikan sebagai `BinaryConstraint`, bukan pemeriksaan hasil setelah
pencarian.

## Algoritma dan konvergensi

1. **AC-3:** antrean busur berarah \(X_i \to X_j\); `revise` membuang nilai
   domain \(X_i\) yang tidak mempunyai satu pun nilai pendukung di \(X_j\).
   Jika domain menjadi kosong, CSP dinyatakan tidak konsisten. Busur diproses
   dengan `deque`, dan busur yang sudah antre tidak dimasukkan berulang kali.
2. **Backtracking:** memilih variabel belum terisi, mencoba nilai yang
   konsisten terhadap assignment, lalu melanjutkan secara rekursif. Assignment
   dibatalkan saat cabang tidak menghasilkan solusi.
3. **MRV + degree:** pilih variabel dengan domain tersisa terkecil; jika seri,
   pilih variabel dengan tetangga belum terisi terbanyak.
4. **LCV:** coba nilai yang menghapus paling sedikit kandidat variabel tetangga
   terlebih dahulu.
5. **Forward checking:** setelah nilai dipilih, hapus nilai yang tidak
   kompatibel dari domain tetangga yang belum ditugaskan. Domain cabang disalin,
   sehingga backtracking tidak mencemari state cabang lain.

AC-3 memiliki worst-case \(O(e d^3)\), dengan \(e\) jumlah pasangan variabel
yang dibatasi dan \(d\) ukuran domain maksimum. Backtracking bersifat
eksponensial pada kasus terburuk (\(O(d^n)\)); heuristik dan propagasi
mengurangi ruang pencarian, tetapi tidak mengubah worst-case tersebut. Untuk
masalah CSP biner hingga, pencarian lengkap akan mengembalikan solusi yang
memenuhi semua constraint bila solusi ada, dan `None` bila tidak ada.

Solver ini mencari **solusi layak pertama**, bukan meminimalkan penalti. Jika
jadwal perlu dioptimalkan berdasarkan biaya preferensi, tambahkan objective
weighted-CSP/branch-and-bound atau gunakan mesin optimasi A*/UCS yang sudah
menjadi bagian terpisah dari proyek. Hard constraints tidak boleh diubah
menjadi penalti lunak.

## Analisis konvergensi empiris

Perbandingan berikut diukur pada skenario 3 mata kuliah yang dijalankan CLI.
Jumlah node/backtrack/pruning bersifat deterministik; waktu eksekusi tidak
dicantumkan karena berubah antar mesin. Ini ilustrasi bahwa heuristik mengurangi
pencarian pada kasus tersebut, bukan klaim bahwa konfigurasi selalu lebih cepat
untuk setiap CSP.

| Konfigurasi | Solusi layak | Nilai dicoba (nodes) | Backtrack | Domain pruning |
|---|---:|---:|---:|---:|
| AC-3 + MRV + LCV + forward checking | Ya | 3 | 0 | 1 |
| Tanpa preprocessing AC-3 | Ya | 3 | 0 | 1 |
| Tanpa forward checking | Ya | 3 | 0 | 0 |
| Backtracking dasar tanpa propagasi/heuristik | Ya | 5 | 0 | 0 |

## Hasil demonstrasi bisnis

Skenario pada `src/main.py` menjadwalkan dua mata kuliah cohort gabungan
31SI1/31SI2 (58 mahasiswa) serta satu praktikum. Domain menyaring GD935
(kapasitas 40) untuk kelas besar, slot H+1, dan ruang non-lab untuk praktikum.
Constraint pasangan selanjutnya mencegah bentrok dosen, mahasiswa, dan ruang.
Program mencetak hasil jadwal beserta jumlah node, backtrack, domain pruning,
dan waktu eksekusi aktual; assignment dinyatakan berhasil hanya bila seluruh
constraint terpenuhi.

## Pengujian dan bukti kebenaran

Jalankan:

```bash
uv run pytest tests/test_solver.py
uv run pytest
uv run python src/main.py
```

| Kelompok uji | Pemeriksaan |
|---|---|
| Benchmark | Pewarnaan peta Australia menghasilkan pewarnaan yang valid. |
| Kasus bisnis | Alokasi ruang tidak konflik; kandidat kapasitas, H-2, waktu operasional, makan siang, dan kebutuhan lab divalidasi. |
| Konsistensi AC-3 | Propagasi berantai memangkas domain sampai fixpoint tanpa mengubah domain input. |
| Kasus ekstrem | Domain kosong, konflik domain singleton, dan konflik ruang yang tidak mungkin menghasilkan status tidak terpecahkan. |
| Orientasi constraint | Constraint asimetris tetap diperiksa dalam urutan variabel saat constraint dideklarasikan. |
| Kelengkapan solver | Seluruh 27 kombinasi constraint equality/inequality pada CSP tiga variabel dibandingkan dengan enumerasi brute-force; hasil AC-3/backtracking harus setara. |
| Pilihan propagasi | Kasus oracle dijalankan dengan konfigurasi default, tanpa preprocessing AC-3, dan tanpa forward checking. |
| Validasi input | Variabel ganda, domain tidak lengkap, dan constraint yang merujuk variabel tidak dikenal ditolak eksplisit. |

## Kesesuaian rubrik penilaian

| Komponen rubrik | Bobot | Bukti untuk target “100 (Sangat Baik)” |
|---|---:|---|
| Pemodelan batasan bisnis formal | 30% | \(X,D,C\) didokumentasikan; seluruh aturan SOP individu menjadi domain dan bentrok dosen/cohort/ruang menjadi constraint biner yang dapat diuji. |
| Kebenaran algoritma & konvergensi solver | 40% | Implementasi AC-3 modular, antrean efisien, backtracking lengkap, MRV/degree/LCV/forward checking, deteksi domain kosong, serta pembandingan exhaustive dengan brute force. |
| Pengujian sensitivitas & kerapian modul | 30% | Uji kasus ekstrem, perbedaan orientasi relasi, input invalid, validasi SOP, dan konfigurasi propagasi; dokumentasi mencantumkan kompleksitas, cara menjalankan, dan batas klaim optimasi. |

## Modul yang diserahkan

- `src/search/solver.py` — CSP generik, AC-3 dan backtracking.
- `src/del_academic_navigator/csp_schedule.py` — formulasi constraint bisnis
  penjadwalan akademik.
- `src/main.py` — demonstrasi milestone 2 yang dapat dijalankan.
- `tests/test_solver.py` — pengujian unit, kasus bisnis, dan oracle brute-force.
