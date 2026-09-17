"""
Modul Graf Ruang Keadaan (State Space Graph) untuk Del-Academic Navigator.

Mendefinisikan pemodelan formal ruang keadaan jadwal perkuliahan dan bimbingan akademik
di Institut Teknologi Del berdasarkan formulasi (X, A, T, G, C) dan fungsi heuristik admissible.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class AcademicSlot:
    """
    Representasi State (X) dalam ruang keadaan jadwal akademik.
    
    Attributes:
        slot_id: Identifier unik slot, misal 'SENIN_10:00_GD721'.
        day: Nama hari perkuliahan ('Senin', 'Selasa', dst).
        day_index: Indeks hari (Senin=1, Selasa=2, ..., Jumat=5).
        hour: Jam mulai perkuliahan (format 24 jam, misal 8, 10, 13).
        duration_hours: Durasi sesi perkuliahan/bimbingan (dalam jam).
        room_id: Kode ruangan (misal 'GD721', 'GD512', 'GD722', 'GD911').
        building: Nama gedung (misal 'Gedung 7', 'Gedung 5', 'Gedung 9').
        capacity: Daya tampung kapasitas mahasiswa di ruangan tersebut.
        is_lab: Penanda apakah ruangan merupakan laboratorium komputer.
    """
    slot_id: str
    day: str = "Senin"
    day_index: int = 1
    hour: int = 8
    duration_hours: int = 2
    room_id: str = "GD721"
    building: str = "Gedung 7"
    capacity: int = 50
    is_lab: bool = False


@dataclass
class TransitionEdge:
    """
    Representasi Aksi (A) dan Transisi (T) antar-slot dengan bobot biaya (Cost C).
    """
    to_node: str
    cost: float
    description: str = ""


class AcademicScheduleGraph:
    """
<<<<<<< HEAD
    Representasi Graf Berarah dan Berbobot untuk Penjadwalan Akademik IT Del.
    
    Elemen Formulasi Formal:
    - X (State Space): Himpunan node slot waktu dan fasilitas ruangan kampus.
    - A (Action Space): Pemilihan alokasi slot alternatif yang feasible.
    - T (Transition Model): Transisi dari status slot n ke n'.
    - G (Goal State): Target slot waktu yang memenuhi persyaratan SOP (ruang cukup, nir-konflik).
    - C (Step Cost): Penalti komposit berbasis keterlambatan hari, pergeseran jam, dan perubahan ruangan.
    """

    def __init__(self):
        self.adj_list: Dict[str, List[Tuple[str, float]]] = {}
        self.edges_detail: Dict[Tuple[str, str], TransitionEdge] = {}
        self.slots: Dict[str, AcademicSlot] = {}
        # Backward-compatibility metadata dictionary
        self.node_metadata: Dict[str, dict] = {}

    def add_slot(
        self,
        node_id: str,
        hour: int = 8,
        room_id: int | str = 0,
        day: str = "Senin",
        day_index: int = 1,
        capacity: int = 40,
        building: str = "Kampus IT Del",
        is_lab: bool = False,
    ) -> None:
        """
        Menambahkan node slot waktu baru ke dalam graf.
        Mendukung pemanggilan lama (hour, room_id) maupun atribut lengkap.
        """
        if node_id not in self.adj_list:
            self.adj_list[node_id] = []
            
        slot_obj = AcademicSlot(
            slot_id=node_id,
            day=day,
            day_index=day_index,
            hour=hour,
            room_id=str(room_id),
            building=building,
            capacity=capacity,
            is_lab=is_lab,
        )
        self.slots[node_id] = slot_obj
        
        # Metadata dictionary untuk kompatibilitas fungsi bawaan
        self.node_metadata[node_id] = {
            "hour": hour,
            "room_id": room_id,
            "day": day,
            "day_index": day_index,
            "capacity": capacity,
            "building": building,
        }

    def add_transition(
        self,
        from_node: str,
        to_node: str,
        cost: float,
        description: str = "",
    ) -> None:
        """
        Menambahkan edge transisi berarah antar-slot waktu beserta biaya penaltinya (Cost C).
        """
=======
    Representasi Graf Ruang Keadaan (State Space) Penjadwalan IT Del.
    """

    def __init__(self):
        self.adj_list = {}
        self.node_metadata = {}

    def add_slot(self, node_id: str, hour: int, day: int = 1, room_name: str = "REGULER"):
        """Menambahkan node slot waktu baru ke graf."""
        if node_id not in self.adj_list:
            self.adj_list[node_id] = []
            self.node_metadata[node_id] = {
                "hour": hour,
                "day": day,
                "room_name": room_name
            }

    def add_transition(self, from_node: str, to_node: str, cost: float):
        """Menambahkan transisi antar-slot beserta bobot penalti (Cost C)."""
