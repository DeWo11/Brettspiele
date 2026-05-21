import streamlit as st
import pandas as pd
import gspread

# --- SEITEN-EINSTELLUNGEN ---
st.set_page_config(
    page_title="Meine Brettspiel-Datenbank",
    page_icon="🎲",
    layout="centered"
)

st.title("🎲 Meine Brettspiel-Datenbank")
st.write("Verwalte deine Brettspiel-Sammlung ganz einfach über diese Web-Oberfläche. Direkt und stabil über gspread.")

DOKUMENT_URL = "https://docs.google.com/spreadsheets/d/1_T4tN3BLPD4rt6F5ccjS0IlbcDkZ19lmobDdajIIn-U/edit?gid=0#gid=0"

# --- MANUELLE GOOGLE VERBINDUNG (GSPREAD) ---
@st.cache_resource
def get_google_client():
    # Wir bauen das originale Google-JSON aus deinen Streamlit-Secrets nach
    credentials = {
        "type": st.secrets["connections"]["gsheets"]["type"],
        "project_id": st.secrets["connections"]["gsheets"]["project_id"],
        "private_key_id": st.secrets["connections"]["gsheets"]["private_key_id"],
        "private_key": st.secrets["connections"]["gsheets"]["private_key"],
        "client_email": st.secrets["connections"]["gsheets"]["client_email"],
        "client_id": st.secrets["connections"]["gsheets"]["client_id"],
        "auth_uri": st.secrets["connections"]["gsheets"]["auth_uri"],
        "token_uri": st.secrets["connections"]["gsheets"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["connections"]["gsheets"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["connections"]["gsheets"]["client_x509_cert_url"],
        "universe_domain": st.secrets["connections"]["gsheets"]["universe_domain"]
    }
    # Direktes Einloggen bei Google ohne Streamlit-Zwischenschicht
    return gspread.service_account_from_dict(credentials)

try:
    gc = get_google_client()
    # Öffne die Tabelle und das Tabellenblatt direkt
    sh = gc.open_by_url(DOKUMENT_URL)
    worksheet = sh.worksheet("spiele")
    verbindung_erfolgreich = True
except Exception as init_err:
    st.error(f"⚠️ Verbindungsfehler zu Google: {init_err}")
    verbindung_erfolgreich = False


# --- FORMULAR: NEUES SPIEL HINZUFÜGEN ---
st.header("➕ Neues Spiel hinzufügen")

with st.form("spiel_form", clear_on_submit=True):
    titel = st.text_input("Name des Spiels")
    spieler = st.text_input("Spieleranzahl", "2-4")
    dauer = st.number_input("Spieldauer (in Minuten)", min_value=5, value=60)
    kategorien = st.text_input("Kategorien (mit Komma trennen)")
    notiz = st.text_area("Meine Bemerkungen")

    submit = st.form_submit_button("In Google Sheets speichern")

    if submit and titel and verbindung_erfolgreich:
        try:
            # Zeile direkt ans Ende der Google-Tabelle anhängen
            neue_zeile = [titel, spieler, int(dauer), kategorien, notiz]
            worksheet.append_row(neue_zeile)
            
            st.success(f"🎲 '{titel}' wurde erfolgreich gespeichert!")
            st.cache_data.clear() # Cache leeren, damit die Anzeige neu lädt
        except Exception as e:
            st.error(f"Fehler beim Speichern: {e}")


# --- ANZEIGE: MEINE SAMMLUNG ---
st.header("📚 Meine Sammlung")

if verbindung_erfolgreich:
    try:
        # Alle Daten aus dem Sheet holen
        all_records = worksheet.get_all_records()
        
        if all_records:
            daten = pd.DataFrame(all_records)
            st.dataframe(
                daten, 
                use_container_width=True,
                hide_index=True
            )
            st.info(f"Insgesamt befinden sich aktuell **{len(daten)} Spiele** in deiner Sammlung.")
        else:
            st.warning("Deine Sammlung ist aktuell noch leer. Trage oben dein erstes Spiel ein!")
            
    except Exception as read_err:
        st.warning(f"Konnte Daten nicht anzeigen: {read_err}")
else:
    st.warning("Keine Verbindung zur Datenbank möglich.")