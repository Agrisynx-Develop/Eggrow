import streamlit as st
import pandas as pd
import numpy as np
import os
import io

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4

st.set_page_config(page_title="Sistem Data Science Ayam Layer", layout="wide")
st.title("🐔 Sistem Data Science Ayam Layer")

os.makedirs("data", exist_ok=True)
save_path = "data/hasil_produktivitas.csv"

menu = st.sidebar.selectbox(
    "Pilih Menu",
    ("Input CSV", "Produktivitas", "Visualisasi Data", "Summary")
)

# =========================================================
# MENU 1 : INPUT CSV
# =========================================================
if menu == "Input CSV":

    st.header("📂 Upload Dataset")

    uploaded_file = st.file_uploader("Upload file CSV", type=["csv"])

    if uploaded_file is None:
        st.info("Silakan upload dataset terlebih dahulu.")
    else:
        df = pd.read_csv(uploaded_file)

        # Normalisasi nama kolom
        df.columns = df.columns.str.strip().str.lower()

        # =============================
        # CLEANING DATA NUMERIK
        # =============================
        numeric_cols = [
            "jumlah ternak",
            "jumlah telur",
            "berat telur rata-rata",
            "konsumsi pakan",
            "harga pakan",
            "harga telur"
        ]

        for col in numeric_cols:
            if col in df.columns:
                df[col] = (
                    df[col]
                    .astype(str)
                    .str.replace("Rp", "", regex=False)
                    .str.replace(",", "", regex=False)
                    .str.strip()
                )
                df[col] = pd.to_numeric(df[col], errors="coerce")

        df = df.dropna(subset=numeric_cols)

        st.subheader("Preview Dataset")
        st.dataframe(df)

        required_cols = [
            "tanggal",
            "jumlah ternak",
            "jumlah telur",
            "berat telur rata-rata",
            "konsumsi pakan",
            "harga pakan",
            "harga telur"
        ]

        missing = [c for c in required_cols if c not in df.columns]

        if missing:
            st.error(f"Kolom berikut tidak ditemukan: {missing}")
            st.stop()

        selected_date = st.selectbox(
            "Pilih Tanggal",
            df["tanggal"].astype(str).unique()
        )

        row = df[df["tanggal"].astype(str) == selected_date].iloc[0]

        jumlah_ternak = float(row["jumlah ternak"])
        jumlah_telur = float(row["jumlah telur"])
        berat_telur = float(row["berat telur rata-rata"])
        konsumsi_pakan = float(row["konsumsi pakan"])
        harga_pakan = float(row["harga pakan"])
        harga_telur = float(row["harga telur"])

        if jumlah_telur > 0 and berat_telur > 0:

            # ========================
            # PERHITUNGAN
            # ========================
            fcr = konsumsi_pakan / (jumlah_telur * berat_telur)
            hda = (jumlah_telur / jumlah_ternak) * 100
            feed_cost = (konsumsi_pakan * harga_pakan) / (jumlah_telur * berat_telur)

            revenue = jumlah_telur * harga_telur
            total_feed_cost = konsumsi_pakan * harga_pakan
            profit = revenue - total_feed_cost

            st.subheader("📊 Hasil Perhitungan")

            col1, col2, col3 = st.columns(3)
            col1.metric("FCR (kg)", round(fcr, 4))
            col2.metric("HDA (%)", round(hda, 2))
            col3.metric("Feed Cost", round(feed_cost, 4))

            st.metric("Profit / Loss", f"Rp {profit:,.0f}")

            # ========================
            # SIMPAN DATA (VERSI AMAN)
            # ========================
            if st.button("💾 Simpan Data"):

                hasil_df = pd.DataFrame({
                    "tanggal": [selected_date],
                    "FCR": [fcr],
                    "HDA": [hda],
                    "Feed Cost": [feed_cost],
                    "Profit": [profit]
                })

                if os.path.exists(save_path):
                    try:
                        old_df = pd.read_csv(save_path)
                        new_df = pd.concat([old_df, hasil_df], ignore_index=True)
                    except:
                        new_df = hasil_df
                else:
                    new_df = hasil_df

                new_df.to_csv(save_path, index=False)

                st.success("Data berhasil disimpan!")

        else:
            st.warning("Jumlah telur atau berat telur tidak boleh 0.")

