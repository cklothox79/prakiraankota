import streamlit as st
import requests
import pandas as pd
from datetime import date
from streamlit_folium import st_folium
import folium
import plotly.graph_objects as go

st.set_page_config(page_title="CUACA PERJALANAN", layout="wide")
st.title("🕓 CUACA PERJALANAN")
st.markdown("**Editor: Ferri Kusuma (STMKG/M8TB_14.22.0003_2025)**")
st.write("Lihat prakiraan suhu, hujan, awan, kelembapan, dan angin setiap jam untuk lokasi dan tanggal yang kamu pilih.")

tanggal = st.date_input("📅 Pilih tanggal perjalanan:", value=date.today(), min_value=date.today())
kota = st.text_input("📝 Masukkan nama kota (opsional):")

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

st.markdown("### 🗺️ Klik lokasi di peta atau masukkan nama kota")
default_location = [-2.5, 117.0]
m = folium.Map(location=default_location, zoom_start=5)

if kota:
    lat, lon = get_coordinates(kota)
    if lat and lon:
        lokasi_sumber = "Kota"
        folium.Marker([lat, lon], tooltip=f"📍 {kota.title()}").add_to(m)
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
        st.success(f"📍 Lokasi dari peta: {lat:.4f}, {lon:.4f}")

    def get_weather(lat, lon, tanggal):
        tgl_str = tanggal.strftime("%Y-%m-%d")
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}"
            f"&hourly=temperature_2m,precipitation,cloudcover,weathercode,"
            f"relativehumidity_2m,windspeed_10m,winddirection_10m,pressure_msl,shortwave_radiation"
            f"&current_weather=true"
            f"&timezone=auto&start_date={tgl_str}&end_date={tgl_str}"
        )
        r = requests.get(url)
        return r.json() if r.status_code == 200 else None

    weather_icon = {
        0: ("☀️", "Cerah"), 1: ("🌤️", "Cerah Berawan"), 2: ("⛅", "Sebagian Berawan"),
        3: ("☁️", "Berawan"), 45: ("🌫️", "Berkabut"), 48: ("🌫️", "Kabut Tebal"),
        51: ("🌦️", "Gerimis Ringan"), 53: ("🌦️", "Gerimis"), 55: ("🌧️", "Gerimis Lebat"),
        61: ("🌦️", "Hujan Ringan"), 63: ("🌧️", "Hujan Sedang"), 65: ("🌧️", "Hujan Lebat"),
        80: ("🌧️", "Hujan Singkat"), 81: ("🌧️", "Hujan Singkat Sedang"), 82: ("🌧️", "Hujan Singkat Lebat"),
        95: ("⛈️", "Badai Petir"), 96: ("⛈️", "Petir + Es"), 99: ("⛈️", "Badai Parah")
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
            shortwave = d.get("shortwave_radiation", [0]*len(waktu))

            try:
                idx_12 = jam_labels.index("12:00")
            except:
                idx_12 = 0

            ikon, deskripsi = weather_icon.get(kode[idx_12], ("❓", "Tidak diketahui"))
            lokasi_tampil = kota.title() if kota else f"{lat:.2f}, {lon:.2f}"
            tanggal_str = tanggal.strftime("%d %B %Y")

            with col2:
                st.markdown(f"""
                <div style='border:2px solid #666; border-radius:10px; padding:15px; background-color:#eef2f7;'>
                    <h4>📆 Cuaca untuk {tanggal_str} <span style="font-size:12px;">(waktu lokal)</span></h4>
                    <p><b>Lokasi:</b> {lokasi_tampil}</p>
                    <p><b>{ikon} {deskripsi}</b></p>
                    <p><b>🌡️ Suhu:</b> {suhu[idx_12]} °C</p>
                    <p><b>💧 Kelembapan:</b> {rh[idx_12]} %</p>
                    <p><b>💨 Angin:</b> {angin_speed[idx_12]} m/s ({angin_dir[idx_12]}°)</p>
                    <p><b>📉 Tekanan:</b> {tekanan[idx_12]} hPa</p>
                    <p><b>🔆 Radiasi Matahari:</b> {shortwave[idx_12]:.1f} W/m²</p>
                </div>
                """, unsafe_allow_html=True)

            # Penyinaran Matahari
            st.subheader("🔆 Durasi & Intensitas Penyinaran Matahari")
            penyinaran_df = pd.DataFrame({"Waktu": jam_labels, "Radiasi (W/m²)": shortwave})
            sinar_positif = penyinaran_df[penyinaran_df["Radiasi (W/m²)"] > 0]
            if not sinar_positif.empty:
                jam_awal = sinar_positif.iloc[0]["Waktu"]
                jam_akhir = sinar_positif.iloc[-1]["Waktu"]
                durasi = len(sinar_positif)
                rata2_radiasi = sinar_positif["Radiasi (W/m²)"].mean()
                st.markdown(f"""
                ☀️ **Durasi Penyinaran Matahari:** {durasi} jam (dari jam {jam_awal} sampai {jam_akhir})  
                🔅 **Rata-rata Intensitas:** {rata2_radiasi:.1f} W/m²
                """)
                st.line_chart(penyinaran_df.set_index("Waktu"))
            else:
                st.info("🌙 Tidak ada penyinaran matahari terdeteksi pada hari ini.")
