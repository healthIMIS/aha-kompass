def coloring(incidence):
    if incidence >= 500:
        return "#d80182"
    elif incidence > 250:
        return "#651212"
    elif incidence > 100:
        return "#921214"
    elif incidence > 50:
        return "#d03523"
    elif incidence > 5:
        return "#faee7d"
    elif incidence > 0:
        return "#faf7c9"
    else :
        return "#ccf5c4"

colors = [
    {"color": "#ccf5c4", "max": 0},
    {"color": "#faf7c9", "min": 0, "max": 5},
    {"color": "#faee7d", "min": 6, "max": 50},
    {"color": "#d03523", "min": 51, "max": 100},
    {"color": "#921214", "min": 101, "max": 200},
    {"color": "#651212", "min": 201, "max": 500},
    {"color": "#faf7c9", "min": 500}
    ]