# =========================================================
# MENU 2 : PRODUKTIVITAS
# =========================================================
elif menu == "Produktivitas":

    st.header("📈 Data Produktivitas")

    if os.path.exists(save_path):

        try:
            hasil_df = pd.read_csv(save_path)
            st.dataframe(hasil_df)
        except:
            st.error("File hasil_produktivitas.csv rusak. Silakan hapus dan buat ulang.")
            st.stop()

        if st.button("🗑 Hapus Semua Data"):
            os.remove(save_path)
            st.success("Semua data berhasil dihapus.")

    else:
        st.warning("Belum ada data yang disimpan.")

# =========================================================
# MENU 3 : VISUALISASI DATA
# =========================================================
elif menu == "Visualisasi Data":

    st.header("📊 Visualisasi Scatter Plot")

    if os.path.exists(save_path):

        try:
            hasil_df = pd.read_csv(save_path)
        except:
            st.error("File hasil_produktivitas.csv rusak.")
            st.stop()

        st.subheader("Scatter Plot FCR")
        st.scatter_chart(hasil_df.set_index("tanggal")["FCR"])

        st.subheader("Scatter Plot HDA")
        st.scatter_chart(hasil_df.set_index("tanggal")["HDA"])

        st.subheader("Scatter Plot Feed Cost")
        st.scatter_chart(hasil_df.set_index("tanggal")["Feed Cost"])

    else:
        st.warning("Belum ada data untuk divisualisasikan.")

# =========================================================
# MENU 4 : SUMMARY
# =========================================================
elif menu == "Summary":

    st.header("📋 Summary Keuntungan & Kerugian")

    if os.path.exists(save_path):

        try:
            hasil_df = pd.read_csv(save_path)
        except:
            st.error("File hasil_produktivitas.csv rusak.")
            st.stop()

        total_profit = hasil_df["Profit"].sum()
        avg_fcr = hasil_df["FCR"].mean()
        avg_hda = hasil_df["HDA"].mean()

        st.metric("Total Profit", f"Rp {total_profit:,.0f}")
        st.metric("Rata-rata FCR", round(avg_fcr, 4))
        st.metric("Rata-rata HDA (%)", round(avg_hda, 2))

        if total_profit > 0:
            status = "KEUNTUNGAN"
            st.success("Usaha mengalami KEUNTUNGAN.")
        elif total_profit < 0:
            status = "KERUGIAN"
            st.error("Usaha mengalami KERUGIAN.")
        else:
            status = "IMPAS"
            st.info("Usaha berada pada titik impas.")

        # ========================
        # GENERATE PDF
        # ========================
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()

        elements.append(Paragraph("LAPORAN SUMMARY AYAM LAYER", styles["Title"]))
        elements.append(Spacer(1, 0.3 * inch))
        elements.append(Paragraph(f"Total Profit: Rp {total_profit:,.0f}", styles["Normal"]))
        elements.append(Paragraph(f"Rata-rata FCR: {round(avg_fcr,4)}", styles["Normal"]))
        elements.append(Paragraph(f"Rata-rata HDA: {round(avg_hda,2)}%", styles["Normal"]))
        elements.append(Paragraph(f"Status Usaha: {status}", styles["Normal"]))

        doc.build(elements)

        st.download_button(
            label="📥 Download as PDF",
            data=buffer.getvalue(),
            file_name="summary_ayam_layer.pdf",
            mime="application/pdf"
        )

    else:
        st.warning("Belum ada data untuk dianalisis.")