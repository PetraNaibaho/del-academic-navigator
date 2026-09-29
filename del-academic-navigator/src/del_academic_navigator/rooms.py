"""
Data Master Ruangan Kampus Institut Teknologi Del.
Memuat 46 ruangan lengkap dari dokumen resmi kampus (Gedung GD5, GD7, GD8, GD9, Lab, dan AUD).
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class RoomInfo:
    room_id: str
    room_type: str        # 'KELAS', 'LAB', 'LAB ING', 'SCL', 'ROBOTIKA', 'AUD'
    capacity: int         # Daya tampung / kapasitas kursi
    faculty_filter: str   # 'FITE', 'FTI', 'FV', 'FB', atau '' (Umum)
    building: str         # Gedung lokasi ruangan


# Master Dataset 46 Ruangan Kampus IT Del
IT_DEL_ROOMS: List[RoomInfo] = [
    # Halaman 1 (29 Ruangan)
    RoomInfo("AUD", "AUD", 150, "", "Auditorium"),
    RoomInfo("GD516", "KELAS", 35, "FV", "Gedung 5"),
    RoomInfo("GD714", "LAB", 30, "", "Gedung 7"),
    RoomInfo("GD721", "KELAS", 80, "FITE", "Gedung 7"),
    RoomInfo("GD722", "KELAS", 75, "FITE", "Gedung 7"),
    RoomInfo("GD723", "LAB", 30, "", "Gedung 7"),
    RoomInfo("GD912", "LAB", 60, "", "Gedung 9"),
    RoomInfo("GD914", "LAB ING", 35, "", "Gedung 9"),
    RoomInfo("GD923", "KELAS", 40, "FTI", "Gedung 9"),
    RoomInfo("GD924", "KELAS", 40, "FTI", "Gedung 9"),
    RoomInfo("GD925", "KELAS", 40, "FTI", "Gedung 9"),
    RoomInfo("GD927", "KELAS", 40, "", "Gedung 9"),
    RoomInfo("GD928", "KELAS", 40, "", "Gedung 9"),
    RoomInfo("GD929", "KELAS", 40, "", "Gedung 9"),
    RoomInfo("GD933", "KELAS", 40, "FB", "Gedung 9"),
    RoomInfo("GD934", "KELAS", 40, "FB", "Gedung 9"),
    RoomInfo("GD935", "KELAS", 40, "FITE", "Gedung 9"),
    RoomInfo("GD937", "KELAS", 35, "FV", "Gedung 9"),
    RoomInfo("GD938", "KELAS", 35, "FV", "Gedung 9"),
    RoomInfo("GD939", "KELAS", 40, "", "Gedung 9"),
    RoomInfo("GD942", "KELAS", 40, "", "Gedung 9"),
    RoomInfo("GD943", "SCL", 40, "", "Gedung 9"),
    RoomInfo("GD944", "ROBOTIKA", 30, "", "Gedung 9"),
    RoomInfo("GD513", "LAB", 30, "", "Gedung 5"),
    RoomInfo("GD514", "LAB", 30, "", "Gedung 5"),
    RoomInfo("GD515", "LAB", 30, "", "Gedung 5"),
    RoomInfo("GD525", "LAB", 30, "", "Gedung 5"),
    RoomInfo("GD526", "LAB", 30, "", "Gedung 5"),
    RoomInfo("GD711", "LAB", 30, "", "Gedung 7"),

    # Halaman 2 (17 Ruangan)
    RoomInfo("GD712", "LAB", 30, "", "Gedung 7"),
    RoomInfo("GD713", "LAB", 30, "", "Gedung 7"),
    RoomInfo("GD724", "LAB", 30, "", "Gedung 7"),
    RoomInfo("GD725", "LAB", 30, "", "Gedung 7"),
    RoomInfo("GD726", "LAB", 30, "", "Gedung 7"),
    RoomInfo("LDTE", "LAB", 30, "", "Gedung LDTE"),
    RoomInfo("LSK", "LAB", 30, "", "Gedung LSK"),
    RoomInfo("LSD", "LAB", 30, "", "Gedung LSD"),
    RoomInfo("GD916", "LAB", 30, "", "Gedung 9"),
    RoomInfo("GD811", "LAB", 30, "", "Gedung 8"),
    RoomInfo("GD812", "LAB", 30, "", "Gedung 8"),
    RoomInfo("GD813", "LAB", 30, "", "Gedung 8"),
    RoomInfo("GD814", "LAB", 30, "", "Gedung 8"),
    RoomInfo("GD815", "LAB", 30, "", "Gedung 8"),
    RoomInfo("GD822", "LAB", 30, "", "Gedung 8"),
    RoomInfo("GD825", "LAB", 30, "", "Gedung 8"),
    RoomInfo("GD826", "LAB", 30, "", "Gedung 8"),
]

# Dictionary index by room_id
ROOMS_BY_ID: Dict[str, RoomInfo] = {room.room_id: room for room in IT_DEL_ROOMS}


def get_room_info(room_id: str) -> Optional[RoomInfo]:
    """Mengembalikan objek RoomInfo berdasarkan kode ruangan."""
    return ROOMS_BY_ID.get(room_id)


def filter_valid_rooms_for_capacity(min_capacity: int = 58) -> List[RoomInfo]:
    """Mengembalikan daftar ruangan yang mampu menampung minimal min_capacity mahasiswa (58 mhs)."""
    return [room for room in IT_DEL_ROOMS if room.capacity >= min_capacity]
