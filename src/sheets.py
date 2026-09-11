"""Écriture des résultats dans le Google Sheet de destination."""

import os
from datetime import datetime
from typing import Optional

import gspread
import streamlit as st
from google.oauth2.service_account import Credentials

_SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

_client: Optional[gspread.Client] = None


def _load_credentials() -> Credentials:
    if "gcp_service_account" in st.secrets:
        return Credentials.from_service_account_info(
            dict(st.secrets["gcp_service_account"]), scopes=_SCOPES
        )
    service_account_path = os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]
    return Credentials.from_service_account_file(service_account_path, scopes=_SCOPES)


def _get_client() -> gspread.Client:
    global _client
    if _client is None:
        _client = gspread.authorize(_load_credentials())
    return _client


def append_row(fields: dict) -> None:
    """Ajoute une ligne au Google Sheet à partir des champs extraits."""
    sheet_id = st.secrets.get("GOOGLE_SHEET_ID") or os.environ["GOOGLE_SHEET_ID"]
    client = _get_client()
    worksheet = client.open_by_key(sheet_id).sheet1

    row = [
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        fields["nom"],
        fields["prenom"],
        fields["formation"],
        fields["projet_1"],
        fields["projet_2"],
        fields["alignement_projet"],
        fields["emploi_formation"],
        fields["secteur"],
    ]
    worksheet.append_row(row, value_input_option="USER_ENTERED")
