# CONTEXT.md — Automatisation de la saisie des entretiens

> Fichier de contexte pour Claude Code. À lire **en entier avant d'écrire du code**.

## 1. Objectif

Automatiser la saisie post-entretien d'un consultant. Aujourd'hui, après chaque
entretien, l'utilisateur remplit manuellement un fichier tableur avec 5 champs.
On veut supprimer cette saisie manuelle.

**Objectif prioritaire : gain de temps.** Toute décision technique doit favoriser
la simplicité de mise en route et la fiabilité, pas l'exhaustivité.

## 2. Flux cible (pipeline)

```
Fichier audio (input/)  →  Transcription (Whisper)  →  Extraction 5 champs (Claude)  →  Ligne ajoutée au Google Sheet
```

1. L'utilisateur dépose un fichier audio d'entretien dans `input/`
   (formats à supporter : mp3, m4a, wav).
2. Le script détecte le nouveau fichier, le transcrit via l'API **Whisper**
   (OpenAI, modèle `whisper-1` ou équivalent courant).
3. La transcription est envoyée à l'API **Claude** (Anthropic) qui extrait
   les 5 champs en **JSON strict**.
4. Le script ajoute une ligne au **Google Sheet** de destination.
5. Le fichier audio traité est déplacé dans `processed/` pour éviter les doublons.

## 3. Les 5 champs à extraire

| Champ                | Type   | Contrainte                                    |
|----------------------|--------|-----------------------------------------------|
| nom                  | string | tel qu'entendu                                |
| prenom               | string | tel qu'entendu                                |
| projet_principal     | string | résumé court (1 phrase max)                   |
| projet_secondaire    | string | résumé court (1 phrase max), "" si absent     |
| secteur_activite     | string | **doit appartenir à la liste ci-dessous**     |

### Liste fermée des secteurs (à ajuster par l'utilisateur)

```
["E-commerce", "Immobilier", "Santé", "Restauration", "BTP",
 "Services aux entreprises", "Tech / SaaS", "Autre"]
```

> Si le secteur détecté ne correspond à aucune valeur, renvoyer `"Autre"`.
> ⚠️ Cette liste est un point de personnalisation : demander à l'utilisateur
> de la valider / compléter avant de figer.

## 4. Format de sortie attendu de Claude (extraction)

Claude doit répondre **uniquement** avec cet objet JSON, sans texte autour,
sans balises Markdown :

```json
{
  "nom": "",
  "prenom": "",
  "projet_principal": "",
  "projet_secondaire": "",
  "secteur_activite": ""
}
```

Le script doit parser ce JSON de façon défensive (gérer le cas où le modèle
ajoute malgré tout du texte ou des backticks).

## 5. Google Sheet de destination

- En-têtes (ligne 1, dans cet ordre exact) :
  `Date | Nom | Prénom | Projet principal | Projet secondaire | Secteur`
- La colonne `Date` = date/heure de traitement (format `YYYY-MM-DD HH:MM`).
- Une ligne = un entretien.
- Accès via l'API Google Sheets (service account recommandé, voir §7).

## 6. Contraintes techniques

- **Langage : Python 3.11+.**
- Dépendances pressenties : `openai` (Whisper), `anthropic` (extraction),
  `gspread` + `google-auth` (Sheets). À confirmer / proposer mieux si pertinent.
- Config via un fichier `.env` (jamais de clés en dur dans le code).
- Structure claire et modulaire : transcription, extraction et écriture Sheet
  dans des fonctions/modules séparés, pour pouvoir réutiliser les briques
  sur de FUTURES automatisations (objectif « tout-en-un » à terme).
- Logging simple (quel fichier traité, succès/échec) dans la console.
- Gestion d'erreurs : un échec sur un fichier ne doit pas bloquer les suivants.

## 7. Secrets attendus dans `.env`

```
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
GOOGLE_SHEET_ID=...
GOOGLE_SERVICE_ACCOUNT_JSON=chemin/vers/service_account.json
```

## 8. Arborescence proposée (à valider avec l'utilisateur)

```
entretiens-automation/
├── CONTEXT.md
├── .env                 # secrets, NON versionné
├── .gitignore
├── requirements.txt
├── input/               # audios à traiter
├── processed/           # audios traités
└── src/
    ├── main.py          # orchestration du pipeline
    ├── transcribe.py    # Whisper
    ├── extract.py       # Claude → JSON
    └── sheets.py        # écriture Google Sheets
```

## 9. Mode de travail attendu de Claude Code

1. **Ne pas coder immédiatement.** D'abord proposer l'arborescence + la liste
   des dépendances, puis attendre validation.
2. Poser les questions ouvertes AVANT de coder (ex. : la liste des secteurs
   est-elle validée ? déclenchement manuel `python main.py` ou surveillance
   auto du dossier ?).
3. Écrire le code brique par brique, testable indépendamment.
4. Signaler tout choix qui enferme dans une techno ou complexifie la
   maintenance future.

## 10. Décisions ouvertes (à trancher avec l'utilisateur)

- [ ] Liste définitive des secteurs d'activité.
- [ ] Déclenchement : commande manuelle vs surveillance automatique du dossier
      (`watchdog`).
- [ ] Modèle Claude à utiliser pour l'extraction (un modèle rapide et
      économique suffit largement ici).
- [ ] Faut-il garder la transcription complète quelque part (archivage) ou
      seulement les 5 champs ?
