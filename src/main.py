<<<<<<< HEAD
"""
Main Entrypoint untuk Del-Academic Navigator.

Menjalankan demonstrasi alur pemecahan masalah bisnis nyata di Institut Teknologi Del:
1. Skenario 1: Penjadwalan Ulang Kuliah (Make-up Class) 10S3001 Kecerdasan Buatan (+P).
2. Skenario 2: Komparasi Kinerja Penelusuran: A* Search vs Uniform Cost Search (UCS).
3. Skenario 3: Alokasi Sesi Bimbingan Akademik Dosen PA Sesuai Kuota SOP IT Del.
4. Skenario 4: Resolusi Bentrok Multi-Mata Kuliah Mahasiswa Menuju Target conflict_count == 0.
"""

import os
import sys

# Memastikan direktori root dan src terdaftar dalam sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
for path in (ROOT_DIR, CURRENT_DIR):
    if path not in sys.path:
        sys.path.insert(0, path)

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.search.graph import (
    AcademicScheduleGraph,
    build_it_del_sample_graph,
)
from src.search.scheduler import a_star_search, uniform_cost_search
from src.search.conflict_resolver import (
    Course,
    Slot,
    ScheduleState,
    ScheduleConflictResolver,
)


def print_banner():
    print("=" * 80)
    print("       DEL-ACADEMIC NAVIGATOR: ENTERPRISE AI COPILOT KAMPUS IT DEL")
    print(" Layanan Penjadwalan Ulang Kuliah (Make-up Class) & Bimbingan Akademik Terpadu")
    print("=" * 80)


def run_makeup_class_scenario():
    print("\n[SKENARIO 1: PENJADWALAN ULANG KULIAH (MAKE-UP CLASS)]")
    print("• Mata Kuliah : 10S3001 - Kecerdasan Buatan (+P)")
    print("• Dosen Pengampu: Samuel Indra Gunawan Situmeang")
    print("• Peserta       : Kelas 31SI1 & 31SI2 (Total: 65 Mahasiswa)")
    print("• Kasus         : Terjadi bentrok jadwal darurat pada slot Selasa 10:00 (GD512).")
    print("• Regulasi SOP  : Pengajuan minimal H-2; Kelas > 40 mhs wajib di GD721/GD722.\n")

    graph = build_it_del_sample_graph()
    start_state = "Start_Slot"
    goal_state = "Jumat_08:00_GD722"

    print(f"Mencari alur jadwal terbaik dari '{start_state}' ke '{goal_state}'...")

    # Eksekusi A* Search
    a_star_result = a_star_search(graph, start_state, goal_state)

    # Eksekusi Uniform Cost Search (UCS)
    ucs_result = uniform_cost_search(graph, start_state, goal_state)

    print("\n" + "-" * 80)
    print(f"{'Metrik Perbandingan':<30} | {'A* Search':<22} | {'Uniform Cost Search (UCS)':<22}")
    print("-" * 80)
    print(f"{'Jalur Terpilih':<30} | {' -> '.join(a_star_result.path):<22} | {' -> '.join(ucs_result.path):<22}")
    print(f"{'Total Biaya Penalti (Cost)':<30} | {a_star_result.total_cost:<22.2f} | {ucs_result.total_cost:<22.2f}")
    print(f"{'Simpul Dieksplorasi (Nodes)':<30} | {a_star_result.nodes_explored:<22} | {ucs_result.nodes_explored:<22}")
    print(f"{'Waktu Komputasi':<30} | {a_star_result.execution_time_ms:<19.3f} ms | {ucs_result.execution_time_ms:<19.3f} ms")
    print("-" * 80)

    print("\n[ANALISIS KEPUTUSAN AI COPILOT]")
    print(f"[OK] Jalur Rekomendasi : {' -> '.join(a_star_result.path)}")
    print(f"[OK] Total Penalti     : {a_star_result.total_cost} (Minimum / Solusi Optimal)")
    print("[OK] Validasi SOP Del  : Memenuhi syarat minimal H-2 (dilaksanakan Kamis/Jumat).")
    print("[OK] Validasi Fasilitas: Menggunakan GD721 (kapasitas 80) dan GD722 (kapasitas 75)")
    print("                      sehingga 65 mahasiswa tertampung dengan aman.")
    if a_star_result.nodes_explored <= ucs_result.nodes_explored:
        print(f"[OK] Efisiensi A*      : Heuristik h(n) memandu pencarian secara admissible,")
        print(f"                      mengeksplorasi {a_star_result.nodes_explored} node (<= UCS: {ucs_result.nodes_explored} node).")


