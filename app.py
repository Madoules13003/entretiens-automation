"""Interface Streamlit : colle le compte-rendu Granola d'un entretien, lance l'extraction, affiche le résultat."""

import re
import sys
from datetime import datetime
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent / "src"))

from extract import extract_fields  # noqa: E402
from sheets import append_row  # noqa: E402

load_dotenv()

BASE_DIR = Path(__file__).parent
PROCESSED_DIR = BASE_DIR / "processed"
PROCESSED_DIR.mkdir(exist_ok=True)

st.set_page_config(page_title="Saisie automatique des entretiens", layout="centered")
st.title("Saisie automatique des entretiens")
st.caption(
    "Colle le compte-rendu Granola de l'entretien : l'extraction des champs et "
    "l'écriture dans le Google Sheet se font automatiquement."
)

if "results" not in st.session_state:
    st.session_state.results = []


def _archive_name(fields: dict) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = "_".join(part for part in (fields.get("nom"), fields.get("prenom")) if part)
    slug = re.sub(r"[^\w-]", "", slug.replace(" ", "_"))
    return f"{slug}_{timestamp}.txt" if slug else f"entretien_{timestamp}.txt"


with st.form("compte_rendu_form", clear_on_submit=True):
    compte_rendu = st.text_area(
        "Compte-rendu Granola",
        height=280,
        placeholder="Colle ici le compte-rendu écrit fourni par Granola...",
    )
    submitted = st.form_submit_button("Traiter", type="primary")

if submitted:
    if not compte_rendu.strip():
        st.warning("Le compte-rendu est vide — colle un texte avant de traiter.")
    else:
        with st.status("Traitement en cours...") as status:
            try:
                fields = extract_fields(compte_rendu)
                append_row(fields)
                (PROCESSED_DIR / _archive_name(fields)).write_text(compte_rendu, encoding="utf-8")

                st.session_state.results.insert(
                    0,
                    {
                        "Statut": "OK",
                        "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Nom": fields["nom"],
                        "Prénom": fields["prenom"],
                        "Formation": fields["formation"],
                        "Projet 1": fields["projet_1"],
                        "Projet 2": fields["projet_2"],
                        "Alignement": fields["alignement_projet"],
                        "Emploi/Formation": fields["emploi_formation"],
                        "Secteur": fields["secteur"],
                    },
                )
                status.update(label="Ajouté au Google Sheet", state="complete")
            except Exception as exc:
                st.session_state.results.insert(
                    0,
                    {
                        "Statut": f"Erreur : {exc}",
                        "Date": "",
                        "Nom": "",
                        "Prénom": "",
                        "Formation": "",
                        "Projet 1": "",
                        "Projet 2": "",
                        "Alignement": "",
                        "Emploi/Formation": "",
                        "Secteur": "",
                    },
                )
                status.update(label="Échec du traitement", state="error")

if st.session_state.results:
    st.divider()
    st.subheader("Historique de cette session")
    st.dataframe(st.session_state.results, use_container_width=True)
