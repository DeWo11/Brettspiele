import gspread
import streamlit as st
from itertools import chain
from streamlit_gsheets import GSheetsConnection

# --- GOOGLE SHEETS VERBINDUNG ---
# Trage HIER die kopierte URL deiner Google-Tabelle ein
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1_T4tN3BLPD4rt6F5ccjS0IlbcDkZ19lmobDdajIIn-U/edit?gid=0#gid=0"

# Verbindung für das Lesen der Daten (Streamlit Built-in)
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
            # KORREKTUR: Wir nutzen .oauth() oder die direkte Client-Steuerung für öffentliche Sheets
            # Da das Sheet öffentlich im Web ist, nutzen wir gspread über den direkten Schlüssel
            gc = gspread.api_client_v4() if hasattr(gspread, "api_client_v4") else gspread.Client(auth=None)
            
            # Wir öffnen die Tabelle ganz normal über ihre URL
            spreadsheet = gc.open_by_url(GOOGLE_SHEET_URL)
            worksheet = spreadsheet.worksheet("spiele")

            # Neue Zeile als Liste vorbereiten und ans Ende der Tabelle anhängen
            neue_zeile = [titel, spieler, int(dauer), kategorien, notiz]
            worksheet.append_row(neue_zeile)

            st.success(f"'{titel}' wurde erfolgreich in der Cloud gespeichert!")
            # Cache leeren, damit die Anzeige unten sofort aktualisiert wird
            st.cache_data.clear()
        except Exception as e:
            st.error(f"Fehler beim Speichern. Details: {e}")

# --- ANZEIGE & FILTER ---
st.header("📚 Meine Sammlung")

try:
    # Daten live aus dem Google Sheet laden (Tabellenblatt "spiele")
    data = conn.read(spreadsheet=GOOGLE_SHEET_URL, worksheet="spiele")

    if data.empty:
        st.info("Noch keine Spiele eingetragen.")
    else:
        filter_kat = st.sidebar.text_input("🔍 Nach Kategorie filtern")

        # Wir gehen Zeile für Zeile durch die geladenen Daten
        for index, row in data.iterrows():
            s_titel = row["titel"]
            s_spieler = row["spieler"]
            s_dauer = row["dauer"]
            s_kat = str(row["kategorien"]) if not None else ""
            s_notiz = row["notiz"]

            # Filter anwenden
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