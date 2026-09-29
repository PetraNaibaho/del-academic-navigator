"""
Unit tests untuk CSP Solver (AC-3, Backtracking, MRV, LCV, FC)
Milestone 2 - Del-Academic Navigator.
"""

# Test suite compatible with standard python runner

from src.search.solver import CSPSolver, BinaryConstraint


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


if __name__ == "__main__":
    print("Running CSP Solver tests...")
    test_australia_map_coloring_ac3_and_backtracking()
    print("[PASS] Australia Map Coloring (AC-3 + Backtracking MRV/LCV/FC)")
    test_it_del_room_scheduling_csp()
    print("[PASS] IT Del Room Scheduling CSP")
    test_unsolvable_csp_edge_case()
    print("[PASS] Unsolvable CSP Edge Case")
    print("\nALL CSP SOLVER TESTS PASSED SUCCESSFULLY!")

