import pytest
from src.search.graph import AcademicScheduleGraph
from src.search.scheduler import a_star_search

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