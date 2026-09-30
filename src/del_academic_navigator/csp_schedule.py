"""Formal CSP model for make-up class scheduling under IT Del's hard rules."""

from dataclasses import dataclass
from typing import Iterable, Tuple

from src.del_academic_navigator.rooms import get_room_info
from src.del_academic_navigator.rules import is_lead_time_valid
from src.search.solver import BinaryConstraint, CSPSolver


@dataclass(frozen=True)
class ScheduleCourse:
    course_id: str
    lecturer: str
    cohorts: Tuple[str, ...]
    student_count: int
    requires_lab: bool = False


@dataclass(frozen=True)
class ScheduleSlot:
    day: str
    start_hour: int
    duration_hours: int
    room_id: str
    room_capacity: int
    is_lab: bool = False
    day_offset: int = 2

    @property
    def end_hour(self) -> int:
        return self.start_hour + self.duration_hours


def _is_valid_slot(course: ScheduleCourse, slot: ScheduleSlot) -> bool:
    if (
        slot.duration_hours <= 0
        or slot.room_capacity <= 0
        or not is_lead_time_valid(0, slot.day_offset)
        or slot.start_hour < 8
        or slot.end_hour > 17
        or (slot.start_hour < 13 and slot.end_hour > 12)
        or slot.room_capacity < course.student_count
    ):
        return False

    if course.student_count > 40 and slot.room_id not in {"GD721", "GD722"}:
        return False

    return not course.requires_lab or slot.is_lab


def _slots_compatible(
    course_a: ScheduleCourse,
    slot_a: ScheduleSlot,
    course_b: ScheduleCourse,
    slot_b: ScheduleSlot,
) -> bool:
    if slot_a.day != slot_b.day:
        return True

    overlaps = (
        slot_a.start_hour < slot_b.end_hour
        and slot_b.start_hour < slot_a.end_hour
    )
    if not overlaps:
        return True

    shares_resource = (
        course_a.lecturer == course_b.lecturer
        or bool(set(course_a.cohorts) & set(course_b.cohorts))
        or slot_a.room_id == slot_b.room_id
    )
    return not shares_resource


def build_academic_schedule_csp(
    courses: Iterable[ScheduleCourse],
    slots: Iterable[ScheduleSlot],
) -> CSPSolver:
    """Build X, D, and binary C from course data and SOP hard constraints."""
    course_list = list(courses)
    slot_list = list(slots)
    variables = [course.course_id for course in course_list]

    if len(set(variables)) != len(variables):
        raise ValueError("Course IDs must be unique.")
    if any(not course.course_id or not course.lecturer for course in course_list):
        raise ValueError("Every course must have a course ID and lecturer.")
    if any(course.student_count <= 0 for course in course_list):
        raise ValueError("Every course must have at least one student.")
    if any(not course.cohorts for course in course_list):
        raise ValueError("Every course must identify at least one student cohort.")
    if any(
        not cohort
        for course in course_list
        for cohort in course.cohorts
    ):
        raise ValueError("Student cohort identifiers must not be empty.")
    if any(not slot.day or not slot.room_id for slot in slot_list):
        raise ValueError("Every slot must identify a day and room.")
    for slot in slot_list:
        room_info = get_room_info(slot.room_id)
        if room_info is not None and room_info.capacity != slot.room_capacity:
            raise ValueError(
                f"Capacity for {slot.room_id} must match the room master "
                f"({room_info.capacity})."
            )

    domains = {
        course.course_id: [
            slot for slot in slot_list if _is_valid_slot(course, slot)
        ]
        for course in course_list
    }
    solver = CSPSolver(variables, domains)

    for index, course_a in enumerate(course_list):
        for course_b in course_list[index + 1 :]:
            solver.add_constraint(
                BinaryConstraint(
                    course_a.course_id,
                    course_b.course_id,
                    lambda slot_a, slot_b, a=course_a, b=course_b: _slots_compatible(
                        a, slot_a, b, slot_b
                    ),
                    f"NoAcademicResourceConflict({course_a.course_id},{course_b.course_id})",
                )
            )

    return solver
