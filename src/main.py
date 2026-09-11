"""Point d'entrée : traite tous les comptes-rendus (.txt) présents dans input/."""

import shutil
import sys
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))

from extract import extract_fields  # noqa: E402
from sheets import append_row  # noqa: E402

BASE_DIR = Path(__file__).parent.parent
INPUT_DIR = BASE_DIR / "input"
PROCESSED_DIR = BASE_DIR / "processed"


def process_file(text_path: Path) -> None:
    print(f"[TRAITEMENT] {text_path.name}")

    compte_rendu = text_path.read_text(encoding="utf-8")

    fields = extract_fields(compte_rendu)
    append_row(fields)

    destination = PROCESSED_DIR / text_path.name
    shutil.move(str(text_path), str(destination))

    print(f"[OK] {text_path.name} -> {fields['nom']} {fields['prenom']} ({fields['secteur_activite']})")


def main() -> None:
    load_dotenv()

    INPUT_DIR.mkdir(exist_ok=True)
    PROCESSED_DIR.mkdir(exist_ok=True)

    text_files = sorted(
        f for f in INPUT_DIR.iterdir()
        if f.is_file() and f.suffix.lower() == ".txt"
    )

    if not text_files:
        print("Aucun compte-rendu (.txt) à traiter dans input/.")
        return

    success_count = 0
    failure_count = 0

    for text_path in text_files:
        try:
            process_file(text_path)
            success_count += 1
        except Exception as exc:
            failure_count += 1
            print(f"[ERREUR] {text_path.name} : {exc}")

    print(f"\nTerminé : {success_count} réussi(s), {failure_count} échoué(s).")


if __name__ == "__main__":
    main()
