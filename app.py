import streamlit as st
from dataclasses import dataclass
import math
import calendar


# Data Penting 
# ============

MONTHS = [
    ("January", 1), ("February", 2), ("March", 3), ("April", 4),
    ("May", 5), ("June", 6), ("July", 7), ("August", 8),
    ("September", 9), ("October", 10), ("November", 11), ("December", 12)
]

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

    # Penghapusan tanggal pada tahun 1582
    if year == 1582 and month == 10 and 5 <= day <= 14:
        return False, "Tanggal 5-14 Oktober 1582 tidak ada di kalender Gregorian."
    return True, None


# Konversi Gregorian -> JD
# ========================

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



# Konversi JD -> Gregorian
# ========================

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

    return DateTimeInput(year, month, day_int, hour, minute, second, tz_offset)


# Streamlit Dashboard
# ===================

st.set_page_config(page_title="Gregorian ⇄ JD Converter", page_icon="🗓️", layout="centered")

st.title("🗓️ Gregorian ⇄ Julian Day (JD) Converter")

with st.sidebar:
    st.header("Pilihan Mode")
    mode = st.radio(
        "Mode konversi",
        ["Gregorian ➜ Julian Day (JD)", "Julian Day (JD) ➜ Gregorian"],
        help="Pilih arah konversi"
    )

    tz_offset = st.number_input(
        "Offset zona waktu (jam dari UTC)",
        min_value=-14.0, max_value=14.0, step=0.25, value=0.0,
        help="Contoh: Jakarta = +7, Sydney = +10, New York (DST) = -4, India = +5.5"
    )

    st.divider()
    st.markdown("**Catatan penting**")
    st.markdown(
        "- Kalender **Gregorian**: tanggal **5-14 Oktober 1582** tidak ada (dihapus).\n"
        "- Jam/menit/detik kosong dianggap 00:00:00.\n"
        "- Offset bisa negatif/positif, gunakan format desimal (misal +5.5 untuk India)."
    )


# Page Konversi Gregorian -> JD
# =============================
if mode == "Gregorian ➜ Julian Day (JD)":
    st.subheader("Masukan Tanggal Gregorian")

    col1, col2, col3 = st.columns(3)
    with col1:
        year = st.number_input("Tahun", value=2025, step=1)
    with col2:
        month_name = st.selectbox("Bulan", [m[0] for m in MONTHS], index=7)
        month = dict(MONTHS)[month_name]
    with col3:
        day = st.number_input("Tanggal", value=30, min_value=1, max_value=31, step=1)

    colh, colm, cols = st.columns(3)
    with colh:
        hour = st.number_input("Jam (0-23)", min_value=0, max_value=23, value=0)
    with colm:
        minute = st.number_input("Menit (0-59)", min_value=0, max_value=59, value=0)
    with cols:
        second = st.number_input("Detik (0-59)", min_value=0, max_value=59, value=0)

    dt_in = DateTimeInput(
        year=int(year), month=int(month), day=int(day),
        hour=int(hour), minute=int(minute), second=int(second),
        tz_offset_hours=float(tz_offset)
    )

    ok, msg = is_valid_gregorian_date(dt_in.year, dt_in.month, dt_in.day)
    if not ok:
        st.error(msg)
    else:
        if st.button("Konversi ke JD"):
            jd = gregorian_to_jd(dt_in)
            month_name = calendar.month_name[dt_in.month]
            st.success(f"Gregorian {dt_in.day} {month_name} {dt_in.year} "
                    f"{dt_in.hour:02}:{dt_in.minute:02}:{dt_in.second:02} (UTC{dt_in.tz_offset_hours:+}) "
                    f"→ JD = {jd}")


# Page Konversi JD -> Gregorian
# =============================
else:
    st.subheader("Masukan Julian Day Number (JD)")
    jd_in = st.number_input("Julian Day Number", value=2451545.0, step=0.1, format="%.5f")

    if st.button("Konversi ke Gregorian"):
        result = jd_to_gregorian(jd_in, tz_offset)
        month_name = calendar.month_name[result.month]
        st.success(f"JD {jd_in} (UTC{tz_offset:+}) → "
                f"Gregorian {result.day} {month_name} {result.year} "
                f"{result.hour:02}:{result.minute:02}:{result.second:02}")

