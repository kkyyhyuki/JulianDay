import math
from dataclasses import dataclass

@dataclass
class HijriDate:
    year: int
    month: int
    day: int

LEAP_YEARS_IN_30 = {2, 5, 7, 10, 13, 16, 18, 21, 24, 26, 29}

def is_leap_hijri(year: int) -> bool:
    return (year % 30) in LEAP_YEARS_IN_30

def days_in_month_hijri(year: int, month: int) -> int:
    if month % 2 == 1:
        return 30
    elif month != 12:
        return 29
    else: 
        return 30 if is_leap_hijri(year) else 29

def is_valid_hijri_date(year: int, month: int, day: int):
    if month < 1 or month > 12:
        return False, "Bulan Hijriah harus 1-12."
    dim = days_in_month_hijri(year, month)
    if day < 1 or day > dim:
        return False, f"Tanggal {day} tidak valid untuk bulan {month} tahun {year} H."
    return True, None


def hijri_to_jd(year: int, month: int, day: int) -> float:
    return (day
            + math.ceil(29.5 * (month - 1))
            + (year - 1) * 354
            + math.floor((3 + 11 * year) / 30)
            + 1948439.5 - 1)

def jd_to_hijri(JD: float) -> HijriDate:
    JD = math.floor(JD) + 0.5
    days_since_epoch = JD - 1948439.5

    year = int((30 * days_since_epoch + 10646) // 10631)
    month = int(min(12, math.ceil((days_since_epoch - (29 + hijri_to_jd(year, 1, 1) - 1948439.5)) / 29.5) + 1))
    day = int(JD - hijri_to_jd(year, month, 1) + 1)

    return HijriDate(year, month, day)
