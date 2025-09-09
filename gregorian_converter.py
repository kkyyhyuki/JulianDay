import math
import datetime
from dataclasses import dataclass

@dataclass
class DateTimeInput:
    year: int
    month: int
    day: int
    hour: int = 0
    minute: int = 0
    second: int = 0
    tz_offset_hours: float = 0.0


def is_leap_gregorian(year: int) -> bool:
    return (year % 4 == 0) and ((year % 100 != 0) or (year % 400 == 0))


def days_in_month_gregorian(year: int, month: int) -> int:
    if month == 2:
        return 29 if is_leap_gregorian(year) else 28
    if month in (4, 6, 9, 11):
        return 30
    return 31


def is_valid_gregorian_date(year: int, month: int, day: int):
    if month < 1 or month > 12:
        return False, "Bulan Gregorian harus 1-12."
    dim = days_in_month_gregorian(year, month)
    if day < 1 or day > dim:
        return False, f"Tanggal Gregorian {day} tidak valid untuk {month}/{year}."
    if year == 1582 and month == 10 and 5 <= day <= 14:
        return False, "Tanggal 5-14 Oktober 1582 tidak ada di kalender Gregorian."
    return True, None


def gregorian_to_jd(dt: DateTimeInput) -> float:
    Y, M, D = dt.year, dt.month, dt.day
    frac_day = (dt.hour - dt.tz_offset_hours + dt.minute/60 + dt.second/3600) / 24
    D = D + frac_day

    if M <= 2:
        Y -= 1
        M += 12

    if (dt.year > 1582) or \
       (dt.year == 1582 and dt.month > 10) or \
       (dt.year == 1582 and dt.month == 10 and dt.day >= 15):
        A = Y // 100
        B = 2 - A + A // 4
    else:
        B = 0

    JD = 1720994.5 + math.floor(365.25 * Y) \
                   + math.floor(30.6001 * (M + 1)) \
                   + D + B
    return JD


def jd_to_gregorian(JD: float, tz_offset: float = 0.0) -> DateTimeInput:
    JD = JD + 0.5
    Z = int(JD)
    F = JD - Z

    if Z < 2299161:
        A = Z
    else:
        alpha = int((Z - 1867216.25) / 36524.25)
        A = Z + 1 + alpha - alpha // 4

    B = A + 1524
    C = int((B - 122.1) / 365.25)
    D = int(365.25 * C)
    E = int((B - D) / 30.6001)

    day = B - D - int(30.6001 * E) + F
    month = E - 1 if E < 14 else E - 13
    year = C - 4716 if month > 2 else C - 4715

    day_int = int(day)
    frac = day - day_int
    seconds_in_day = int(round(frac * 86400))

    hour = (seconds_in_day // 3600) + int(tz_offset)
    minute = (seconds_in_day % 3600) // 60
    second = seconds_in_day % 60

    dt = datetime.datetime(year, month, day_int, 0, 0, 0)
    dt = dt + datetime.timedelta(hours=hour, minutes=minute, seconds=second)

    return DateTimeInput(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, tz_offset)