>>>>>>> 77afe139507d40ad1ee212a629005427ee7d2fb1
        if from_node in self.adj_list and to_node in self.adj_list:
            self.adj_list[from_node].append((to_node, float(cost)))
            self.edges_detail[(from_node, to_node)] = TransitionEdge(
                to_node=to_node,
                cost=float(cost),
                description=description,
            )

<<<<<<< HEAD
    def get_neighbors(self, node: str) -> List[Tuple[str, float]]:
        """Mengembalikan daftar slot tetangga yang dapat dijangkau beserta bobotnya."""
=======
    def get_neighbors(self, node: str):
        """Mengembalikan daftar tetangga yang terhubung."""
>>>>>>> 77afe139507d40ad1ee212a629005427ee7d2fb1
        return self.adj_list.get(node, [])

    def calculate_real_cost(
        self,
        source_node: str,
        target_node: str,
        weight_day: float = 5.0,
        weight_hour: float = 1.0,
        weight_room: float = 2.0,
    ) -> float:
        """
        Menghitung biaya penalti riil transisi antar dua slot berdasarkan SOP IT Del:
        Cost = (Selisih Hari * weight_day) + (|Selisih Jam| * weight_hour) + (Penalti Ruang Baru * weight_room)
        """
        src = self.slots.get(source_node)
        tgt = self.slots.get(target_node)
        if not src or not tgt:
            return 1.0

        day_diff = abs(tgt.day_index - src.day_index)
        hour_diff = abs(tgt.hour - src.hour)
        room_penalty = weight_room if src.room_id != tgt.room_id else 0.0

        return float((day_diff * weight_day) + (hour_diff * weight_hour) + room_penalty)

    def heuristic(self, current_node: str, target_node: str) -> float:
        """
<<<<<<< HEAD
        Fungsi Heuristik h(n) Admissible & Consistent (Monotonic):
        
        Formula:
            h(n) = |hour(current_node) - hour(target_node)| * 1.0
            
        Bukti Matematis Admissibility:
            Karena setiap langkah transisi perpindahan slot n -> n' memiliki biaya
            c(n, a, n') >= |hour(n') - hour(n)| * 1.0 (bobot pergeseran jam terkecil),
            maka h(n) <= h*(n), di mana h*(n) adalah biaya riil minimum menuju goal.
            Heuristik tidak pernah melebih-lebihkan (never overestimates) estimasi biaya,
            sehingga algoritma A* dijamin menghasilkan solusi Optimal.

        Bukti Matematis Consistency (Monotonisitas):
            h(n) <= c(n, a, n') + h(n')
            |hour(n) - hour(G)| <= |hour(n) - hour(n')| + |hour(n') - hour(G)| (Ketaksamaan Segitiga)
            Karena c(n, a, n') >= |hour(n) - hour(n')|, syarat konsistensi selalu terpenuhi.
        """
        if current_node not in self.node_metadata or target_node not in self.node_metadata:
            return 0.0

        curr_h = self.node_metadata[current_node]["hour"]
        target_h = self.node_metadata[target_node]["hour"]
        
        # Selisih jam minimum sebagai lower bound riil penalti waktu
        return float(abs(curr_h - target_h))


