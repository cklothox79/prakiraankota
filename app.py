import streamlit as st
import requests
import pandas as pd
from datetime import date, datetime
from streamlit_folium import st_folium
import folium
import plotly.graph_objects as go

# Konfigurasi dasar
st.set_page_config(page_title="CUACA PERJALANAN", layout="wide")
st.title("🕓 CUACA PERJALANAN")
st.markdown("**Editor: Ferri Kusuma (STMKG/M8TB_14.22.0003_2025)**")
st.write("Lihat prakiraan suhu, hujan, awan, kelembapan, angin, dan penyinaran untuk lokasi & tanggal pilihanmu.")

# Input tanggal & kota
tanggal = st.date_input("📅 Pilih tanggal perjalanan:", value=date.today(), min_value=date.today())
kota = st.text_input("📝 Masukkan nama kota (opsional):")

def get_coordinates(nama):
    r = requests.get(f"https://nominatim.openstreetmap.org/search?q={nama}&format=json&limit=1",
                     headers={"User-Agent":"cuaca-app"})
    if r.status_code==200 and r.json():
        d = r.json()[0]
        return float(d["lat"]), float(d["lon"])
    return None, None

# Map
lat = lon = None
st.markdown("### 🗺️ Pilih lokasi dengan kota atau klik pada peta:")
m = folium.Map(location=[-2.5,117], zoom_start=5)
if kota:
    coords=get_coordinates(kota)
    if coords[0]:
        lat,lon=coords
        folium.Marker([lat,lon], tooltip=kota.title()).add_to(m)
        m.location=[lat,lon]; m.zoom_start=9
m.add_child(folium.LatLngPopup())
col1,col2 = st.columns([2,1])
with col1:
    map_data = st_folium(m, height=400, width=700)
    if map_data and map_data["last_clicked"]:
        lat,lon = map_data["last_clicked"]["lat"],map_data["last_clicked"]["lng"]
        st.success(f"📍 Lokasi: {lat:.4f}, {lon:.4f}")

# Ambil data cuaca termasuk radiasi, penyinaran
def get_weather(lat, lon, tgl):
    t = tgl.strftime("%Y-%m-%d")
    url = (f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
           f"&hourly=temperature_2m,precipitation,cloudcover,weathercode,"
           f"relativehumidity_2m,windspeed_10m,winddirection_10m,pressure_msl,"
           f"shortwave_radiation,sunshine_duration"
           f"&current_weather=true&timezone=auto&start_date={t}&end_date={t}")
    return requests.get(url).json()

# Ikon & deskripsi
weather_icon={0:("☀️","Cerah"),1:("🌤️","Cerah Berawan"),2:("⛅","Sebagian Berawan"),
             3:("☁️","Berawan"),45:("🌫️","Berkabut"),48:("🌫️","Kabut Tebal"),
             51:("🌦️","Gerimis Ringan"),53:("🌦️","Gerimis"),55:("🌧️","Gerimis Lebat"),
             61:("🌦️","Hujan Ringan"),63:("🌧️","Hujan Sedang"),65:("🌧️","Hujan Lebat"),
             80:("🌧️","Hujan Singkat"),95:("⛈️","Badai Petir"),96:("⛈️","Petir + Es"),
             99:("⛈️","Badai Parah")}

if lat and lon:
    data = get_weather(lat, lon, tanggal)
    if "hourly" in data:
        d = data["hourly"]
        waktu = d["time"]; jam=[w[-5:] for w in waktu]
        suhu, hujan, awan = d["temperature_2m"], d["precipitation"], d["cloudcover"]
        kode, rh = d["weathercode"], d["relativehumidity_2m"]
        ws, wd = d["windspeed_10m"], d["winddirection_10m"]
        tekanan = d["pressure_msl"]
        rad, shine = d["shortwave_radiation"], d["sunshine_duration"]

        # Info wind changes
        wind_msgs=[]; prev_dir=wd[0]; start=jam[0]
        for i,dirc in enumerate(wd[1:],1):
            if dirc!=prev_dir:
                wind_msgs.append(f"🔄 Jam {start}–{jam[i]} angin dari {prev_dir:.0f}° berubah ke {dirc:.0f}°")
                start=jam[i]
                prev_dir=dirc
        wind_msgs.append(f"💨 Dari jam {start} angin bertiup dari {prev_dir:.0f}°")
        
        # Tampilkan input info
        lokasi_txt = kota.title() if kota else f"{lat:.2f},{lon:.2f}"
        tanggal_str = tanggal.strftime("%d %B %Y")
        with col2:
            st.markdown(f"**🌤️ Cuaca untuk {tanggal_str} (waktu lokal)** \nLokasi: {lokasi_txt}")
            # Info wind
            for m in wind_msgs: st.markdown(m)
            # Penyinaran
            total_shine = sum(shine)/3600  # detik → jam
            st.markdown(f"☀️ Durasi penyinaran: {total_shine:.2f} jam\n🔆 Radiasi rata-rata: {sum(rad)/len(rad):.1f} W/m²")
        
        # Grafik utama dengan RH dan kode cuaca
        st.subheader("📈 Grafik Unsur Cuaca")
        st.caption(f"{tanggal_str} — {lokasi_txt}")
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=jam,y=suhu,name="Suhu °C", line=dict(color="red")))
        fig.add_trace(go.Scatter(x=jam,y=rh,name="RH %", line=dict(color="green"), yaxis="y3"))
        fig.add_trace(go.Bar(x=jam,y=hujan,name="Hujan mm", yaxis="y2", marker_color="darkblue", opacity=0.6))
        fig.add_trace(go.Bar(x=jam,y=awan,name="Awan %", yaxis="y2", marker_color="gray", opacity=0.4))
        fig.add_trace(go.Scatter(x=jam, y=[max(suhu)+2]*len(jam), text=[str(k) for k in kode],
                                 mode="text", textposition="top center", name="Kode Cuaca", showlegend=False))
        fig.update_layout(xaxis=dict(title="Jam"),
                          yaxis=dict(title="Suhu (°C)"),
                          yaxis2=dict(title="Hujan / Awan", overlaying="y", side="right"),
                          yaxis3=dict(title="RH (%)", overlaying="y", side="left", position=0.05, showgrid=False),
                          height=550)
        st.plotly_chart(fig, use_container_width=True)

        # Grafik angin
        st.subheader("🧭 Arah & Kecepatan Angin")
        st.caption(f"{tanggal_str} — {lokasi_txt}")
        fig2=go.Figure()
        fig2.add_trace(go.Barpolar(r=ws, theta=wd, width=[10]*len(ws), marker_color="royalblue", opacity=0.7))
        fig2.update_layout(polar=dict(angularaxis=dict(direction="clockwise",rotation=90),
                                      radialaxis=dict(title="m/s")), height=450)
        st.plotly_chart(fig2, use_container_width=True)

        # Tabel data
        df = pd.DataFrame({"Waktu":waktu,"Suhu":suhu,"Hujan":hujan,"Awan":awan,"RH":rh,
                           "Angin(m/s)":ws,"Arah(°)":wd,"Radiasi(W/m²)":rad,
                           "Sinar(s)":shine,"Tekanan(hPa)":tekanan,"Kode":kode})
        st.subheader("📊 Tabel Data Cuaca")
        st.caption(f"{tanggal_str} — {lokasi_txt}")
        st.dataframe(df, use_container_width=True)
        st.download_button("📥 Unduh CSV", data=df.to_csv(index=False), mime="text/csv")

    else:
        st.error("❌ Data tidak tersedia.")
