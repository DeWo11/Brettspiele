import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# --- GOOGLE SHEETS VERBINDUNG ---
# Trage HIER deine Google-Tabellen-URL ein
GOOGLE_SHEET_URL = "HIER_DEINE_GOOGLE_TABELLEN_URL_EINFÜGEN"

# Verbindung zu Google Sheets herstellen
conn = st.connection("gsheets", type=GSheetsConnection)

# --- WEB-OBERFLÄCHE ---
st.title("🎲 Meine Brettspiel-Datenbank (Cloud)")
st.write("Deine Daten sind sicher in Google Sheets gespeichert!")

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
        try:
            # 1. Wir bereiten die neuen Daten als einfache Liste vor
            # (Reihenfolge: titel, spieler, dauer, kategorien, notiz)
            neue_zeile = [[titel, spieler, int(dauer), kategorien, notiz]]
            
            # 2. Wir erstellen ein winziges Datenblatt nur für diese eine Zeile
            neues_spiel_df = pd.DataFrame(
                neue_zeile, 
                columns=["titel", "spieler", "dauer", "kategorien", "notiz"]
            )

            # 3. Wir lesen die Tabelle einmal kurz aus, um zu sehen, ob schon was drin steht
            try:
                aktuelle_daten = conn.read(spreadsheet=GOOGLE_SHEET_URL, worksheet="spiele")
                start_zeile = len(aktuelle_daten) + 2 if aktuelle_daten is not None else 2
            except Exception:
                start_zeile = 2

            # 4. Wir hängen die Zeile gezielt unten an, statt alles zu überschreiben
            conn.update(
                spreadsheet=GOOGLE_SHEET_URL,
                worksheet="spiele",
                data=neues_spiel_df,
                range=f"A{start_zeile}" # Setzt es genau in die nächste freie Zeile
            )

            st.success(f"🎲 '{titel}' wurde erfolgreich in deiner Google-Tabelle gespeichert!")
            st.cache_data.clear()

        except Exception as e:
            # Sicherheitsnetz für die hartnäckige Response-200-Meldung
            if "200" in str(e):
                st.success(f"🎲 '{titel}' wurde erfolgreich in deiner Google-Tabelle gespeichert!")
                st.cache_data.clear()
            else:
                st.error(f"Fehler beim Speichern: {e}")

# --- ANZEIGE & FILTER ---
st.header("📚 Meine Sammlung")

try:
    # Daten live aus dem Google Sheet laden (Tabellenblatt "spiele")
    data = conn.read(spreadsheet=GOOGLE_SHEET_URL, worksheet="spiele")

    # Falls Daten da sind und die Tabelle nicht leer ist
    if data is None or data.empty or "titel" not in data.columns:
        st.info(
            "Noch keine Spiele eingetragen oder Spaltenüberschriften fehlen."
        )
    else:
        # Filter-Eingabe in der linken Seitenleiste
        filter_kat = st.sidebar.text_input("🔍 Nach Kategorie filtern")

        # Wir gehen Zeile für Zeile durch die Google-Tabelle
        for index, row in data.iterrows():
            s_titel = str(row["titel"])
            s_spieler = str(row["spieler"])
            s_dauer = str(row["dauer"])
            s_kat = str(row["kategorien"]) if pd.notna(row["kategorien"]) else ""
            s_notiz = str(row["notiz"]) if pd.notna(row["notiz"]) else ""

            # Filter anwenden (Groß-/Kleinschreibung ignorieren)
            if filter_kat.lower() in s_kat.lower():
                with st.expander(
                    f"🔴 {s_titel} ({s_spieler} Spieler | {s_dauer} Min)"
                ):
                    st.write(f"**Kategorien:** {s_kat}")
                    st.write(f"**Meine Notiz:** {s_notiz}")
except Exception as e:
    st.info(
        "Füge dein erstes Spiel hinzu, um die Tabelle zu aktivieren! (Oder überprüfe deine URL)"
    )