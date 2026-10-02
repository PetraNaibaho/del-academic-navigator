"""
Unit tests untuk Sensitivity Analyzer & Benchmarking CSP Solver.
"""

from src.search.sensitivity import (
    CSPSensitivityAnalyzer,
    generate_benchmark_instance,
)


def test_generate_benchmark_instance():
    courses, slots = generate_benchmark_instance(num_courses=5, seed=42)
    assert len(courses) == 5
    assert len(slots) > 0
    assert all(c.course_id.startswith("COURSE_") for c in courses)


def test_sensitivity_analyzer_runs_successfully():
    analyzer = CSPSensitivityAnalyzer()
    c_small, s_small = generate_benchmark_instance(num_courses=3, num_slots_per_day=2, num_days=2, seed=123)
    results = analyzer.evaluate_configs_on_instance("Test Scale", c_small, s_small)

    assert len(results) == 4
    for metric in results:
        assert metric.scale_name == "Test Scale"
        assert metric.num_courses == 3
        assert isinstance(metric.is_satisfied, bool)
        assert metric.nodes_explored >= 0
        assert metric.backtracks >= 0
        assert metric.execution_time_ms >= 0.0

    table_md = analyzer.format_markdown_table(results)
    assert "Test Scale" in table_md
    assert "| Node Dieksplorasi |" in table_md


def test_full_sensitivity_benchmark_executes_without_error():
    analyzer = CSPSensitivityAnalyzer()
    metrics = analyzer.run_full_benchmark()
    assert len(metrics) >= 12
