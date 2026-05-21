import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- SEITEN-EINSTELLUNGEN ---
st.set_page_config(
    page_title="Meine Brettspiel-Datenbank",
    page_icon="🎲",
    layout="centered"
)

st.title("🎲 Meine Brettspiel-Datenbank")
st.write("Verwalte deine Brettspiel-Sammlung ganz einfach über diese Web-Oberfläche. Alle Daten werden live in Google Sheets gespeichert.")

# --- GOOGLE SHEETS VERBINDUNG INITIALISIEREN ---
# Streamlit holt sich alle Zugangsdaten und die URL automatisch aus deinen Secrets!
conn = st.connection("gsheets", type=GSheetsConnection)


# --- FORMULAR: NEUES SPIEL HINZUFÜGEN ---
st.header("➕ Neues Spiel hinzufügen")

with st.form("spiel_form", clear_on_submit=True):
    titel = st.text_input("Name des Spiels")
    spieler = st.text_input("Spieleranzahl", "2-4")
    dauer = st.number_input("Spieldauer (in Minuten)", min_value=5, value=60)
    kategorien = st.text_input("Kategorien (mit Komma trennen)")
    notiz = st.text_area("Meine Bemerkungen")

    submit = st.form_submit_button("In Google Sheets speichern")

    if submit and titel:
        # 1. Bestehende Daten laden
        try:
            # Wir geben die URL hier wieder explizit an, damit er die Tabelle findet
            aktuelle_daten = conn.read(spreadsheet="https://docs.google.com/spreadsheets/d/1_T4tN3BLPD4rt6F5ccjS0IlbcDkZ19lmobDdajIIn-U/edit?gid=0#gid=0", worksheet="spiele")
            if aktuelle_daten is None:
                aktuelle_daten = pd.DataFrame(columns=["titel", "spieler", "dauer", "kategorien", "notiz"])
        except Exception:
            aktuelle_daten = pd.DataFrame(columns=["titel", "spieler", "dauer", "kategorien", "notiz"])

        # 2. Das neue Spiel anlegen
        neues_spiel = pd.DataFrame([{
            "titel": titel,
            "spieler": spieler,
            "dauer": int(dauer),
            "kategorien": kategorien,
            "notiz": notiz
        }])
        neues_spiel = neues_spiel.reindex(columns=["titel", "spieler", "dauer", "kategorien", "notiz"])

        # 3. Daten zusammenführen
        if aktuelle_daten.empty:
            aktualisierte_daten = neues_spiel
        else:
            aktuelle_daten = aktuelle_daten.dropna(how='all')
            aktualisierte_daten = pd.concat([aktuelle_daten, neues_spiel], ignore_index=True)

        # 4. Daten mit expliziter URL-Angabe hochladen
        conn.update(
            spreadsheet="https://docs.google.com/spreadsheets/d/1_T4tN3BLPD4rt6F5ccjS0IlbcDkZ19lmobDdajIIn-U/edit?gid=0#gid=0", 
            worksheet="spiele", 
            data=aktualisierte_daten
        )
        
        # 5. Erfolg anzeigen und Cache leeren
        st.success(f"🎲 '{titel}' wurde erfolgreich in deiner Google-Tabelle gespeichert!")
        st.cache_data.clear()


# --- ANZEIGE: MEINE SAMMLUNG ---
st.header("📚 Meine Sammlung")

try:
    # Daten live aus dem Google Sheet laden
    daten = conn.read(worksheet="spiele")
    
    if daten is not None and not daten.empty:
        # Komplett leere Zeilen für die Anzeige ignorieren
        anzeige_daten = daten.dropna(how='all')
        
        # Die Tabelle hübsch in der App anzeigen
        st.dataframe(
            anzeige_daten, 
            use_container_width=True,
            hide_index=True
        )
        
        # Kleine Statistik am Rande
        anzahl_spiele = len(anzeige_daten)
        st.info(f"Insgesamt befinden sich aktuell **{anzahl_spiele} Spiele** in deiner Sammlung.")
    else:
        st.warning("Deine Sammlung ist aktuell noch leer. Trage oben dein erstes Spiel ein!")

except Exception:
    st.warning("Deine Sammlung ist aktuell noch leer. Trage oben dein erstes Spiel ein!")