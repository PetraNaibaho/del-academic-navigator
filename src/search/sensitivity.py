"""
Modul Analisis Sensitivitas & Pengujian Skalabilitas CSP Solver.

Mengukur kinerja CSP Solver (AC-3 + Backtracking + MRV + LCV + FC)
terhadap variasi ukuran masalah (skala kecil, sedang, besar)
serta membandingkan efisiensi kombinasi propagasi & heuristik.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple
import random

from src.search.solver import CSPSolutionResult
from src.del_academic_navigator.csp_schedule import (
    ScheduleCourse,
    ScheduleSlot,
    build_academic_schedule_csp,
)


@dataclass
class BenchmarkMetrics:
    scale_name: str
    num_courses: int
    num_slots: int
    config_name: str
    is_satisfied: bool
    nodes_explored: int
    backtracks: int
    domain_prunings: int
    execution_time_ms: float


def generate_benchmark_instance(
    num_courses: int,
    num_slots_per_day: int = 2,
    num_days: int = 3,
    seed: int = 42,
) -> Tuple[List[ScheduleCourse], List[ScheduleSlot]]:
    """
    Menghasilkan data sintetis terkontrol untuk pengujian skala CSP.
    """
    rng = random.Random(seed)

    lecturers = [f"Dosen_{i}" for i in range(1, max(2, num_courses // 2) + 1)]
    cohort_pool = [f"Cohort_{i}" for i in range(1, max(2, num_courses // 2) + 1)]
    rooms = ["GD721", "GD722", "GD512", "GD911"]
    room_caps = {"GD721": 80, "GD722": 75, "GD512": 40, "GD911": 60}

    courses = []
    for i in range(1, num_courses + 1):
        c_id = f"COURSE_{i:02d}"
        lecturer = rng.choice(lecturers)
        selected_cohorts = (rng.choice(cohort_pool),)
        student_count = rng.choice([30, 45, 60])
        requires_lab = (i % 3 == 0)
        courses.append(
            ScheduleCourse(
                course_id=c_id,
                lecturer=lecturer,
                cohorts=selected_cohorts,
                student_count=student_count,
                requires_lab=requires_lab,
            )
        )

    days = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat"][:num_days]
    hours = [8, 10, 13, 15][:num_slots_per_day]

    slots = []
    for day in days:
        for hour in hours:
            for room in rooms:
                is_lab_room = (room == "GD911")
                cap = room_caps[room]
                slots.append(
                    ScheduleSlot(
                        day=day,
                        start_hour=hour,
                        duration_hours=2,
                        room_id=room,
                        room_capacity=cap,
                        is_lab=is_lab_room,
                        day_offset=2,
                    )
                )

    return courses, slots


class CSPSensitivityAnalyzer:
    """
    Analyzer untuk menguji dan mengevaluasi sensitivitas serta konvergensi CSP Solver.
    """

    @staticmethod
    def evaluate_configs_on_instance(
        scale_name: str,
        courses: List[ScheduleCourse],
        slots: List[ScheduleSlot],
    ) -> List[BenchmarkMetrics]:
        """
        Menjalankan 4 variasi konfigurasi solver pada satu instance masalah.
        """
        configs = [
            ("Full CSP (AC-3 + MRV + LCV + FC)", True, True, True, True),
            ("Tanpa Preprocessing AC-3", False, True, True, True),
            ("Tanpa Forward Checking", True, True, True, False),
            ("Backtracking Standar (Tanpa MRV/LCV/FC)", False, False, False, False),
        ]

        results = []
        for name, use_ac3, use_mrv, use_lcv, use_fc in configs:
            instance_solver = build_academic_schedule_csp(courses, slots)
            res: CSPSolutionResult = instance_solver.solve(
                use_ac3_preprocess=use_ac3,
                use_mrv=use_mrv,
                use_lcv=use_lcv,
                use_fc=use_fc,
            )
            results.append(
                BenchmarkMetrics(
                    scale_name=scale_name,
                    num_courses=len(courses),
                    num_slots=len(slots),
                    config_name=name,
                    is_satisfied=res.is_satisfied,
                    nodes_explored=res.nodes_explored,
                    backtracks=res.backtracks,
                    domain_prunings=res.domain_prunings,
                    execution_time_ms=res.execution_time_ms,
                )
            )

        return results

    def run_full_benchmark(self) -> List[BenchmarkMetrics]:
        """
        Menjalankan benchmark lengkap dari skala kecil hingga skala besar.
        """
        all_metrics = []

        # 1. Skala Kecil (3 Courses)
        c_small, s_small = generate_benchmark_instance(num_courses=3, num_slots_per_day=2, num_days=2, seed=10)
        all_metrics.extend(self.evaluate_configs_on_instance("Skala Kecil (3 MK)", c_small, s_small))

        # 2. Skala Sedang (6 Courses)
        c_med, s_med = generate_benchmark_instance(num_courses=6, num_slots_per_day=2, num_days=3, seed=20)
        all_metrics.extend(self.evaluate_configs_on_instance("Skala Sedang (6 MK)", c_med, s_med))

        # 3. Skala Besar (10 Courses)
        c_large, s_large = generate_benchmark_instance(num_courses=10, num_slots_per_day=3, num_days=4, seed=30)
        all_metrics.extend(self.evaluate_configs_on_instance("Skala Besar (10 MK)", c_large, s_large))

        return all_metrics

    def format_markdown_table(self, metrics: List[BenchmarkMetrics]) -> str:
        """
        Format hasil benchmark ke dalam tabel Markdown yang rapi.
        """
        lines = [
            "| Skala Masalah | Konfigurasi Solver | Solusi | Node Dieksplorasi | Backtracks | Domain Prunings | Waktu (ms) |",
            "|---|---|:---:|---:|---:|---:|---:|",
        ]
        for m in metrics:
            status = "Ya" if m.is_satisfied else "Tidak"
            lines.append(
                f"| {m.scale_name} | {m.config_name} | {status} | {m.nodes_explored} | {m.backtracks} | {m.domain_prunings} | {m.execution_time_ms:.3f} |"
            )
        return "\n".join(lines)
