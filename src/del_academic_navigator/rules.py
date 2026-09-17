def is_lead_time_valid(request_day: int, target_day: int) -> bool:
    return (target_day - request_day) >= 2


def calculate_room_cost(room_name: str, student_count: int) -> float:
    is_large_room = room_name in ["GD721", "GD722"]
    if is_large_room and student_count <= 40:
        return 15.0
    elif is_large_room and student_count > 40:
        return 2.0
    else:
        return 1.0