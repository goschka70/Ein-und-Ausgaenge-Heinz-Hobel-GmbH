import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Ein- und Ausgänge Heinz Hobel GmbH", layout="wide")

st.title("🚗 Ein- und Ausgänge Heinz Hobel GmbH")

# Datei-Upload
uploaded_files = st.file_uploader("📁 Lade zwei CSV-Dateien hoch", type="csv", accept_multiple_files=True)

if uploaded_files and len(uploaded_files) == 2:
    # Beide Dateien einlesen und zusammenführen
    df1 = pd.read_csv(uploaded_files[0], sep=";", encoding="utf-8")
    df2 = pd.read_csv(uploaded_files[1], sep=";", encoding="utf-8")
    df = pd.concat([df1, df2], ignore_index=True)

    # Datumsspalten konvertieren
    df["Fahrzeugeingang"] = pd.to_datetime(df["Fahrzeugeingang"], errors="coerce")
    df["Fahrzeugausgang am"] = pd.to_datetime(df["Fahrzeugausgang am"], errors="coerce")

    # Monatsspalten erstellen
    df["Eingang_Monat"] = df["Fahrzeugeingang"].dt.to_period("M")
    df["Ausgang_Monat"] = df["Fahrzeugausgang am"].dt.to_period("M")

    # Filter
    auftraggeber = st.selectbox("🔍 Auftraggeber auswählen", options=df["Auftraggeber"].dropna().unique())
    platz = st.selectbox("📍 Platz auswählen", options=df["Platz"].dropna().unique())

    # Eingänge nach Monat und Platz
    eingang_df = df[(df["Auftraggeber"] == auftraggeber) & (df["Platz"] == platz)]
    eingang_monat = eingang_df.groupby("Eingang_Monat").size().reset_index(name="Eingänge")
    fig_eingang = px.bar(eingang_monat, x="Eingang_Monat", y="Eingänge", title="📈 Monatliche Eingänge", labels={"Eingang_Monat": "Monat"})
    st.plotly_chart(fig_eingang, use_container_width=True)

    # Ausgänge nach Monat und Platz
    ausgang_df = df[(df["Auftraggeber"] == auftraggeber) & (df["Platz"] == platz)]
    ausgang_monat = ausgang_df.groupby("Ausgang_Monat").size().reset_index(name="Ausgänge")
    fig_ausgang = px.bar(ausgang_monat, x="Ausgang_Monat", y="Ausgänge", title="📉 Monatliche Ausgänge", labels={"Ausgang_Monat": "Monat"})
    st.plotly_chart(fig_ausgang, use_container_width=True)

    # Fahrzeugbestand pro Monat nach Auftraggeber
    df_bestand = df[df["Auftraggeber"] == auftraggeber].copy()
    df_bestand["Monat"] = pd.date_range(start=df_bestand["Fahrzeugeingang"].min(), end=df_bestand["Fahrzeugausgang am"].max(), freq="MS").to_period("M")
    bestand_monate = []
    for monat in df_bestand["Monat"].unique():
        count = df_bestand[(df_bestand["Fahrzeugeingang"].dt.to_period("M") <= monat) & ((df_bestand["Fahrzeugausgang am"].dt.to_period("M") > monat) | (df_bestand["Fahrzeugausgang am"].isna()))].shape[0]
        bestand_monate.append({"Monat": monat, "Bestand": count})
    df_bestand_monat = pd.DataFrame(bestand_monate)
    fig_bestand = px.line(df_bestand_monat, x="Monat", y="Bestand", title="📊 Fahrzeugbestand pro Monat", markers=True)
    st.plotly_chart(fig_bestand, use_container_width=True)
else:
    st.info("Bitte lade genau zwei CSV-Dateien hoch.")
