# Del-Academic Navigator

Enterprise AI Copilot untuk Layanan Bimbingan Akademik dan Penjadwalan Ulang Kuliah Kampus IT Del.

## 1. Spesifikasi Formal PEAS
- **Performance Measure:** Schedule zero-conflict, minimasi penalti jam/hari pengganti, presisi rujukan SOP akademik.
- **Environment:** Diskrit, Deterministik, Statis, Sepenuhnya Teramati (Ruang Jadwal Master).
- **Actuators:** Opsi slot perkuliahan pengganti, rekomendasi slot bimbingan dosen.
- **Sensors:** Teks kueri pengguna, data master jadwal (JSON), dokumen SOP akademik.

## 2. Cara Menjalankan
```bash
# Instal dependensi via uv
uv sync

# Jalankan baseline A* search
uv run python src/main.py

# Jalankan pengujian otomatis
uv run pytest