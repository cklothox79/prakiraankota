import streamlit as st
import requests
import pandas as pd
from datetime import date
from streamlit_folium import st_folium
import folium
import plotly.graph_objects as go

st.set_page_config(page_title="CUACA PERJALANAN", layout="wide")
st.title("\U0001F553 CUACA PERJALANAN")
st.markdown("**Editor: Ferri Kusuma (STMKG/M8TB_14.22.0003_2025)**")
st.write("Lihat prakiraan suhu, hujan, awan, kelembapan, dan angin setiap jam untuk lokasi dan tanggal yang kamu pilih.")

# Mode tema
mode = st.radio("\U0001F319 Pilih Mode Tampilan:", ["Siang", "Malam"], horizontal=True)
dark_mode = mode == "Malam"

# Tema warna
warna = {
    "cuaca_box": "#ffffff" if not dark_mode else "#1e1e1e",
    "cuaca_teks": "#222222" if not dark_mode else "#dddddd",
    "ekstrem_bg": "#fff3f3" if not dark_mode else "#330000",
    "ekstrem_teks": "#b30000" if not dark_mode else "#ff6666",
    "hujan_bg": "#e6f3ff" if not dark_mode else "#002b45",
    "hujan_teks": "#003355" if not dark_mode else "#aad4ff",
    "border_default": "#444" if not dark_mode else "#888"
}

tanggal = st.date_input("\U0001F4C5 Pilih tanggal perjalanan:", value=date.today(), min_value=date.today())
kota = st.text_input("\U0001F4DD Masukkan nama kota (opsional):")

def get_coordinates(nama_kota):
    url = f"https://nominatim.openstreetmap.org/search?q={nama_kota}&format=json&limit=1"
    headers = {"User-Agent": "cuaca-perjalanan-app"}
    r = requests.get(url, headers=headers)
    if r.status_code == 200 and r.json():
        data = r.json()[0]
        return float(data["lat"]), float(data["lon"])
    return None, None

lat = lon = None
lokasi_sumber = ""

st.markdown("### \U0001F5FA️ Klik lokasi di peta atau masukkan nama kota")
default_location = [-2.5, 117.0]
m = folium.Map(location=default_location, zoom_start=5)

if kota:
    lat, lon = get_coordinates(kota)
    if lat and lon:
        lokasi_sumber = "Kota"
        folium.Marker([lat, lon], tooltip=f"\U0001F4CD {kota.title()}").add_to(m)
        m.location = [lat, lon]
        m.zoom_start = 9

m.add_child(folium.LatLngPopup())