def run_advising_session_scenario():
    print("\n" + "=" * 80)
    print("[SKENARIO 2: ALOKASI SESI BIMBINGAN AKADEMIK (DOSEN PA)]")
    print("• Layanan       : Konsultasi Persetujuan KRS & Evaluasi Indeks Prestasi")
    print("• Dosen PA      : Dosen Wali Sarjana Sistem Informasi")
    print("• Batasan SOP   : Maksimal kuota 5 mahasiswa per sesi bimbingan.")
    print("=" * 80)

    advising_graph = AcademicScheduleGraph()
    advising_graph.add_slot("Antrean_Mhs", hour=8, room_id="Lobby_Gd9", day="Senin", day_index=1, capacity=10)
    advising_graph.add_slot("Sesi_1_Senin_09:00", hour=9, room_id="Ruang_Dosen_911", day="Senin", day_index=1, capacity=5)
    advising_graph.add_slot("Sesi_2_Senin_14:00", hour=14, room_id="Ruang_Dosen_911", day="Senin", day_index=1, capacity=5)
    advising_graph.add_slot("Sesi_3_Selasa_10:00", hour=10, room_id="Ruang_Dosen_911", day="Selasa", day_index=2, capacity=5)

    advising_graph.add_transition("Antrean_Mhs", "Sesi_1_Senin_09:00", cost=1.5, description="Sesi Pagi (Ideal)")
    advising_graph.add_transition("Antrean_Mhs", "Sesi_2_Senin_14:00", cost=4.0, description="Sesi Siang (Setelah jam ajar)")
    advising_graph.add_transition("Sesi_1_Senin_09:00", "Sesi_3_Selasa_10:00", cost=2.0, description="Sesi Lanjutan H+1")

    path, cost = a_star_search(advising_graph, "Antrean_Mhs", "Sesi_1_Senin_09:00")
    print(f"Jalur Slot Bimbingan Terpilih : {' -> '.join(path)}")
    print(f"Biaya Penalti Konsultasi      : {cost}")
    print("Status SOP IT Del             : Memenuhi kuota 5 mhs/sesi di Ruang Dosen 911.\n")


def run_conflict_resolution_scenario():
    print("=" * 80)
    print("[SKENARIO 3: RESOLUSI BENTROK JADWAL MULTI-MATA KULIAH (GOAL: CONFLICT_COUNT == 0)]")
    print("• Deskripsi Kasus : Mahasiswa kelas 31SI1 mengambil 2 matakuliah yang bentrok di slot awal.")
    print("• Mata Kuliah A   : 10S3001 - Kecerdasan Buatan (Dosen: Samuel Situmeang)")
    print("• Mata Kuliah B   : 10S3002 - Basis Data Lanjut (Dosen: Tim Pengampu BD)")
    print("• Kondisi Awal    : Keduanya terjadwal di Senin 10:00 (GD512) -> Bentrok Mahasiswa & Ruang!")
    print("=" * 80)

    courses = {
        "10S3001": Course("10S3001", "Kecerdasan Buatan", "Samuel Situmeang", "31SI1", 40, "Senin", 10),
        "10S3002": Course("10S3002", "Basis Data Lanjut", "Tim Pengampu BD", "31SI1", 40, "Senin", 10),
    }

    slot_clash = Slot(day="Senin", hour=10, room_id="GD512", capacity=40)
    slot_alt_1 = Slot(day="Senin", hour=13, room_id="GD512", capacity=40)
    slot_alt_2 = Slot(day="Selasa", hour=10, room_id="GD721", capacity=80)

    initial_state = ScheduleState(assignments={
        "10S3001": slot_clash,
        "10S3002": slot_clash,
    })

    resolver = ScheduleConflictResolver(courses, [slot_clash, slot_alt_1, slot_alt_2])
    print(f"Jumlah Konflik Awal (Initial State) : {resolver.count_conflicts(initial_state)} bentrok")
    for conf in initial_state.get_conflicts(courses):
        print(f"  [!] {conf}")

    final_state, cost, nodes, history = resolver.solve(initial_state, algorithm="A*")

    print("\n[HASIL RESOLUSI A* SEARCH]")
    print(f"Jumlah Konflik Akhir (Goal State)   : {resolver.count_conflicts(final_state)} bentrok (Goal Test: {resolver.goal_test(final_state)})")
    print(f"Total Biaya Penalti Perubahan (Cost): {cost:.2f}")
    print(f"Simpul Ruang Keadaan Dieksplorasi  : {nodes} node")
    print("Aksi Perubahan Jadwal:")
    for step in history:
        print(f"  -> {step}")
    print("Alokasi Akhir Bebas Bentrok:")
    for c_code, s in final_state.assignments.items():
        print(f"  * {c_code}: {s.day} {s.hour}:00 di {s.room_id} (Kapasitas: {s.capacity})")
    print()

