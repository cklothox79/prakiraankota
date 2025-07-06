# ... [semua kode di atas TETAP sama, hingga sebelum bagian grafik] ...

            # ========== GRAFIK UNSUR CUACA ==========
            st.subheader("📈 Grafik Unsur Cuaca")
            st.caption(f"Prakiraan untuk {tanggal_str} (waktu lokal) — Lokasi: {lokasi_tampil}")
            fig = go.Figure()

            # Suhu (garis)
            fig.add_trace(go.Scatter(
                x=jam_labels, y=suhu,
                name="Suhu (°C)",
                line=dict(color="red"),
                mode="lines+markers"
            ))

            # RH (garis hijau)
            fig.add_trace(go.Scatter(
                x=jam_labels, y=rh,
                name="RH (%)",
                line=dict(color="green"),
                yaxis="y3"
            ))

            # Hujan (bar biru)
            fig.add_trace(go.Bar(
                x=jam_labels, y=hujan,
                name="Hujan (mm)",
                yaxis="y2",
                marker_color="darkblue",
                opacity=0.6
            ))

            # Awan (bar abu)
            fig.add_trace(go.Bar(
                x=jam_labels, y=awan,
                name="Awan (%)",
                yaxis="y2",
                marker_color="gray",
                opacity=0.4
            ))

            # Kode cuaca sebagai teks
            label_kode = [str(k) for k in kode]
            fig.add_trace(go.Scatter(
                x=jam_labels,
                y=[max(suhu)+1]*len(jam_labels),
                text=label_kode,
                mode="text",
                textposition="top center",
                name="Kode Cuaca",
                showlegend=False
            ))

            fig.update_layout(
                xaxis=dict(title="Jam"),
                yaxis=dict(title="Suhu (°C)"),
                yaxis2=dict(
                    title="Hujan / Awan",
                    overlaying="y",
                    side="right"
                ),
                yaxis3=dict(
                    title="RH (%)",
                    overlaying="y",
                    side="left",
                    position=0.05,
                    showgrid=False
                ),
                height=550
            )
            st.plotly_chart(fig, use_container_width=True)

# ... [seluruh bagian grafik angin, tabel, cuaca ekstrem TETAP seperti sebelumnya] ...
