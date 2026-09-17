<<<<<<< HEAD
"""
Unit Test Suite untuk Del-Academic Navigator.

Menguji:
1. Kebenaran penelusuran optimal A* Search & Uniform Cost Search (UCS).
2. Penanganan edge-cases (graf terputus, siklus, tie-breaking).
3. Validasi matematis Admissibility dan Consistency fungsi heuristik h(n).
4. Resolusi bentrok multi-matakuliah (Course Conflict Resolution, Goal: conflict_count == 0).
"""

import pytest
from src.search.graph import (
    AcademicScheduleGraph,
    build_it_del_sample_graph,
)
from src.search.scheduler import SearchResult, a_star_search, uniform_cost_search
from src.search.conflict_resolver import (
    Course,
    Slot,
    ScheduleState,
    ScheduleConflictResolver,
)
=======
import sys
from pathlib import Path

# Baris ini agar Python tidak bingung mencari folder src
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest
from del_academic_navigator.rules import calculate_room_cost
from search.graph import AcademicScheduleGraph
from search.scheduler import a_star_search
>>>>>>> 77afe139507d40ad1ee212a629005427ee7d2fb1


def test_a_star_pathfinding_success():
    """Menguji penelusuran dasar A* pada graf sederhana."""
    graph = AcademicScheduleGraph()
    graph.add_slot("Start", hour=8, room_id=1)
    graph.add_slot("Target", hour=10, room_id=1)
    graph.add_transition("Start", "Target", 3.0)

    path, cost = a_star_search(graph, "Start", "Target")
    assert path == ["Start", "Target"]
    assert cost == 3.0


def test_a_star_no_path():
    """Menguji kondisi graf terputus (goal unreachable) tidak menyebabkan crash."""
    graph = AcademicScheduleGraph()
<<<<<<< HEAD
    graph.add_slot("Start", hour=8, room_id=1)
    graph.add_slot("Isolated", hour=10, room_id=1)
=======
    graph.add_slot("Start", 8, 1)
    graph.add_slot("Isolated", 10, 1)
>>>>>>> 77afe139507d40ad1ee212a629005427ee7d2fb1

    path, cost = a_star_search(graph, "Start", "Isolated")
    assert path is None
    assert cost == float("inf")


<<<<<<< HEAD
def test_ucs_pathfinding_success():
    """Menguji Uniform Cost Search berhasil menemukan jalur berbiaya termurah."""
    graph = AcademicScheduleGraph()
    graph.add_slot("A", hour=8, room_id=1)
    graph.add_slot("B", hour=9, room_id=1)
    graph.add_slot("C", hour=10, room_id=1)

    graph.add_transition("A", "B", cost=2.0)
    graph.add_transition("B", "C", cost=1.0)
    graph.add_transition("A", "C", cost=5.0)

    result = uniform_cost_search(graph, "A", "C")
    assert result.path == ["A", "B", "C"]
    assert result.total_cost == 3.0


def test_ucs_vs_a_star_optimality():
    """Menguji bahwa A* dan UCS menghasilkan total biaya optimal yang identik."""
    graph = build_it_del_sample_graph()
    start_node = "Start_Slot"
    goal_node = "Jumat_08:00_GD722"

    ucs_result = uniform_cost_search(graph, start_node, goal_node)
    astar_result = a_star_search(graph, start_node, goal_node)

    assert ucs_result.path is not None
    assert astar_result.path is not None
    assert ucs_result.total_cost == astar_result.total_cost
    assert astar_result.total_cost == pytest.approx(20.0)


def test_a_star_exploration_efficiency():
    """Menguji bahwa A* Search mengeksplorasi <= simpul dibanding UCS."""
    graph = build_it_del_sample_graph()
    start_node = "Start_Slot"
    goal_node = "Jumat_08:00_GD722"

    ucs_result = uniform_cost_search(graph, start_node, goal_node)
    astar_result = a_star_search(graph, start_node, goal_node)

    assert astar_result.nodes_explored <= ucs_result.nodes_explored


