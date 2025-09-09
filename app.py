import streamlit as st
import calendar
from gregorian_converter import (
    DateTimeInput, is_valid_gregorian_date,
    gregorian_to_jd, jd_to_gregorian
)
from hijriah_converter import hijri_to_jd, jd_to_hijri, is_valid_hijri_date


# Bulan Gregorian 
MONTHS = [
    ("January", 1), ("February", 2), ("March", 3), ("April", 4),
    ("May", 5), ("June", 6), ("July", 7), ("August", 8),
    ("September", 9), ("October", 10), ("November", 11), ("December", 12)
]

# Bulan Hijriah
HIJRI_MONTHS = [
    ("Muharram", 1), ("Safar", 2), ("Rabiʽ al-Awwal", 3), ("Rabiʽ al-Thani", 4),
    ("Jumada al-Awwal", 5), ("Jumada al-Thani", 6), ("Rajab", 7), ("Shaʽban", 8),
    ("Ramadan", 9), ("Shawwal", 10), ("Dhu al-Qiʽdah", 11), ("Dhu al-Hijjah", 12)
]

# Mapping angka -> nama bulan Hijriah
HIJRI_MONTH_MAP = {num: name for name, num in HIJRI_MONTHS}

st.set_page_config(page_title="Calendar Converter", page_icon="🗓️", layout="centered")
st.title("🗓️ Calendar Converter")

# --- Sidebar ---
with st.sidebar:
    st.header("Pilih Jenis Konversi")
    main_mode = st.radio(
        "Jenis kalender",
        ["Gregorian", "Hijriah", "Silang"]
    )

    if main_mode == "Gregorian":
        sub_mode = st.radio(
            "Mode konversi (Gregorian)",
            ["Gregorian ➜ Julian Day (JD)", "Julian Day (JD) ➜ Gregorian"]
        )
        tz_offset = st.number_input(
            "Offset zona waktu (jam dari UTC)",
            min_value=-14.0, max_value=14.0, step=0.25, value=0.0,
            help="Contoh: Jakarta = +7, Sydney = +10, New York (DST) = -4, India = +5.5"
        )

    elif main_mode == "Hijriah":
        sub_mode = st.radio(
            "Mode konversi (Hijriah)",
            ["Hijriah ➜ Julian Day (JD)", "Julian Day (JD) ➜ Hijriah"]
        )
        tz_offset = 0.0 

    else:  
        sub_mode = st.radio(
            "Mode konversi silang",
            ["Gregorian ➜ Hijriah", "Hijriah ➜ Gregorian"]
        )
        tz_offset = 0.0  

# --- Gregorian ---
if main_mode == "Gregorian":
    if sub_mode == "Gregorian ➜ Julian Day (JD)":
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
            hour = st.number_input("Jam", min_value=0, max_value=23, value=0)
        with colm:
            minute = st.number_input("Menit", min_value=0, max_value=59, value=0)
        with cols:
            second = st.number_input("Detik", min_value=0, max_value=59, value=0)

        dt_in = DateTimeInput(int(year), int(month), int(day),
                              int(hour), int(minute), int(second), float(tz_offset))

        ok, msg = is_valid_gregorian_date(dt_in.year, dt_in.month, dt_in.day)
        if not ok:
            st.error(msg)
        else:
            if st.button("Konversi ke JD (Gregorian)"):
                jd = gregorian_to_jd(dt_in)
                month_name = calendar.month_name[dt_in.month]
                st.success(f"{dt_in.day} {month_name} {dt_in.year} "
                           f"{dt_in.hour:02}:{dt_in.minute:02}:{dt_in.second:02} "
                           f"(UTC{dt_in.tz_offset_hours:+}) → JD = {jd}")

    elif sub_mode == "Julian Day (JD) ➜ Gregorian":
        st.subheader("Masukan Julian Day Number (JD)")
        jd_in = st.number_input("Julian Day Number (Gregorian)", value=2451545.0, step=0.1, format="%.5f")
        if st.button("Konversi ke Gregorian"):
            result = jd_to_gregorian(jd_in, tz_offset)
            month_name = calendar.month_name[result.month]
            st.success(f"JD {jd_in} (UTC{tz_offset:+}) → "
                       f"{result.day} {month_name} {result.year} "
                       f"{result.hour:02}:{result.minute:02}:{result.second:02}")

