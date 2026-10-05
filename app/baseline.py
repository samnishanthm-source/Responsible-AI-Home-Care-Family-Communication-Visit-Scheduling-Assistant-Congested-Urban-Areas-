def baseline_message(visit: dict) -> str:
    status = visit.get("visit_status")
    eta = visit.get("estimated_arrival")
    if status == "delayed":
        return f"Your visit is delayed. ETA: {eta}."
    if status == "scheduled":
        return f"Your visit is scheduled. ETA: {eta}."
    if status == "completed":
        return "Your visit has been completed."
    if status == "cancelled":
        return "Your visit has been cancelled."
    if status == "in_progress":
        return "Your visit is in progress."
    return "No information available."
