from pathlib import Path

from .data import ConversionAnomaly, LoadResult
from .modeling import ModelMetrics


def pct(value: float) -> str:
    return f"{value * 100:.2f} %"


def _format_rejected_examples(load_result: LoadResult, limit: int = 3) -> str:
    if not load_result.rejected_records:
        return "Aucune ligne traitee a part."

    lines = []
    for record in load_result.rejected_records[:limit]:
        preview = " | ".join(record.row)
        if len(preview) > 180:
            preview = f"{preview[:177]}..."
        lines.append(f"- Ligne {record.line_number}: {record.reason}. Extrait: `{preview}`")
    return "\n".join(lines)


def _format_rejection_reasons(load_result: LoadResult) -> str:
    if not load_result.rejection_reasons:
        return "- Aucun rejet"
    return "\n".join(f"- {reason}: {count}" for reason, count in load_result.rejection_reasons.items())


def _format_conversion_anomalies(anomalies: dict[str, ConversionAnomaly]) -> str:
    lines = []
    for info in anomalies.values():
        lines.append(
            f"- `{info.column}` -> {info.target_type}: {info.invalid_count} valeurs invalides, "
            f"{info.missing_count} valeurs vides. Origine probable: {info.origin}. "
            f"Exemples fautifs: {info.examples}"
        )
        for nature, count in info.nature_counts.items():
            lines.append(f"  - Nature: {nature}: {count}")
    return "\n".join(lines)


def render_report(
    load_result: LoadResult,
    anomalies: dict[str, ConversionAnomaly],
    hoax_count: int,
    hoax_rate: float,
    leakage_rows: list[dict[str, str]],
    leaky_metrics: ModelMetrics,
    clean_metrics: ModelMetrics,
    baseline_accuracy: float,
) -> str:
    anomaly_lines = _format_conversion_anomalies(anomalies)
    leakage_lines = "\n".join(
        f"| `{row['column']}` | `{row['source']}` | {row['writer']} | {row['moment']} | {row['knows_hoax']} |"
        for row in leakage_rows
    )
    rejected_examples = _format_rejected_examples(load_result)
    rejection_reasons = _format_rejection_reasons(load_result)

    return f"""# Rapport

## Phase 1 - Ouvrir la caisse

- Lignes logiques lues: {load_result.total_records}
- Lignes chargees: {load_result.loaded_records}
- Lignes traitees a part: {load_result.rejected_records_count}

Les lignes mises a part sont celles dont le nombre de champs ne correspond pas aux onze champs du manifeste.

Repartition des problemes:

{rejection_reasons}

Exemples:

{rejected_examples}

## Phase 2 - Types et anomalies

Les conversions sont appliquees sans supprimer de ligne. Les valeurs impossibles deviennent `NaN` ou `NaT`, puis sont comptees et conservees pour l'analyse.

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