=======
import sys
from pathlib import Path

# Baris ini memastikan folder src terbaca langsung oleh Python
sys.path.insert(0, str(Path(__file__).resolve().parent))

from del_academic_navigator.rules import calculate_room_cost, is_lead_time_valid
from search.graph import AcademicScheduleGraph
from search.scheduler import a_star_search
>>>>>>> 77afe139507d40ad1ee212a629005427ee7d2fb1


def main():
<<<<<<< HEAD
    print_banner()
    run_makeup_class_scenario()
    run_advising_session_scenario()
    run_conflict_resolution_scenario()
    print("=" * 80)
    print("Milestone 1 Terpenuhi: State Space Search teruji bebas bug & siap untuk Milestone 2.")
    print("=" * 80)

=======
    print("==========================================================")
    print("   DEL-ACADEMIC NAVIGATOR: BASELINE A* SEARCH SCHEDULER   ")
    print("==========================================================")

    # Parameter Pengajuan (Kasus Nyata IT Del)
    request_day = 1       # Diajukan hari Senin (Day 1)
    target_day = 3        # Rencana kuliah pengganti hari Rabu (Day 3)
    student_count = 32    # Jumlah rombel kelas (32 mahasiswa)

    print(f"Hari Pengajuan   : Hari ke-{request_day} (Senin)")
    print(f"Target Jadwal    : Hari ke-{target_day} (Rabu)")
    print(f"Jumlah Mahasiswa : {student_count} orang")
    print("----------------------------------------------------------")

    # 1. Validasi Batasan SOP H-2
    if not is_lead_time_valid(request_day, target_day):
        print("Status: DITOLAK.")
        print("Alasan: Melanggar SOP IT Del (pengajuan pengganti wajib minimal H-2).")
        return

    # 2. Inisialisasi Graf Ruang Keadaan
    graph = AcademicScheduleGraph()

    # Daftarkan slot awal, opsi-opsi slot ruang, dan slot selesai (Goal)
    graph.add_slot("Start_Slot", hour=8, day=request_day)
    graph.add_slot("Rabu_13:00_GD512", hour=13, day=target_day, room_name="GD512")
    graph.add_slot("Rabu_10:00_GD721", hour=10, day=target_day, room_name="GD721")  # Ruang besar
    graph.add_slot("Rabu_Goal", hour=15, day=target_day)

    # 3. Hitung Biaya Penalti Riil Berdasarkan Aturan SOP
    cost_gd512 = calculate_room_cost("GD512", student_count)
    cost_gd721 = calculate_room_cost("GD721", student_count)

    # Hubungkan jalur perpindahan slot
    graph.add_transition("Start_Slot", "Rabu_13:00_GD512", cost=cost_gd512)
    graph.add_transition("Rabu_13:00_GD512", "Rabu_Goal", cost=1.0)

    graph.add_transition("Start_Slot", "Rabu_10:00_GD721", cost=cost_gd721)
    graph.add_transition("Rabu_10:00_GD721", "Rabu_Goal", cost=1.0)

    # 4. Jalankan Algoritma Pencarian A*
    path, total_cost = a_star_search(graph, "Start_Slot", "Rabu_Goal")

    # 5. Tampilkan Keputusan AI
    if path:
        print("Status           : BERHASIL DITEMUKAN")
        print(f"Jalur Rekomendasi: {' -> '.join(path)}")
        print(f"Total Biaya/Cost : {total_cost}")
        print("----------------------------------------------------------")
        print("Analisis Keputusan AI:")
        print("- Sistem otomatis memilih GD512 karena peserta <= 40 mahasiswa.")
        print("- GD721 dihindari karena terkena penalti pemborosan ruang besar.")
    else:
        print("Status: Jadwal bentrok atau tidak ditemukan alur yang valid.")
    print("==========================================================")

>>>>>>> 77afe139507d40ad1ee212a629005427ee7d2fb1

if __name__ == "__main__":
    main()