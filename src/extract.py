"""Extraction des 8 champs structurés depuis un compte-rendu Granola (sections markdown `# titre`)."""

import re

REQUIRED_FIELDS = [
    "nom",
    "prenom",
    "formation",
    "projet_1",
    "projet_2",
    "alignement_projet",
    "emploi_formation",
    "secteur",
]

ALIGNEMENT_VALUES = ["Oui", "Non"]
EMPLOI_FORMATION_VALUES = ["Emploi", "Formation"]

# Point de personnalisation : liste à valider/ajuster avec l'utilisateur.
SECTEURS = [
    "Commerce, hôtellerie, restauration, tertiaire",
    "Industrie, logistique, bâtiment, artisanat, numérique",
    "Santé, social, formation et enseignement",
    "Nettoyage extérieur, sécurité",
    "Projets à confirmer",
]

# Titre de section Granola (en minuscules) -> nom du champ interne.
SECTION_FIELD_MAP = {
    "nom": "nom",
    "prénom": "prenom",
    "prenom": "prenom",
    "formation": "formation",
    "projet numéro 1": "projet_1",
    "projet numero 1": "projet_1",
    "projet numéro 2": "projet_2",
    "projet numero 2": "projet_2",
    "alignement projet": "alignement_projet",
    "emploi / formation": "emploi_formation",
    "emploi/formation": "emploi_formation",
    "secteur": "secteur",
}


def _parse_sections(compte_rendu: str) -> dict:
    """Découpe le compte-rendu en sections à partir des titres markdown `# Titre`."""
    headers = list(re.finditer(r"^#\s+(.+?)\s*$", compte_rendu, re.MULTILINE))
    sections = {}
    for i, header in enumerate(headers):
        title = header.group(1).strip().lower()
        start = header.end()
        end = headers[i + 1].start() if i + 1 < len(headers) else len(compte_rendu)
        sections[title] = compte_rendu[start:end].strip()
    return sections


def _normalize_choice(value: str, allowed: list) -> str:
    for option in allowed:
        if value.strip().lower() == option.lower():
            return option
    return value


def _normalize_secteur(value: str) -> str:
    for option in SECTEURS:
        if value.strip().lower() == option.lower():
            return option
    return "Projets à confirmer"


def extract_fields(compte_rendu: str) -> dict:
    """Extrait les 8 champs à partir des sections `# Titre` du compte-rendu Granola."""
    sections = _parse_sections(compte_rendu)

    if not sections:
        raise ValueError(
            "Aucune section (# Titre) détectée dans le compte-rendu — "
            "vérifie que le template Granola a bien été utilisé."
        )

    fields = {}
    for section_title, field_name in SECTION_FIELD_MAP.items():
        if section_title in sections:
            fields[field_name] = sections[section_title]

    for field in REQUIRED_FIELDS:
        fields.setdefault(field, "")

    fields["alignement_projet"] = _normalize_choice(fields["alignement_projet"], ALIGNEMENT_VALUES)
    fields["emploi_formation"] = _normalize_choice(fields["emploi_formation"], EMPLOI_FORMATION_VALUES)
    fields["secteur"] = _normalize_secteur(fields["secteur"])

    return fields