def test_heuristic_admissibility():
    """Validasi Matematis Admissibility: h(n) <= h*(n)."""
    graph = build_it_del_sample_graph()
    goal_node = "Jumat_08:00_GD722"

    for node in graph.slots.keys():
        h_val = graph.heuristic(node, goal_node)
        ucs_true_cost = uniform_cost_search(graph, node, goal_node).total_cost
        if ucs_true_cost != float("inf"):
            assert h_val <= ucs_true_cost


def test_heuristic_consistency():
    """Validasi Matematis Consistency (Monotonisitas): h(n) <= c(n, a, n') + h(n')."""
    graph = build_it_del_sample_graph()
    goal_node = "Jumat_08:00_GD722"

    for (u, v), edge in graph.edges_detail.items():
        h_u = graph.heuristic(u, goal_node)
        h_v = graph.heuristic(v, goal_node)
        assert h_u <= (edge.cost + h_v) + 1e-6


def test_cyclic_graph_termination():
    """Menguji algoritma tidak terjebak dalam loop pada graf bersiklus."""
    graph = AcademicScheduleGraph()
    graph.add_slot("N1", hour=8, room_id=1)
    graph.add_slot("N2", hour=9, room_id=1)
    graph.add_slot("N3", hour=10, room_id=1)

    graph.add_transition("N1", "N2", 1.0)
    graph.add_transition("N2", "N1", 1.0)
    graph.add_transition("N2", "N3", 2.0)

    res = a_star_search(graph, "N1", "N3")
    assert res.path == ["N1", "N2", "N3"]
    assert res.total_cost == 3.0


def test_schedule_conflict_resolution_goal_zero_conflicts():
    """
    Menguji pemodelan State Space di mana mahasiswa mengambil beberapa matakuliah
    yang mengalami bentrok slot waktu, dan algoritma memindahkan jadwal hingga conflict_count == 0.
    """
    courses = {
        "10S3001": Course("10S3001", "Kecerdasan Buatan", "Samuel Situmeang", "31SI1", 40, "Senin", 10),
        "10S3002": Course("10S3002", "Basis Data Lanjut", "Dosen B", "31SI1", 40, "Senin", 10),
    }

    slot_clash = Slot("Senin", 10, "GD512", 40)
    slot_alt_1 = Slot("Senin", 13, "GD512", 40)
    slot_alt_2 = Slot("Selasa", 10, "GD721", 80)

    # Initial state: Kedua matakuliah bentrok di hari Senin 10:00 (cohort 31SI1 dan room GD512)
    initial_state = ScheduleState(assignments={
        "10S3001": slot_clash,
        "10S3002": slot_clash,
    })

    resolver = ScheduleConflictResolver(courses, [slot_clash, slot_alt_1, slot_alt_2])
    assert resolver.count_conflicts(initial_state) > 0

    # Jalankan pencarian solusi hingga goal: conflict_count == 0
    final_state, cost, nodes, history = resolver.solve(initial_state, algorithm="A*")

    assert final_state is not None
    assert resolver.goal_test(final_state) is True
    assert resolver.count_conflicts(final_state) == 0
    assert cost > 0.0
    assert len(history) > 0
=======
def test_a_star_sop_room_selection():
    graph = AcademicScheduleGraph()
    graph.add_slot("Start", 8, 1)
    graph.add_slot("GD512", 10, 3, "GD512")
    graph.add_slot("GD721", 10, 3, "GD721")
    graph.add_slot("Goal", 12, 3)

    cost_small = calculate_room_cost("GD512", 30)
    cost_large = calculate_room_cost("GD721", 30)

    graph.add_transition("Start", "GD512", cost_small)
    graph.add_transition("GD512", "Goal", 1.0)

    graph.add_transition("Start", "GD721", cost_large)
    graph.add_transition("GD721", "Goal", 1.0)

    path, cost = a_star_search(graph, "Start", "Goal")

    assert path == ["Start", "GD512", "Goal"]
    assert cost == 2.0
>>>>>>> 77afe139507d40ad1ee212a629005427ee7d2fb1
