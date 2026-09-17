import sys
from pathlib import Path

# Baris ini memastikan folder src terbaca langsung oleh Python
sys.path.insert(0, str(Path(__file__).resolve().parent))

from del_academic_navigator.rules import calculate_room_cost, is_lead_time_valid
from search.graph import AcademicScheduleGraph
from search.scheduler import a_star_search


def main():
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


if __name__ == "__main__":
    main()