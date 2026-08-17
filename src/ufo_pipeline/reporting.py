from pathlib import Path

from .data import LoadResult
from .modeling import ModelMetrics


def pct(value: float) -> str:
    return f"{value * 100:.2f} %"


def render_report(
    load_result: LoadResult,
    anomalies: dict[str, dict[str, object]],
    hoax_count: int,
    hoax_rate: float,
    leakage_rows: list[dict[str, str]],
    leaky_metrics: ModelMetrics,
    clean_metrics: ModelMetrics,
    baseline_accuracy: float,
) -> str:
    anomaly_lines = "\n".join(
        f"- `{column}` ({info['type']}): {info['count']} valeurs invalides. Exemples: {info['examples']}"
        for column, info in anomalies.items()
    )
    leakage_lines = "\n".join(
        f"| `{row['column']}` | `{row['source']}` | {row['writer']} | {row['moment']} | {row['knows_hoax']} |"
        for row in leakage_rows
    )

    return f"""# Rapport

## Phase 1 - Ouvrir la caisse

- Lignes logiques lues: {load_result.total_records}
- Lignes chargees: {load_result.loaded_records}
- Lignes traitees a part: {len(load_result.rejected_records)}

Les lignes mises a part sont celles dont le nombre de champs ne correspond pas aux onze champs du manifeste.

## Phase 2 - Types et anomalies

{anomaly_lines}

## Phase 3 - Etiquette canular

Regle: un releve est marque comme canular si le temoignage contient un mot explicite comme `hoax`, `fake`, `prank` ou `joke`.

- Releves marques canulars: {hoax_count}
- Proportion: {pct(hoax_rate)}

Limite: cette regle rate les canulars qui ne sont pas avoues dans le texte et peut attraper a tort un temoignage qui nie explicitement le canular.

## Phase 4 - Premier verdict

Evaluation sur {leaky_metrics.test_size} releves jamais vus pendant l'apprentissage.

- Sur 100 canulars reels, le systeme en attrape: {leaky_metrics.recall * 100:.2f}
- Sur 100 releves signales, vraiment canulars: {leaky_metrics.precision * 100:.2f}

## Phase 5 - Fuite de donnees

Le premier modele utilise une information derivee du temoignage alors que l'etiquette de canular vient aussi du temoignage. Ce score n'a donc pas le droit d'etre presente comme une prediction disponible avant lecture/traitement du dossier.

| Colonne modele | Source | Qui ecrit | Quand | Savait deja si canular |
| --- | --- | --- | --- | --- |
{leakage_lines}

| Mesure | Avant retrait | Apres retrait |
| --- | ---: | ---: |
| Rappel canular | {pct(leaky_metrics.recall)} | {pct(clean_metrics.recall)} |
| Precision canular | {pct(leaky_metrics.precision)} | {pct(clean_metrics.precision)} |
| Accuracy | {pct(leaky_metrics.accuracy)} | {pct(clean_metrics.accuracy)} |

## Phase 6 - Modele naif

- Accuracy du stagiaire qui repond toujours `pas canular`: {pct(baseline_accuracy)}
- Accuracy du modele propre: {pct(clean_metrics.accuracy)}

L'accuracy seule est trompeuse ici parce que les canulars sont rares. Un systeme peut obtenir un score eleve en ignorant tous les canulars. Pour defendre le modele, il faut presenter le rappel et la precision de la classe canular.
"""


def write_report(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
