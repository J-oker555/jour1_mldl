# jour1_mldl

Projet Machine Learning - reception des releves OVNI.

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

## Validation

```powershell
.\.venv\Scripts\python.exe -m pytest
```

