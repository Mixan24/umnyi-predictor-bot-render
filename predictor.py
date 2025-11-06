def calculate_goal_probability(stats: dict) -> float:
    attacks = stats.get("attacks", 0)
    dangerous = stats.get("dangerous_attacks", 0)
    shots_on = stats.get("shots_on", 0)
    shots_total = stats.get("shots_total", 0)
    corners = stats.get("corners", 0)
    possession = stats.get("possession", 50)

    pressure_index = (
        attacks * 0.2 +
        dangerous * 0.4 +
        shots_on * 4 +
        shots_total * 1 +
        corners * 1.5 +
        (possession - 50) * 1.2
    ) / 10
    probability = max(5, min(95, pressure_index))
    return round(probability, 1)
