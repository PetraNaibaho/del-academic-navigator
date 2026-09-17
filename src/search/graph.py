class AcademicScheduleGraph:
    """
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
        if from_node in self.adj_list and to_node in self.adj_list:
            self.adj_list[from_node].append((to_node, cost))

    def get_neighbors(self, node: str):
        """Mengembalikan daftar tetangga yang terhubung."""
        return self.adj_list.get(node, [])

    def heuristic(self, current_node: str, target_node: str) -> float:
        """
        Fungsi Heuristik h(n) Admissible:
        Menghitung selisih waktu minimum menuju slot target.
        """
        if current_node not in self.node_metadata or target_node not in self.node_metadata:
            return 0.0
            
        curr = self.node_metadata[current_node]
        target = self.node_metadata[target_node]
        
        return float(abs(curr["hour"] - target["hour"]) + abs(curr["day"] - target["day"]))