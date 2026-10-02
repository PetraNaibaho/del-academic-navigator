"""
Unit tests untuk CSP Solver (AC-3, Backtracking, MRV, LCV, FC)
Milestone 2 - Del-Academic Navigator.
"""

# Test suite compatible with standard python runner

from itertools import product
from contextlib import contextmanager

try:
    import pytest
except ImportError:
    pytest = None


@contextmanager
def assert_raises(exc_type, match=None):
    if pytest is not None:
        with pytest.raises(exc_type, match=match):
            yield
    else:
        try:
            yield
        except exc_type as e:
            if match and match not in str(e):
                raise AssertionError(f"Expected match '{match}' in '{str(e)}'") from e
            return
        except Exception as e:
            raise AssertionError(f"Expected {exc_type.__name__}, got {type(e).__name__}") from e
        raise AssertionError(f"Expected {exc_type.__name__} was not raised")

from src.search.solver import CSPSolver, BinaryConstraint
from src.del_academic_navigator.csp_schedule import (
    ScheduleCourse,
    ScheduleSlot,
    build_academic_schedule_csp,
)


def test_australia_map_coloring_ac3_and_backtracking():
    """
    Uji coba kasus benchmark Map Coloring Peta Australia.
    Variabel: WA, NT, SA, Q, NSW, V, T
    Domain: {Red, Green, Blue}
    Batasan: Wilayah bertetangga tidak boleh berwarna sama (WA != NT, WA != SA, dst.)
    """
    variables = ["WA", "NT", "SA", "Q", "NSW", "V", "T"]
    colors = ["Red", "Green", "Blue"]
    domains = {v: list(colors) for v in variables}

    solver = CSPSolver(variables, domains)

    # Tambahkan batasan ketetanggaan
    edges = [
        ("WA", "NT"), ("WA", "SA"),
        ("NT", "SA"), ("NT", "Q"),
        ("SA", "Q"), ("SA", "NSW"), ("SA", "V"),
        ("Q", "NSW"),
        ("NSW", "V"),
    ]

    for v1, v2 in edges:
        solver.add_constraint(
            BinaryConstraint(v1, v2, lambda x, y: x != y, f"NotEqual({v1},{v2})")
        )

    # Preprocessing AC-3
    is_consistent, ac3_domains, prunings = solver.ac3()
    assert is_consistent is True
    assert prunings >= 0

    # Solve CSP
    res = solver.solve(use_ac3_preprocess=True, use_mrv=True, use_lcv=True, use_fc=True)
    assert res.is_satisfied is True
    assert res.assignment is not None
    assert len(res.assignment) == 7

    # Verifikasi batasan
    for v1, v2 in edges:
        assert res.assignment[v1] != res.assignment[v2]


def test_it_del_room_scheduling_csp():
    """
    Uji coba kasus alokasi ruang perkuliahan IT Del dengan batasan bisnis:
    1. Dosen A (Samuel) dan Dosen B (Indra) tidak boleh memakai gedung/ruang yang sama di jam bersamaan.
    2. Mahasiswa paralel (>40 mhs) wajib menggunakan GD721/GD722.
    """
    variables = ["KULIAH_31SI1", "KULIAH_31SI2", "KULIAH_31S1_PARALEL"]
    
    # Domain: (Hari, SlotJam, Ruang, Kapasitas)
    domains = {
        "KULIAH_31SI1": [("Senin", "08:00", "GD512", 40), ("Senin", "10:00", "GD512", 40)],
        "KULIAH_31SI2": [("Senin", "08:00", "GD512", 40), ("Senin", "10:00", "GD911", 40)],
        "KULIAH_31S1_PARALEL": [("Senin", "08:00", "GD721", 60), ("Senin", "10:00", "GD722", 60)],
    }

    solver = CSPSolver(variables, domains)

    # Batasan 1: KULIAH_31SI1 dan KULIAH_31SI2 tidak boleh di ruang yang sama pada jam yang sama
    solver.add_constraint(
        BinaryConstraint(
            "KULIAH_31SI1",
            "KULIAH_31SI2",
            lambda v1, v2: not (v1[0] == v2[0] and v1[1] == v2[1] and v2[2] == v1[2]),
            "NoRoomTimeConflict",
        )
    )

    res = solver.solve()
    assert res.is_satisfied is True
    assert res.assignment["KULIAH_31SI1"] != res.assignment["KULIAH_31SI2"]


