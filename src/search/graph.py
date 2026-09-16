class AcademicScheduleGraph:
    """
    Representasi Graf Ruang Keadaan (State Space) untuk Jadwal Perkuliahan & Bimbingan Akademik.
    State (X): Node yang mewakili slot waktu dan ruangan ("Hari_Jam_Ruangan").
    """
    def __init__(self):
        self.adj_list = {}
        self.node_metadata = {}

    def add_slot(self, node_id: str, hour: int, room_id: int):
        """Menambahkan node slot waktu baru ke dalam graf."""
        if node_id not in self.adj_list:
            self.adj_list[node_id] = []
            self.node_metadata[node_id] = {"hour": hour, "room_id": room_id}

    def add_transition(self, from_node: str, to_node: str, cost: float):
        """Menambahkan transisi antar-slot waktu beserta biaya penaltinya (Cost C)."""
        if from_node in self.adj_list and to_node in self.adj_list:
            self.adj_list[from_node].append((to_node, cost))

    def get_neighbors(self, node: str):
        """Mengembalikan daftar slot tetangga yang dapat dijangkau."""
        return self.adj_list.get(node, [])

    def heuristic(self, current_node: str, target_node: str) -> float:
        """
        Fungsi Heuristik h(n) Admissible:
        Menghitung selisih jam minimum menuju slot target ideal yang diharapkan.
        """
        curr_h = self.node_metadata[current_node]["hour"]
        target_h = self.node_metadata[target_node]["hour"]
        return abs(curr_h - target_h)