def build_it_del_sample_graph() -> AcademicScheduleGraph:
    """
    Membangun graf simulasi jadwal perkuliahan riil di Institut Teknologi Del.
    
    Kasus Bisnis:
    Mata kuliah '10S3001 - Kecerdasan Buatan (+P)' kelas gabungan (65 mahasiswa)
    semula terjadwal pada Selasa 10:00 di GD512 (Kapasitas 40, terjadi overload/bentrok).
    Sistem mengevaluasi opsi pemindahan kuliah pengganti (make-up class) ke slot nir-bentrok
    sesuai SOP H-2 dan kapasitas ruangan besar (GD721/GD722 kapasitas 70-80).
    """
    g = AcademicScheduleGraph()

    # Slot Awal & Slot Alternatif
    g.add_slot("Start_Slot", hour=10, room_id="GD512", day="Selasa", day_index=2, capacity=40, building="Gedung 5")
    
    # Hari Rabu (H+1) - Melanggar aturan ideal H-2 SOP, penalti tinggi
    g.add_slot("Rabu_08:00_GD512", hour=8, room_id="GD512", day="Rabu", day_index=3, capacity=40, building="Gedung 5")
    g.add_slot("Rabu_10:00_GD721", hour=10, room_id="GD721", day="Rabu", day_index=3, capacity=80, building="Gedung 7")
    
    # Hari Kamis (H+2) - Sesuai SOP minimal H-2
    g.add_slot("Kamis_10:00_GD721", hour=10, room_id="GD721", day="Kamis", day_index=4, capacity=80, building="Gedung 7")
    g.add_slot("Kamis_13:00_GD722", hour=13, room_id="GD722", day="Kamis", day_index=4, capacity=75, building="Gedung 7")
    
    # Hari Jumat (H+3) - Goal Slot Ideal yang telah disetujui BAAK
    g.add_slot("Jumat_08:00_GD722", hour=8, room_id="GD722", day="Jumat", day_index=5, capacity=75, building="Gedung 7")

    # Transisi dan Bobot Biaya Penalti Riil (Cost C) berbasis calculate_real_cost
    # Start -> Opsi Hari Rabu
    cost_start_rabu1 = g.calculate_real_cost("Start_Slot", "Rabu_08:00_GD512") + 1.0  # +1.0 Penalti H+1 mepet SOP
    g.add_transition("Start_Slot", "Rabu_08:00_GD512", cost=cost_start_rabu1, description="H+1 (Terlalu mepet SOP) & Kapasitas sempit")
    
    cost_start_rabu2 = g.calculate_real_cost("Start_Slot", "Rabu_10:00_GD721")
    g.add_transition("Start_Slot", "Rabu_10:00_GD721", cost=cost_start_rabu2, description="H+1 tapi ruangan GD721 memadai")
    
    # Start -> Opsi Hari Kamis (Sesuai SOP H-2)
    cost_start_kamis1 = g.calculate_real_cost("Start_Slot", "Kamis_10:00_GD721")
    g.add_transition("Start_Slot", "Kamis_10:00_GD721", cost=cost_start_kamis1, description="H+2 Sesuai SOP H-2, jam sama (10:00), GD721 luas")
    
    cost_start_kamis2 = g.calculate_real_cost("Start_Slot", "Kamis_13:00_GD722")
    g.add_transition("Start_Slot", "Kamis_13:00_GD722", cost=cost_start_kamis2, description="H+2 Sesuai SOP H-2, jam siang, GD722 luas")
    
    # Transisi ke Goal State Jumat_08:00_GD722
    cost_rabu1_jumat = g.calculate_real_cost("Rabu_08:00_GD512", "Jumat_08:00_GD722")
    g.add_transition("Rabu_08:00_GD512", "Jumat_08:00_GD722", cost=cost_rabu1_jumat, description="Pindah hari Rabu ke Jumat")
    
    cost_rabu2_jumat = g.calculate_real_cost("Rabu_10:00_GD721", "Jumat_08:00_GD722")
    g.add_transition("Rabu_10:00_GD721", "Jumat_08:00_GD722", cost=cost_rabu2_jumat, description="Pindah hari Rabu ke Jumat")
    
    cost_kamis1_jumat = g.calculate_real_cost("Kamis_10:00_GD721", "Jumat_08:00_GD722")
    g.add_transition("Kamis_10:00_GD721", "Jumat_08:00_GD722", cost=cost_kamis1_jumat, description="Pindah hari Kamis ke Jumat (Jalur Optimal)")
    
    cost_kamis2_jumat = g.calculate_real_cost("Kamis_13:00_GD722", "Jumat_08:00_GD722")
    g.add_transition("Kamis_13:00_GD722", "Jumat_08:00_GD722", cost=cost_kamis2_jumat, description="Pindah hari Kamis siang ke Jumat")

    return g
=======
        Fungsi Heuristik h(n) Admissible:
        Menghitung selisih waktu minimum menuju slot target.
        """
        if current_node not in self.node_metadata or target_node not in self.node_metadata:
            return 0.0
            
        curr = self.node_metadata[current_node]
        target = self.node_metadata[target_node]
        
        return float(abs(curr["hour"] - target["hour"]) + abs(curr["day"] - target["day"]))
>>>>>>> 77afe139507d40ad1ee212a629005427ee7d2fb1
