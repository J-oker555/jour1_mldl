import pandas as pd

from src.ufo_pipeline.modeling import baseline_always_not_hoax, baseline_always_not_hoax_metrics, train_and_evaluate


def test_train_and_evaluate_reports_split_and_confusion_matrix() -> None:
    features = pd.DataFrame(
        {
            "score": [0, 0, 0, 1, 1, 1, 2, 2],
            "kind": ["a", "a", "b", "b", "c", "c", "d", "d"],
        }
    )
    target = pd.Series([False, False, False, False, True, True, True, True])

    metrics = train_and_evaluate(features, target, seed=7, test_size=0.5)

    assert metrics.train_size == 4
    assert metrics.test_size == 4
    assert metrics.train_positive == 2
    assert metrics.train_negative == 2
    assert metrics.test_positive == 2
    assert metrics.test_negative == 2
    assert metrics.true_negative + metrics.false_positive + metrics.false_negative + metrics.true_positive == 4
    assert metrics.test_fraction == 0.5
    assert metrics.random_seed == 7


def test_baseline_always_not_hoax() -> None:
    score = baseline_always_not_hoax(pd.Series([True, False, False, False]))

    assert score == 0.75


def test_baseline_always_not_hoax_metrics_exposes_why_accuracy_is_misleading() -> None:
    metrics = baseline_always_not_hoax_metrics(pd.Series([True, False, False, False]))

    assert metrics.accuracy == 0.75
    assert metrics.recall == 0
    assert metrics.precision == 0
    assert metrics.predicted_positive == 0
    assert metrics.predicted_negative == 4