def test_unsolvable_csp_edge_case():
    """
    Kasus ekstrem: CSP tanpa solusi karena batasan yang tidak mungkin terpenuhi.
    Variabel A dan B dengan domain {1}, dan batasan A != B.
    """
    variables = ["A", "B"]
    domains = {"A": [1], "B": [1]}

    solver = CSPSolver(variables, domains)
    solver.add_constraint(BinaryConstraint("A", "B", lambda x, y: x != y, "Unequal"))

    # AC-3 harus mendeteksi kontradiksi
    is_consistent, _, _ = solver.ac3()
    assert is_consistent is False

    res = solver.solve()
    assert res.is_satisfied is False
    assert res.assignment is None


def test_ac3_cascades_pruning_without_mutating_input_domains():
    solver = CSPSolver(
        ["A", "B", "C"],
        {"A": [1, 2], "B": [1, 2], "C": [2]},
    )
    solver.add_constraint(BinaryConstraint("A", "B", lambda a, b: a != b))
    solver.add_constraint(BinaryConstraint("B", "C", lambda b, c: b == c))
    original_domains = {"A": [1, 2], "B": [1, 2], "C": [2]}

    is_consistent, reduced_domains, prunings = solver.ac3(original_domains)

    assert is_consistent is True
    assert reduced_domains == {"A": [1], "B": [2], "C": [2]}
    assert prunings == 2
    assert original_domains == {"A": [1, 2], "B": [1, 2], "C": [2]}


def test_ac3_detects_empty_domain_even_without_constraints():
    solver = CSPSolver(["A"], {"A": []})

    is_consistent, reduced_domains, prunings = solver.ac3()

    assert is_consistent is False
    assert reduced_domains == {"A": []}
    assert prunings == 0
    assert solver.solve().assignment is None


def test_reversed_pair_checks_constraint_in_declared_orientation():
    solver = CSPSolver(["A", "B"], {"A": [1, 2], "B": [1, 2]})
    solver.add_constraint(BinaryConstraint("A", "B", lambda a, b: a <= b))

    assert solver.is_consistent_pair("B", 2, "A", 1) is True
    assert solver.is_consistent_pair("B", 1, "A", 2) is False


def test_solver_matches_brute_force_for_all_three_variable_binary_csps():
    variables = ["A", "B", "C"]
    pairs = [("A", "B"), ("A", "C"), ("B", "C")]
    relations = (
        None,
        lambda left, right: left == right,
        lambda left, right: left != right,
    )

    for relation_choices in product(range(len(relations)), repeat=len(pairs)):
        solver = CSPSolver(
            variables,
            {variable: [0, 1] for variable in variables},
        )
        for pair, relation_index in zip(pairs, relation_choices):
            relation = relations[relation_index]
            if relation is not None:
                solver.add_constraint(BinaryConstraint(*pair, relation))

        brute_force_solutions = []
        for values in product((0, 1), repeat=len(variables)):
            assignment = dict(zip(variables, values))
            if all(
                solver.is_consistent_pair(
                    constraint.var1,
                    assignment[constraint.var1],
                    constraint.var2,
                    assignment[constraint.var2],
                )
                for constraint in solver.constraints
            ):
                brute_force_solutions.append(assignment)

        for options in (
            {},
            {"use_ac3_preprocess": False},
            {"use_fc": False},
        ):
            result = solver.solve(**options)
            assert result.is_satisfied is bool(brute_force_solutions)
            if result.assignment is not None:
                assert all(
                    solver.is_consistent_pair(
                        constraint.var1,
                        result.assignment[constraint.var1],
                        constraint.var2,
                        result.assignment[constraint.var2],
                    )
                    for constraint in solver.constraints
                )


def test_solver_rejects_invalid_variable_and_constraint_references():
    with assert_raises(ValueError, match="unique"):
        CSPSolver(["A", "A"], {"A": [1]})
    with assert_raises(ValueError, match="Domain keys"):
        CSPSolver(["A", "B"], {"A": [1]})
    with assert_raises(TypeError, match="callable"):
        BinaryConstraint("A", "B", None)

    solver = CSPSolver(["A"], {"A": [1]})
    with assert_raises(ValueError, match="unknown variables"):
        solver.add_constraint(BinaryConstraint("A", "B", lambda a, b: True))
    with assert_raises(ValueError, match="distinct variables"):
        solver.add_constraint(BinaryConstraint("A", "A", lambda a, b: True))


