import sqlite3
import streamlit as st

# --- DATENBANK EINRICHTEN ---
# Verbindet mit der Datenbank-Datei (wird automatisch erstellt)
conn = sqlite3.connect("brettspiele.db", check_same_thread=False)
cursor = conn.cursor()

# Tabelle für die Spiele erstellen, falls sie noch nicht existiert
cursor.execute("""
CREATE TABLE IF NOT EXISTS spiele (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titel TEXT NOT NULL,
    spieler TEXT,
    dauer INTEGER,
    kategorien TEXT,
    notiz TEXT
)
""")
conn.commit()

# --- WEB-OBERFLÄCHE (STREAMLIT) ---
st.title("🎲 Meine Brettspiel-Datenbank")
st.write("Trage deine Spiele ein und filtere deine Sammlung online!")

# --- FORMULAR: NEUES SPIEL HINZUFÜGEN ---
st.header("➕ Neues Spiel hinzufügen")

with st.form("spiel_form", clear_on_submit=True):
    titel = st.text_input("Name des Spiels")
    spieler = st.text_input("Spieleranzahl (z.B. 2-4)", "2-4")
    dauer = st.number_input("Spieldauer (in Minuten)", min_value=5, value=60)

    # Hier kannst du deine Kategorien als Text oder Schlagworte eingeben
    kategorien = st.text_input("Kategorien (mit Komma trennen, z.B. Würfel, Sci-Fi)")

    notiz = st.text_area("Meine Bemerkungen")

    submit = st.form_submit_button("In Datenbank speichern")

    if submit and titel:
        # Daten in die SQLite Datenbank schreiben
        cursor.execute(
            "INSERT INTO spiele (titel, spieler, dauer, kategorien, notiz) VALUES (?, ?, ?, ?, ?)",
            (titel, spieler, dauer, kategorien, notiz),
        )
        conn.commit()
        st.success(f"'{titel}' wurde erfolgreich gespeichert!")

# --- ANZEIGE & FILTER ---
st.header("📚 Meine Sammlung")

# Alle Spiele aus der Datenbank abrufen
cursor.execute("SELECT titel, spieler, dauer, kategorien, notiz FROM spiele")
alle_spiele = cursor.fetchall()

if not alle_spiele:
    st.info("Noch keine Spiele in der Datenbank. Trage oben dein erstes Spiel ein!")
else:
    # Filter-Option in der Seitenleiste
    filter_kat = st.sidebar.text_input("🔍 Nach Kategorie filtern")

    # Spiele anzeigen
    for spiel in alle_spiele:
        s_titel, s_spieler, s_dauer, s_kat, s_notiz = spiel

        # Wenn ein Filter aktiv ist, prüfen ob die Kategorie passt
        if filter_kat.lower() in s_kat.lower():
            with st.expander(f"🔴 {s_titel} ({s_spieler} Spieler | {s_dauer} Min)"):
                st.write(f"**Kategorien:** {s_kat}")
                st.write(f"**Meine Notiz:** {s_notiz}")