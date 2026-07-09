from datetime import date
from data.banner_data import (
    BANNERS,
    TOTAL_DAYS,
    REFERENCE_DAY,
    REFERENCE_YEAR,
    REFERENCE_MONTH,
    REFERENCE_DATE,
)


def get_current_day():
    ref = date(REFERENCE_YEAR, REFERENCE_MONTH, REFERENCE_DATE)
    today = date.today()

    diff = (today - ref).days
    day = ((REFERENCE_DAY - 1 + diff) % TOTAL_DAYS) + 1

    return day


def get_banner(day=None):
    if day is None:
        day = get_current_day()

    return BANNERS.get(day)


def get_next_banner(day=None):
    if day is None:
        day = get_current_day()

    current = get_banner(day)

    for i in range(1, TOTAL_DAYS + 1):
        check = ((day - 1 + i) % TOTAL_DAYS) + 1
        banner = BANNERS.get(check)

        if banner and (
            current is None or banner["name"] != current["name"]
        ):
            return check, banner

    return None, None


def get_previous_banner(day=None):
    if day is None:
        day = get_current_day()

    current = get_banner(day)

    for i in range(1, TOTAL_DAYS + 1):
        check = ((day - 1 - i) % TOTAL_DAYS) + 1
        banner = BANNERS.get(check)

        if banner and (
            current is None or banner["name"] != current["name"]
        ):
            return check, banner

    return None, None
