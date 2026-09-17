"""
Modul Algoritma Penelusuran Ruang Keadaan (State Space Search Engine).

Mengimplementasikan:
1. Uniform Cost Search (UCS) berbasis antrean prioritas (heapq)
2. A* Search berbasis heuristik konsisten dan admissible
untuk menemukan jalur penjadwalan kuliah/bimbingan berbiaya penalti minimum.
"""

import heapq
import time
from dataclasses import dataclass
from typing import Iterator, List, Optional, Tuple, Any


@dataclass
class SearchResult:
    """
    Struktur data hasil pencarian algoritma penelusuran.
    
    Mendukung unpacking tuple: `path, cost = search_result` untuk kompatibilitas penuh.
    """
    path: Optional[List[str]]
    total_cost: float
    nodes_explored: int = 0
    execution_time_ms: float = 0.0
    algorithm: str = "A* Search"

    def __iter__(self) -> Iterator[Any]:
        """Memungkinkan unpacking langsung: path, cost = result."""
        yield self.path
        yield self.total_cost

    def __getitem__(self, index: int) -> Any:
        if index == 0:
            return self.path
        elif index == 1:
            return self.total_cost
        raise IndexError("SearchResult index out of range (0=path, 1=cost)")


def uniform_cost_search(
    graph: Any,
    start_node: str,
    goal_node: str,
) -> SearchResult:
    """
    Algoritma Uniform Cost Search (UCS) untuk graf masalah bisnis berbobot.
    
    Karakteristik:
    - Menelusuri simpul berdasarkan g(n) terkecil (akumulasi path cost terendah).
    - Dijamin menemukan solusi optimal jika seluruh bobot sisi c(n, a, n') > 0.
    - Menggunakan tie-breaking counter agar antrean prioritas selalu stabil.
    """
    start_time = time.perf_counter()
    nodes_explored = 0
    counter = 0  # Tie-breaker untuk stabilitas heapq

    # Priority queue menyimpan: (g_score, counter, current_node, path)
    priority_queue: List[Tuple[float, int, str, List[str]]] = []
    heapq.heappush(priority_queue, (0.0, counter, start_node, [start_node]))

    visited = {}

    while priority_queue:
        g_score, _, current, path = heapq.heappop(priority_queue)
        nodes_explored += 1

        if current == goal_node:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return SearchResult(
                path=path,
                total_cost=g_score,
                nodes_explored=nodes_explored,
                execution_time_ms=elapsed_ms,
                algorithm="Uniform Cost Search (UCS)",
            )

        if current in visited and visited[current] <= g_score:
            continue

        visited[current] = g_score

        for neighbor, weight in graph.get_neighbors(current):
            tentative_g = g_score + weight

            if neighbor not in visited or tentative_g < visited[neighbor]:
                counter += 1
                heapq.heappush(
                    priority_queue,
                    (tentative_g, counter, neighbor, path + [neighbor]),
                )

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0
    return SearchResult(
        path=None,
        total_cost=float("inf"),
        nodes_explored=nodes_explored,
        execution_time_ms=elapsed_ms,
        algorithm="Uniform Cost Search (UCS)",
    )


def a_star_search(
    graph: Any,
    start_node: str,
    goal_node: str,
) -> SearchResult:
    """
    Algoritma A* Search dengan heuristik h(n) admissible untuk penentuan slot optimal.
    
    Formula Evaluasi:
        f(n) = g(n) + h(n)
        - g(n): Biaya penalti akumulatif riil dari start node ke simpul n.
        - h(n): Estimasi biaya minimum dari simpul n menuju goal node (admissible: h(n) <= h*(n)).
    
    Keunggulan:
    - Mengarahkan pencarian secara terarah menuju slot target.
    - Jumlah node yang dieksplorasi secara signifikan lebih sedikit dibanding UCS murni.
    """
    start_time = time.perf_counter()
    nodes_explored = 0
    counter = 0  # Tie-breaker untuk stabilitas heapq

    initial_h = graph.heuristic(start_node, goal_node)
    # Priority queue menyimpan: (f_score, counter, g_score, current_node, path)
    priority_queue: List[Tuple[float, int, float, str, List[str]]] = []
    heapq.heappush(priority_queue, (initial_h, counter, 0.0, start_node, [start_node]))

    visited = {}

    while priority_queue:
        f_score, _, g_score, current, path = heapq.heappop(priority_queue)
        nodes_explored += 1

        if current == goal_node:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return SearchResult(
                path=path,
                total_cost=g_score,
                nodes_explored=nodes_explored,
                execution_time_ms=elapsed_ms,
                algorithm="A* Search",
            )

        if current in visited and visited[current] <= g_score:
            continue

        visited[current] = g_score

        for neighbor, weight in graph.get_neighbors(current):
            tentative_g = g_score + weight
            h_score = graph.heuristic(neighbor, goal_node)
            f_neighbor = tentative_g + h_score

            if neighbor not in visited or tentative_g < visited[neighbor]:
                counter += 1
                heapq.heappush(
                    priority_queue,
                    (f_neighbor, counter, tentative_g, neighbor, path + [neighbor]),
                )

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0
    return SearchResult(
        path=None,
        total_cost=float("inf"),
        nodes_explored=nodes_explored,
        execution_time_ms=elapsed_ms,
        algorithm="A* Search",
    )