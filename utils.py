from datetime import date, timedelta

def today():
    return date.today()

def format_points(points):
    if points > 0:
        return f"+{points}"
    return str(points)