with st.container():
    col1, col2 = st.columns([2, 1])
    with col1:
        map_data = st_folium(m, height=400, width=700)

    if map_data and map_data["last_clicked"]:
        lat = map_data["last_clicked"]["lat"]
        lon = map_data["last_clicked"]["lng"]
        lokasi_sumber = "Peta"
        st.success(f"\U0001F4CD Lokasi dari peta: {lat:.4f}, {lon:.4f}")

    def get_weather(lat, lon, tanggal):
        tgl_str = tanggal.strftime("%Y-%m-%d")
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}"
            f"&hourly=temperature_2m,precipitation,cloudcover,weathercode,"
            f"relativehumidity_2m,windspeed_10m,winddirection_10m,pressure_msl"
            f"&current_weather=true"
            f"&timezone=auto&start_date={tgl_str}&end_date={tgl_str}"
        )
        r = requests.get(url)
        return r.json() if r.status_code == 200 else None

    weather_icon = {
        0: ("\u2600\ufe0f", "Cerah"), 1: ("\U0001F324\ufe0f", "Cerah Berawan"), 2: ("\u26c5", "Sebagian Berawan"),
        3: ("\u2601\ufe0f", "Berawan"), 45: ("\U0001F32B\ufe0f", "Berkabut"), 48: ("\U0001F32B\ufe0f", "Kabut Tebal"),
        51: ("\U0001F326\ufe0f", "Gerimis Ringan"), 53: ("\U0001F326\ufe0f", "Gerimis"), 55: ("\U0001F327\ufe0f", "Gerimis Lebat"),
        61: ("\U0001F326\ufe0f", "Hujan Ringan"), 63: ("\U0001F327\ufe0f", "Hujan Sedang"), 65: ("\U0001F327\ufe0f", "Hujan Lebat"),
        80: ("\U0001F327\ufe0f", "Hujan Singkat"), 81: ("\U0001F327\ufe0f", "Hujan Singkat Sedang"), 82: ("\U0001F327\ufe0f", "Hujan Singkat Lebat"),
        95: ("\u26c8\ufe0f", "Badai Petir"), 96: ("\u26c8\ufe0f", "Petir + Es"), 99: ("\u26c8\ufe0f", "Badai Parah")
    }

    if lat and lon and tanggal:
        data = get_weather(lat, lon, tanggal)
        if data and "hourly" in data:
            d = data["hourly"]
            waktu = d["time"]
            jam_labels = [w[-5:] for w in waktu]
            suhu = d["temperature_2m"]
            hujan = d["precipitation"]
            awan = d["cloudcover"]
            kode = d["weathercode"]
            rh = d["relativehumidity_2m"]
            angin_speed = d["windspeed_10m"]
            angin_dir = d["winddirection_10m"]
            tekanan = d["pressure_msl"]

            try:
                idx_12 = jam_labels.index("12:00")
            except:
                idx_12 = 0

            ikon, deskripsi = weather_icon.get(kode[idx_12], ("❓", "Tidak diketahui"))
            lokasi_tampil = kota.title() if kota else f"{lat:.2f}, {lon:.2f}"
            tanggal_str = tanggal.strftime("%d %B %Y")

            with col2:
                st.markdown(f"""
                <div style='border:2px solid {warna['border_default']}; border-radius:10px; padding:15px; background-color:{warna['cuaca_box']}; color:{warna['cuaca_teks']}; font-weight:bold; font-size:16px; line-height:1.6;'>
                    <h4 style="margin-bottom:5px;">📆 Cuaca untuk {tanggal_str} <span style="font-size:12px; font-weight:normal;">(waktu lokal)</span></h4>
                    <p><b>Lokasi:</b> {lokasi_tampil}</p>
                    <p><b>{ikon} {deskripsi}</b></p>
                    <p><b>🌡️ Suhu:</b> {suhu[idx_12]} °C</p>
                    <p><b>💧 Kelembapan:</b> {rh[idx_12]} %</p>
                    <p><b>💨 Angin:</b> {angin_speed[idx_12]} m/s ({angin_dir[idx_12]}°)</p>
                    <p><b>📉 Tekanan:</b> {tekanan[idx_12]} hPa</p>
                </div>
                """, unsafe_allow_html=True)

            # Cuaca ekstrem
            ekstrem = [w.replace("T", " ") for i, w in enumerate(waktu) if kode[i] >= 80]
            if ekstrem:
                daftar = "<br>".join(f"• {e}" for e in ekstrem)
                st.markdown(f"""
                    <div style='border: 2px solid {warna['ekstrem_teks']}; padding: 15px; border-radius: 10px; background-color: {warna['ekstrem_bg']}; color: {warna['ekstrem_teks']}; font-weight: bold; font-size: 16px; line-height: 1.6; margin-top: 10px;'>
                        ⚠️ <u>Cuaca ekstrem diperkirakan</u> (waktu lokal):<br>{daftar}
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.success("✅ Tidak ada cuaca ekstrem terdeteksi.")

            def intensitas_hujan(mm):
                if 0.1 <= mm <= 2.5:
                    return "Ringan"
                elif 2.6 <= mm <= 7.5:
                    return "Sedang"
                elif mm > 7.5:
                    return "Lebat"
                return ""

            hujan_info = [
                f"• {w[-5:]} — {h:.1f} mm ({intensitas_hujan(h)})"
                for w, h in zip(waktu, hujan)
                if h > 0
            ]

            if hujan_info:
                daftar_hujan = "<br>".join(hujan_info)
                st.markdown(f"""
                    <div style='border:2px solid #005f99; padding:15px; border-radius:10px; background-color:{warna['hujan_bg']}; color:{warna['hujan_teks']}; font-size:16px; font-weight:bold; line-height:1.6; margin-top:10px;'>
                        ☔ <u>Prakiraan Hujan</u> (waktu lokal):<br>{daftar_hujan}
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.info("🌤️ Tidak ada hujan yang diperkirakan.")
