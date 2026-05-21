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
            # 1. Wir versuchen, die bestehenden Daten zu laden
            try:
                aktuelle_daten = conn.read(spreadsheet=GOOGLE_SHEET_URL, worksheet="spiele")
                
                # Falls die Tabelle existiert, aber Pandas sie falsch eingelesen hat (z.B. als None)
                if aktuelle_daten is None:
                    aktuelle_daten = pd.DataFrame(columns=["titel", "spieler", "dauer", "kategorien", "notiz"])
            except Exception:
                # Falls das Laden fehlschlägt (z.B. weil das Sheet komplett leer ist)
                aktuelle_daten = pd.DataFrame(columns=["titel", "spieler", "dauer", "kategorien", "notiz"])

            # 2. Das neue Spiel als sauberes Datenblatt (DataFrame) anlegen
            neues_spiel = pd.DataFrame([{
                "titel": titel,
                "spieler": spieler,
                "dauer": int(dauer),
                "kategorien": kategorien,
                "notiz": notiz
            }])

            # 3. Sicherstellen, dass die Spaltennamen exakt übereinstimmen
            neues_spiel = neues_spiel.reindex(columns=["titel", "spieler", "dauer", "kategorien", "notiz"])

            # 4. Das neue Spiel unten an die alten Daten anheften
            if aktuelle_daten.empty:
                aktualisierte_daten = neues_spiel
            else:
                # Wir bereinigen eventuelle leere Zeilen/Spalten aus dem Google-Sheet-Import
                aktuelle_daten = aktuelle_daten.dropna(how='all')
                aktualisierte_daten = pd.concat([aktuelle_daten, neues_spiel], ignore_index=True)

            # 5. Das gesamte Paket komplett zu Google hochladen
            conn.update(
                spreadsheet=GOOGLE_SHEET_URL,
                worksheet="spiele",
                data=aktualisierte_daten
            )

            st.success(f"🎲 '{titel}' wurde erfolgreich gespeichert!")
            st.cache_data.clear()

        except Exception as e:
            # Der bewährte Filter für die harmlose Response-200-Erfolgsmeldung
            if "200" in str(e):
                st.success(f"🎲 '{titel}' wurde erfolgreich gespeichert!")
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