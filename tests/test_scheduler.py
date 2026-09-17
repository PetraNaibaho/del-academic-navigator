import sys
from pathlib import Path

# Baris ini agar Python tidak bingung mencari folder src
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest
from del_academic_navigator.rules import calculate_room_cost
from search.graph import AcademicScheduleGraph
from search.scheduler import a_star_search


def test_a_star_pathfinding_success():
    graph = AcademicScheduleGraph()
    graph.add_slot("Start", 8, 1)
    graph.add_slot("Target", 10, 1)
    graph.add_transition("Start", "Target", 3.0)

    path, cost = a_star_search(graph, "Start", "Target")
    assert path == ["Start", "Target"]
    assert cost == 3.0


def test_a_star_no_path():
    graph = AcademicScheduleGraph()
    graph.add_slot("Start", 8, 1)
    graph.add_slot("Isolated", 10, 1)

    path, cost = a_star_search(graph, "Start", "Isolated")
    assert path is None
    assert cost == float("inf")


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