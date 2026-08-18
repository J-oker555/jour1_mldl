# jour1_mldl

Projet Machine Learning - reception des releves OVNI.

Le depot contient un pipeline reproductible qui part du telechargement du CSV brut et regenere le rapport final.

## Installation

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Execution

```powershell
.\.venv\Scripts\python.exe analyse.py
```

Le script telecharge le CSV dans `data/raw/`, reconstruit les resultats et met a jour `RAPPORT.md`.
Le fichier CSV brut est ignore par Git pour garder le depot leger.

## Validation

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Validation de bout en bout utilisee pendant le developpement :

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe analyse.py
```

## Structure

- `analyse.py` : point d'entree qui execute toutes les phases.
- `src/ufo_pipeline/data.py` : telechargement, chargement CSV et conversions.
- `src/ufo_pipeline/labels.py` : construction de l'etiquette canular.
- `src/ufo_pipeline/features.py` : features et detection de fuite.
- `src/ufo_pipeline/modeling.py` : modele, evaluation et baseline.
- `src/ufo_pipeline/reporting.py` : generation de `RAPPORT.md`.
- `tests/` : tests unitaires du pipeline.

## Resultats actuels

- lignes lues : 88 875
- lignes chargees : 88 679
- lignes traitees a part : 196
- canulars etiquetes : 827, soit 0.93 %
- tests : 12 tests unitaires