# --- Hijriah ---
elif main_mode == "Hijriah":
    if sub_mode == "Hijriah ➜ Julian Day (JD)":
        st.subheader("Masukan Tanggal Hijriah")
        year = st.number_input("Tahun H", value=1447, step=1)
        month_name = st.selectbox("Bulan Hijriah", [m[0] for m in HIJRI_MONTHS], index=0)
        month = dict(HIJRI_MONTHS)[month_name]
        day = st.number_input("Tanggal", min_value=1, max_value=30, value=1)

        if st.button("Konversi ke JD (Hijriah)"):
            ok, msg = is_valid_hijri_date(int(year), int(month), int(day))
            if not ok:
                st.error(msg)
            else:
                jd = hijri_to_jd(int(year), int(month), int(day))
                st.success(f"Hijri {day} {month_name} {year} H → JD = {jd}")

    elif sub_mode == "Julian Day (JD) ➜ Hijriah":
        st.subheader("Masukan Julian Day Number (JD)")
        jd_in = st.number_input("Julian Day Number (Hijriah)", value=2451545.0, step=0.1, format="%.5f")
        if st.button("Konversi ke Hijriah"):
            result = jd_to_hijri(jd_in)
            month_name = HIJRI_MONTH_MAP[result.month]   
            st.success(f"JD {jd_in} → {result.day} {month_name} {result.year} H")

elif main_mode == "Silang":
    if sub_mode == "Gregorian ➜ Hijriah":
        st.subheader("Masukan Tanggal Gregorian untuk konversi silang")
        year = st.number_input("Tahun (Gregorian)", value=2025, step=1)
        month_name = st.selectbox("Bulan Gregorian", [m[0] for m in MONTHS], index=7)
        month = dict(MONTHS)[month_name]
        day = st.number_input("Tanggal", value=30, min_value=1, max_value=31, step=1)

        dt_in = DateTimeInput(int(year), int(month), int(day))
        ok, msg = is_valid_gregorian_date(dt_in.year, dt_in.month, dt_in.day)
        if not ok:
            st.error(msg)
        else:
            if st.button("Konversi Gregorian ➜ Hijriah"):
                jd = gregorian_to_jd(dt_in)
                hijri_date = jd_to_hijri(jd)
                month_name = HIJRI_MONTH_MAP[hijri_date.month]  
                st.success(f"{day} {calendar.month_name[dt_in.month]} {year} → "
                           f"Hijri {hijri_date.day} {month_name} {hijri_date.year} H")

    elif sub_mode == "Hijriah ➜ Gregorian":
        st.subheader("Masukan Tanggal Hijriah untuk konversi silang")
        year = st.number_input("Tahun H (Hijriah)", value=1447, step=1)
        month_name = st.selectbox("Bulan Hijriah (silang)", [m[0] for m in HIJRI_MONTHS], index=0)
        month = dict(HIJRI_MONTHS)[month_name]
        day = st.number_input("Tanggal H", min_value=1, max_value=30, value=1)

        ok, msg = is_valid_hijri_date(int(year), int(month), int(day))
        if not ok:
            st.error(msg)
        else:
            if st.button("Konversi Hijriah ➜ Gregorian"):
                jd = hijri_to_jd(int(year), int(month), int(day))
                greg_date = jd_to_gregorian(jd)
                st.success(f"Hijri {day} {month_name} {year} H → "
                           f"{greg_date.day} {calendar.month_name[greg_date.month]} {greg_date.year}")
