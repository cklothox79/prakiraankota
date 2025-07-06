# [potongan kode awal tidak berubah]
# Tambahkan 'shortwave_radiation,sunshine_duration' ke dalam URL API:
def get_weather(lat, lon, tanggal):
    tgl_str = tanggal.strftime("%Y-%m-%d")
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&hourly=temperature_2m,precipitation,cloudcover,weathercode,"
        f"relativehumidity_2m,windspeed_10m,winddirection_10m,pressure_msl,"
        f"shortwave_radiation,sunshine_duration"
        f"&current_weather=true"
        f"&timezone=auto&start_date={tgl_str}&end_date={tgl_str}"
    )
    r = requests.get(url)
    return r.json() if r.status_code == 200 else None

# [lanjut di bagian setelah parsing data]
shortwave = d["shortwave_radiation"]
sunshine = d["sunshine_duration"]

# Tambahan: rata-rata radiasi & total durasi sinar matahari (jam)
avg_radiasi = sum(shortwave) / len(shortwave)
durasi_sinar_jam = sum(sunshine) / 3600  # detik → jam

# Kotak keterangan cuaca (di dalam col2)
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
        <hr style="margin:10px 0;">
        <p><b>☀️ Durasi Penyinaran:</b> {durasi_sinar_jam:.2f} jam</p>
        <p><b>🔆 Radiasi Matahari:</b> {avg_radiasi:.1f} W/m² (rata-rata)</p>
    </div>
    """, unsafe_allow_html=True)

# [lanjutan kode lainnya seperti biasa: ekstrem, hujan, grafik, tabel...]
# Jangan lupa menambahkan dua kolom ini ke dalam tabel dataframe juga:
df = pd.DataFrame({
    "Waktu": waktu,
    "Suhu (°C)": suhu,
    "Hujan (mm)": hujan,
    "Awan (%)": awan,
    "RH (%)": rh,
    "Kecepatan Angin (m/s)": angin_speed,
    "Arah Angin (°)": angin_dir,
    "Tekanan (hPa)": tekanan,
    "Radiasi (W/m²)": shortwave,
    "Penyinaran (s)": sunshine,
    "Kode Cuaca": kode
})
