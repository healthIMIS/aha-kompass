"""
def coloring(incidence):
    if incidence > 200:
        return "black"
    elif incidence > 150:
        return "darkred"
    elif incidence > 100:
        return "red"
    elif incidence > 75:
        return "orange"
    elif incidence > 50:
        return "yellow"
    elif incidence > 35:
        return "greenyellow"
    else :
        return "green"
"""
def coloring(incidence):
    if incidence > 500:
        return "d80182"
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