def test_business_scheduler_enforces_sop_and_returns_conflict_free_schedule():
    courses = [
        ScheduleCourse("AI", "Samuel", ("31SI1", "31SI2"), 58),
        ScheduleCourse("BD", "Indra", ("31SI1", "31SI2"), 58),
        ScheduleCourse("NET", "Samuel", ("31SI1",), 30, requires_lab=True),
    ]
    invalid_regular_room = ScheduleSlot("Senin", 10, 2, "GD935", 40)
    invalid_short_notice = ScheduleSlot(
        "Senin", 8, 2, "GD721", 80, day_offset=1
    )
    slots = [
        invalid_regular_room,
        invalid_short_notice,
        ScheduleSlot("Selasa", 8, 2, "GD721", 80),
        ScheduleSlot("Selasa", 8, 2, "GD722", 75),
        ScheduleSlot("Selasa", 10, 2, "GD911", 60, is_lab=True),
        ScheduleSlot("Selasa", 13, 2, "GD512", 40),
        ScheduleSlot("Rabu", 10, 2, "GD722", 75),
    ]
    solver = build_academic_schedule_csp(courses, slots)

    assert invalid_regular_room not in solver.domains["AI"]
    assert invalid_short_notice not in solver.domains["AI"]
    assert all(slot.is_lab for slot in solver.domains["NET"])
    assert all(slot.room_capacity >= 58 for slot in solver.domains["AI"])
    assert all(slot.room_id in {"GD721", "GD722"} for slot in solver.domains["AI"])

    result = solver.solve()

    assert result.is_satisfied is True
    assert result.assignment is not None
    for index, course in enumerate(courses):
        slot = result.assignment[course.course_id]
        assert slot.day_offset >= 2
        assert slot.start_hour >= 8
        assert slot.end_hour <= 17
        assert not (slot.start_hour < 13 and slot.end_hour > 12)
        assert slot.room_capacity >= course.student_count
        if course.student_count > 40:
            assert slot.room_id in {"GD721", "GD722"}
        if course.requires_lab:
            assert slot.is_lab
        for other_course in courses[index + 1 :]:
            assert solver.is_consistent_pair(
                course.course_id,
                slot,
                other_course.course_id,
                result.assignment[other_course.course_id],
            )


def test_business_scheduler_reports_unsatisfiable_room_and_resource_conflicts():
    shared_slot = ScheduleSlot("Selasa", 8, 2, "GD721", 80)
    room_conflict = build_academic_schedule_csp(
        [
            ScheduleCourse("A", "Dosen A", ("31SI1",), 30),
            ScheduleCourse("B", "Dosen B", ("31SI2",), 30),
        ],
        [shared_slot],
    )
    assert room_conflict.solve().is_satisfied is False

    lecturer_conflict = build_academic_schedule_csp(
        [
            ScheduleCourse("A", "Dosen A", ("31SI1",), 30),
            ScheduleCourse("B", "Dosen A", ("31SI2",), 30),
        ],
        [
            shared_slot,
            ScheduleSlot("Selasa", 10, 2, "GD722", 75),
        ],
    )
    result = lecturer_conflict.solve()
    assert result.is_satisfied is True
    assert result.assignment is not None
    assert result.assignment["A"] != result.assignment["B"]


def test_business_scheduler_rejects_room_capacity_not_in_master_data():
    with assert_raises(ValueError, match="room master"):
        build_academic_schedule_csp(
            [ScheduleCourse("A", "Dosen A", ("31SI1",), 30)],
            [ScheduleSlot("Selasa", 8, 2, "GD721", 100)],
        )


if __name__ == "__main__":
    print("Running CSP Solver tests...")
    test_australia_map_coloring_ac3_and_backtracking()
    print("[PASS] Australia Map Coloring (AC-3 + Backtracking MRV/LCV/FC)")
    test_it_del_room_scheduling_csp()
    print("[PASS] IT Del Room Scheduling CSP")
    test_unsolvable_csp_edge_case()
    print("[PASS] Unsolvable CSP Edge Case")
    test_ac3_cascades_pruning_without_mutating_input_domains()
    test_ac3_detects_empty_domain_even_without_constraints()
    test_reversed_pair_checks_constraint_in_declared_orientation()
    test_solver_matches_brute_force_for_all_three_variable_binary_csps()
    test_solver_rejects_invalid_variable_and_constraint_references()
    test_business_scheduler_enforces_sop_and_returns_conflict_free_schedule()
    test_business_scheduler_reports_unsatisfiable_room_and_resource_conflicts()
    test_business_scheduler_rejects_room_capacity_not_in_master_data()
    print("[PASS] AC-3 Propagation, Exhaustive CSP Oracle, and SOP Scheduling")
    print("\nALL CSP SOLVER TESTS PASSED SUCCESSFULLY!")
