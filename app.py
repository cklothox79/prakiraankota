import streamlit as st
import requests
import pandas as pd
from datetime import date, datetime
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
            f"relativehumidity_2m,windspeed_10m,winddirection_10m,pressure_msl"
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
                </div>
                """, unsafe_allow_html=True)

            ekstrem = [w.replace("T", " ") for i, w in enumerate(waktu) if kode[i] >= 80]
            if ekstrem:
                daftar = "<br>".join(f"• {e}" for e in ekstrem)
                st.markdown(f"""
                    <div style='border:2px solid red; padding:15px; border-radius:10px; background-color:#ffe6e6; margin-top:10px;'>
                        <b>🚨 Cuaca ekstrem diperkirakan (waktu lokal):</b><br>{daftar}
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.success("✅ Tidak ada cuaca ekstrem terdeteksi.")

            # GRAFIK SUHU-HUJAN-AWAN
            st.subheader("📈 Grafik Suhu, Hujan & Awan")
            st.caption(f"Prakiraan untuk {tanggal_str} (waktu lokal) — Lokasi: {lokasi_tampil}")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=jam_labels, y=suhu, name="Suhu (°C)", line=dict(color="red")))
            fig.add_trace(go.Bar(x=jam_labels, y=hujan, name="Hujan (mm)", yaxis="y2", marker_color="darkblue", opacity=0.6))
            fig.add_trace(go.Bar(x=jam_labels, y=awan, name="Awan (%)", yaxis="y2", marker_color="gray", opacity=0.4))
            fig.update_layout(
                xaxis=dict(title="Jam"),
                yaxis=dict(title="Suhu (°C)"),
                yaxis2=dict(title="Hujan / Awan", overlaying="y", side="right"),
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)

            # ARAH ANGIN
            st.subheader("🧭 Arah & Kecepatan Angin")
            st.caption(f"Prakiraan untuk {tanggal_str} (waktu lokal) — Lokasi: {lokasi_tampil}")
            fig_angin = go.Figure()
            fig_angin.add_trace(go.Barpolar(
                r=angin_speed,
                theta=angin_dir,
                width=[10]*len(angin_speed),
                marker_color="royalblue",
                opacity=0.7
            ))
            fig_angin.update_layout(
                polar=dict(angularaxis=dict(direction="clockwise", rotation=90), radialaxis=dict(title="m/s")),
                height=450
            )
            st.plotly_chart(fig_angin, use_container_width=True)

            # TABEL DATA
            df = pd.DataFrame({
                "Waktu": waktu,
                "Suhu (°C)": suhu,
                "Hujan (mm)": hujan,
                "Awan (%)": awan,
                "RH (%)": rh,
                "Kecepatan Angin (m/s)": angin_speed,
                "Arah Angin (°)": angin_dir,
                "Tekanan (hPa)": tekanan,
                "Kode Cuaca": kode
            })
            st.markdown("### 📊 Tabel Data Cuaca")
            st.caption(f"Prakiraan untuk {tanggal_str} (waktu lokal) — Lokasi: {lokasi_tampil}")
            st.dataframe(df, use_container_width=True)
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Unduh Data (CSV)", data=csv, file_name="cuaca_per_jam.csv", mime="text/csv")

        else:
            st.error("❌ Data cuaca tidak tersedia.")
