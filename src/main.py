from search.graph import AcademicScheduleGraph
from search.scheduler import a_star_search

def main():
    print("=== DEL-ACADEMIC NAVIGATOR: BASELINE A* SEARCH ===")
    
    graph = AcademicScheduleGraph()

    # Inisialisasi Ruang Keadaan (Slot Waktu & Ruangan IT Del)
    graph.add_slot("Start_Slot", hour=8, room_id=0)
    graph.add_slot("Senin_10:00_GD721", hour=10, room_id=721)
    graph.add_slot("Selasa_13:00_GD512", hour=13, room_id=512)
    graph.add_slot("Rabu_08:00_GD722", hour=8, room_id=722)

    # Menambahkan Transisi & Biaya Penalti (Cost C)
    graph.add_transition("Start_Slot", "Senin_10:00_GD721", cost=5.0)
    graph.add_transition("Start_Slot", "Selasa_13:00_GD512", cost=2.0)
    graph.add_transition("Selasa_13:00_GD512", "Rabu_08:00_GD722", cost=1.0)
    graph.add_transition("Senin_10:00_GD721", "Rabu_08:00_GD722", cost=4.0)

    # Eksekusi Pencarian Slot Terbaik
    start_state = "Start_Slot"
    target_state = "Rabu_08:00_GD722"
    
    path, total_cost = a_star_search(graph, start_state, target_state)
    
    if path:
        print(f"Jalur Slot Terpilih : {' -> '.join(path)}")
        print(f"Total Biaya Penalti : {total_cost}")
    else:
        print("Tidak ditemukan slot jadwal yang sesuai (Conflict).")

if __name__ == "__main__":
    main()