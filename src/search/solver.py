"""
Modul CSP Solver (Constraint Satisfaction Problems) untuk Del-Academic Navigator.

Mengimplementasikan:
1. Formulasi CSP Formal (X, D, C)
2. Propagasi Batasan AC-3 (Arc Consistency 3)
3. Backtracking Search dengan Heuristik:
   - Minimum Remaining Values (MRV) untuk Pemilihan Variabel
   - Degree Heuristic sebagai Tie-Breaker MRV
   - Least Constraining Value (LCV) untuk Pengurutan Domain
   - Forward Checking (FC) / Inference saat pencarian
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
import copy
import time


@dataclass
class CSPSolutionResult:
    """
    Hasil eksekusi pencarian CSP Solver.
    """
    assignment: Optional[Dict[str, Any]]
    is_satisfied: bool
    nodes_explored: int = 0
    backtracks: int = 0
    domain_prunings: int = 0
    execution_time_ms: float = 0.0
    algorithm: str = "Backtracking CSP Solver (AC-3 + MRV + LCV + FC)"


class BinaryConstraint:
    """
    Representasi Batasan Biner antara dua variabel Xi dan Xj.
    """

    def __init__(
        self,
        var1: str,
        var2: str,
        relation: Callable[[Any, Any], bool],
        name: str = "BinaryConstraint",
    ):
        self.var1 = var1
        self.var2 = var2
        self.relation = relation
        self.name = name

    def is_satisfied(self, val1: Any, val2: Any) -> bool:
        """Evaluasi apakah penugasan (val1, val2) memenuhi batasan."""
        return self.relation(val1, val2)

    def __repr__(self) -> str:
        return f"<{self.name}: {self.var1} <-> {self.var2}>"


class CSPSolver:
    """
    Constraint Satisfaction Problem (CSP) Solver Cerdas.
    
    Komponen:
    - X: Himpunan Variabel
    - D: Himpunan Domain (Mapping variabel ke list/set nilai)
    - C: Himpunan Batasan (Binary & Unary Constraints)
    """

    def __init__(
        self,
        variables: List[str],
        domains: Dict[str, List[Any]],
    ):
        self.variables: List[str] = list(variables)
        self.domains: Dict[str, List[Any]] = {
            v: list(domains[v]) for v in variables
        }
        self.constraints: List[BinaryConstraint] = []
        self.neighbors: Dict[str, Set[str]] = {v: set() for v in variables}

    def add_constraint(self, constraint: BinaryConstraint) -> None:
        """Menambahkan batasan biner ke dalam masalah CSP."""
        self.constraints.append(constraint)
        self.neighbors[constraint.var1].add(constraint.var2)
        self.neighbors[constraint.var2].add(constraint.var1)

    def get_constraints_between(self, var1: str, var2: str) -> List[BinaryConstraint]:
        """Mengembalikan daftar batasan biner antara var1 dan var2."""
        res = []
        for c in self.constraints:
            if (c.var1 == var1 and c.var2 == var2) or (c.var1 == var2 and c.var2 == var1):
                res.append(c)
        return res

    def is_consistent_pair(self, var1: str, val1: Any, var2: str, val2: Any) -> bool:
        """
        Memeriksa apakah penugasan val1 pada var1 dan val2 pada var2 konsisten
        terhadap seluruh batasan antara var1 dan var2.
        """
        for c in self.constraints:
            if c.var1 == var1 and c.var2 == var2:
                if not c.is_satisfied(val1, val2):
                    return False
            elif c.var1 == var2 and c.var2 == var1:
                if not c.is_satisfied(val2, val1):
                    return False
        return True

    def revise(self, xi: str, xj: str, current_domains: Dict[str, List[Any]]) -> Tuple[bool, int]:
        """
        Prosedur Revise(Xi, Xj) untuk AC-3.
        
        Memeriksa setiap elemen x in D_i. Jika x tidak memiliki pasangan pendukung (support)
        y in D_j yang memenuhi batasan biner (xi, xj), maka x dihapus dari D_i.
        
        Mengembalikan (revised, number_of_prunings).
        """
        revised = False
        pruned_count = 0
        new_di = []

        for x in current_domains[xi]:
            # Cari support di D_j
            has_support = False
            for y in current_domains[xj]:
                if self.is_consistent_pair(xi, x, xj, y):
                    has_support = True
                    break
            
            if has_support:
                new_di.append(x)
            else:
                revised = True
                pruned_count += 1

        if revised:
            current_domains[xi] = new_di

        return revised, pruned_count

    def ac3(self, current_domains: Optional[Dict[str, List[Any]]] = None) -> Tuple[bool, Dict[str, List[Any]], int]:
        """
        Algoritma Arc Consistency 3 (AC-3).
        
        Memangkas nilai-nilai domain yang inkonsisten secara sistematis sebelum
        atau selama proses pencarian backtracking.
        
        Mengembalikan (is_consistent, pruned_domains, total_prunings).
        """
        if current_domains is None:
            domains_copy = {v: list(self.domains[v]) for v in self.variables}
        else:
            domains_copy = {v: list(current_domains[v]) for v in self.variables}

        # Inisialisasi antrean queue dengan seluruh busur berarah (Xi, Xj)
        queue: List[Tuple[str, str]] = []
        for c in self.constraints:
            queue.append((c.var1, c.var2))
            queue.append((c.var2, c.var1))

        total_prunings = 0

        while queue:
            xi, xj = queue.pop(0)
            revised, pruned = self.revise(xi, xj, domains_copy)
            total_prunings += pruned

            if revised:
                if len(domains_copy[xi]) == 0:
                    # Kontradiksi: Domain menjadi kosong, tidak ada solusi
                    return False, domains_copy, total_prunings
                
                # Masukkan kembali seluruh busur tetangga Xk -> Xi (k != j)
                for xk in self.neighbors[xi]:
                    if xk != xj:
                        if (xk, xi) not in queue:
                            queue.append((xk, xi))

        return True, domains_copy, total_prunings

    def select_unassigned_variable_mrv(
        self, assignment: Dict[str, Any], current_domains: Dict[str, List[Any]]
    ) -> str:
        """
        Heuristik Minimum Remaining Values (MRV) dengan Degree Heuristic sebagai Tie-Breaker.
        
        Memilih variabel yang belum diisi dengan sisa nilai domain paling sedikit (Fail-First).
        Jika terdapat kesamaan (tie), pilih variabel dengan derajat tetangga belum terisi terbanyak.
        """
        unassigned = [v for v in self.variables if v not in assignment]
        
        # Sort key: (jumlah nilai domain tersisa, -jumlah tetangga belum terisi)
        def mrv_key(var: str) -> Tuple[int, int]:
            domain_size = len(current_domains[var])
            unassigned_neighbors = sum(
                1 for n in self.neighbors[var] if n not in assignment
            )
            return (domain_size, -unassigned_neighbors)

        unassigned.sort(key=mrv_key)
        return unassigned[0]

    def order_domain_values_lcv(
        self, var: str, assignment: Dict[str, Any], current_domains: Dict[str, List[Any]]
    ) -> List[Any]:
        """
        Heuristik Least Constraining Value (LCV).
        
        Mengurutkan nilai domain untuk `var` berdasarkan seberapa sedikit nilai tersebut
        mengeliminasi opsi pada variabel tetangga yang belum terisi (Fail-Last).
        """
        unassigned_neighbors = [
            n for n in self.neighbors[var] if n not in assignment
        ]

        def lcv_key(val: Any) -> int:
            ruled_out = 0
            for neighbor in unassigned_neighbors:
                for n_val in current_domains[neighbor]:
                    if not self.is_consistent_pair(var, val, neighbor, n_val):
                        ruled_out += 1
            return ruled_out

        domain_values = list(current_domains[var])
        domain_values.sort(key=lcv_key)
        return domain_values

    def forward_check(
        self,
        var: str,
        val: Any,
        assignment: Dict[str, Any],
        current_domains: Dict[str, List[Any]],
    ) -> Tuple[bool, Dict[str, List[Any]], int]:
        """
        Propagasi Forward Checking (FC).
        
        Saat `var` diberi nilai `val`, pangkas nilai inkonsisten pada domain tetangga.
        Mengembalikan (is_valid, new_domains, prunings).
        """
        new_domains = {v: list(current_domains[v]) for v in self.variables}
        new_domains[var] = [val]
        prunings = 0

        for neighbor in self.neighbors[var]:
            if neighbor not in assignment:
                valid_n_vals = []
                for n_val in new_domains[neighbor]:
                    if self.is_consistent_pair(var, val, neighbor, n_val):
                        valid_n_vals.append(n_val)
                    else:
                        prunings += 1

                if not valid_n_vals:
                    # Domain tetangga menjadi kosong
                    return False, new_domains, prunings

                new_domains[neighbor] = valid_n_vals

        return True, new_domains, prunings

    def solve(
        self,
        use_ac3_preprocess: bool = True,
        use_mrv: bool = True,
        use_lcv: bool = True,
        use_fc: bool = True,
    ) -> CSPSolutionResult:
        """
        Menjalankan pencarian solusi CSP menggunakan Backtracking dengan heuristik pilihan.
        """
        start_time = time.perf_counter()
        nodes_explored = 0
        backtracks = 0
        total_prunings = 0

        # Preprocessing AC-3
        current_domains = {v: list(self.domains[v]) for v in self.variables}
        if use_ac3_preprocess:
            is_consistent, ac3_domains, prunings = self.ac3(current_domains)
            total_prunings += prunings
            if not is_consistent:
                elapsed_ms = (time.perf_counter() - start_time) * 1000.0
                return CSPSolutionResult(
                    assignment=None,
                    is_satisfied=False,
                    nodes_explored=0,
                    backtracks=0,
                    domain_prunings=total_prunings,
                    execution_time_ms=elapsed_ms,
                )
            current_domains = ac3_domains

        def backtrack(
            assignment: Dict[str, Any],
            domains: Dict[str, List[Any]],
        ) -> Optional[Dict[str, Any]]:
            nonlocal nodes_explored, backtracks, total_prunings

            # Goal Test: Jika seluruh variabel telah diberi nilai
            if len(assignment) == len(self.variables):
                return assignment

            # Selection Variabel (MRV vs Standar)
            if use_mrv:
                var = self.select_unassigned_variable_mrv(assignment, domains)
            else:
                unassigned = [v for v in self.variables if v not in assignment]
                var = unassigned[0]

            # Ordering Domain Values (LCV vs Standar)
            if use_lcv:
                values = self.order_domain_values_lcv(var, assignment, domains)
            else:
                values = list(domains[var])

            for val in values:
                nodes_explored += 1

                # Check Consistency dengan assignment saat ini
                is_consistent = True
                for assigned_var, assigned_val in assignment.items():
                    if not self.is_consistent_pair(var, val, assigned_var, assigned_val):
                        is_consistent = False
                        break

                if is_consistent:
                    assignment[var] = val

                    # Propagasi Forward Checking
                    if use_fc:
                        fc_success, new_domains, fc_prunings = self.forward_check(
                            var, val, assignment, domains
                        )
                        total_prunings += fc_prunings
                        if fc_success:
                            result = backtrack(assignment, new_domains)
                            if result is not None:
                                return result
                    else:
                        result = backtrack(assignment, domains)
                        if result is not None:
                            return result

                    # Backtrack (Undo assignment)
                    del assignment[var]
                    backtracks += 1

            return None

        final_assignment = backtrack({}, current_domains)
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        return CSPSolutionResult(
            assignment=final_assignment,
            is_satisfied=final_assignment is not None,
            nodes_explored=nodes_explored,
            backtracks=backtracks,
            domain_prunings=total_prunings,
            execution_time_ms=elapsed_ms,
        )
