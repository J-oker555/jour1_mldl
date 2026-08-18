from pathlib import Path

from .data import ConversionAnomaly, LoadResult
from .labels import HoaxLabelResult
from .modeling import BaselineMetrics, ModelMetrics


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


def _format_trigger_counts(label_result: HoaxLabelResult) -> str:
    if not label_result.trigger_counts:
        return "- Aucun mot declencheur trouve"
    return "\n".join(f"- `{term}`: {count}" for term, count in label_result.trigger_counts.items())


def _format_hoax_examples(label_result: HoaxLabelResult) -> str:
    if not label_result.examples:
        return "- Aucun exemple positif"
    lines = []
    for example in label_result.examples:
        compact = " ".join(example.split())
        if len(compact) > 180:
            compact = f"{compact[:177]}..."
        lines.append(f"- `{compact}`")
    return "\n".join(lines)


def _format_evaluation_protocol(metrics: ModelMetrics) -> str:
    return (
        f"Split stratifie avec {metrics.test_fraction:.0%} des donnees en test, "
        f"graine aleatoire {metrics.random_seed}. "
        f"Apprentissage: {metrics.train_size} releves "
        f"({metrics.train_positive} canulars, {metrics.train_negative} non-canulars). "
        f"Test: {metrics.test_size} releves "
        f"({metrics.test_positive} canulars, {metrics.test_negative} non-canulars)."
    )


def render_report(
    load_result: LoadResult,
    anomalies: dict[str, ConversionAnomaly],
    label_result: HoaxLabelResult,
    leakage_rows: list[dict[str, str]],
    leaky_metrics: ModelMetrics,
    clean_metrics: ModelMetrics,
    baseline_metrics: BaselineMetrics,
) -> str:
    anomaly_lines = _format_conversion_anomalies(anomalies)
    leakage_lines = "\n".join(
        f"| `{row['column']}` | `{row['source']}` | {row['writer']} | {row['moment']} | {row['knows_hoax']} |"
        for row in leakage_rows
    )
    rejected_examples = _format_rejected_examples(load_result)
    rejection_reasons = _format_rejection_reasons(load_result)
    trigger_counts = _format_trigger_counts(label_result)
    hoax_examples = _format_hoax_examples(label_result)
    evaluation_protocol = _format_evaluation_protocol(leaky_metrics)

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

Regle: {label_result.rule}.

- Releves marques canulars: {label_result.positive_count}
- Proportion: {pct(label_result.positive_rate)}

Mots declencheurs trouves:

{trigger_counts}

Exemples de releves marques:

{hoax_examples}

Limite: {label_result.limitation}

## Phase 4 - Premier verdict

{evaluation_protocol}

- Sur 100 canulars reels, le systeme en attrape: {leaky_metrics.recall * 100:.2f}
- Sur 100 releves signales, vraiment canulars: {leaky_metrics.precision * 100:.2f}

Matrice de confusion sur le jeu de test:

| Reel \\ Predit | Pas canular | Canular |
| --- | ---: | ---: |
| Pas canular | {leaky_metrics.true_negative} | {leaky_metrics.false_positive} |
| Canular | {leaky_metrics.false_negative} | {leaky_metrics.true_positive} |

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

- Accuracy du stagiaire qui repond toujours `pas canular`: {pct(baseline_metrics.accuracy)}
- Accuracy du modele propre: {pct(clean_metrics.accuracy)}
- Releves signales canular par le stagiaire: {baseline_metrics.predicted_positive}
- Rappel canular du stagiaire: {pct(baseline_metrics.recall)}
- Precision canular du stagiaire: {pct(baseline_metrics.precision)}

L'accuracy seule est trompeuse ici parce que les canulars sont rares. Un systeme peut obtenir un score eleve en ignorant tous les canulars. Pour defendre le modele, il faut presenter le rappel et la precision de la classe canular.
"""


def write_report(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
