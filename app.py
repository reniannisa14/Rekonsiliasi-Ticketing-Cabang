app.py
import streamlit as st
import pandas as pd

st.title("📊 Rekonsiliasi Ticketing")

# Upload file
ticket_file = st.file_uploader("Upload Ticket Detail", type=["xlsx"])
settlement_file = st.file_uploader("Upload Settlement Report", type=["csv"])

if ticket_file and settlement_file:

    ticket_df = pd.read_excel(ticket_file)
    settlement_df = pd.read_csv(settlement_file)

    # ===== FILTER PAID =====
    ticket_df = ticket_df[ticket_df["status"] == "PAID"]

    # ===== CONVERT TIMEZONE =====
    def convert_waktu(teks):
        if "WIT" in teks:
            waktu = pd.to_datetime(teks.replace(" WIT", ""))
            return waktu - pd.Timedelta(hours=2)
        elif "WITA" in teks:
            waktu = pd.to_datetime(teks.replace(" WITA", ""))
            return waktu - pd.Timedelta(hours=1)
        else:
            waktu = pd.to_datetime(teks.replace(" WIB", ""))
            return waktu

    ticket_df["created_wib"] = ticket_df["created_at"].apply(convert_waktu)

    # ===== RENAME KOLOM =====
    ticket_df = ticket_df.rename(columns={
        "Order ID": "order_id",
        "Tarif": "amount"
    })

    settlement_df = settlement_df.rename(columns={
        "Order ID": "order_id",
        "Amount": "amount_settlement"
    })

    # ===== MERGE =====
    merged = pd.merge(
        ticket_df,
        settlement_df,
        on="order_id",
        how="outer",
        indicator=True
    )

    # ===== STATUS =====
    def cek_status(row):
        if row["_merge"] == "left_only":
            return "Tidak ada di Settlement"
        elif row["_merge"] == "right_only":
            return "Tidak ada di Ticket"
        else:
            if row["amount"] == row["amount_settlement"]:
                return "Match"
            else:
                return "Selisih"

    merged["status"] = merged.apply(cek_status, axis=1)
    merged["selisih"] = merged["amount"] - merged["amount_settlement"]

    st.dataframe(merged)

    # Download
    csv = merged.to_csv(index=False).encode("utf-8")
    st.download_button("Download Hasil", csv, "hasil.csv")
