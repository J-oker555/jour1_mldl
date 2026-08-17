from src.ufo_pipeline.config import RAW_DATA, REPORT
from src.ufo_pipeline.data import convert_types, download_data, load_transmission
from src.ufo_pipeline.features import add_basic_features, leakage_table
from src.ufo_pipeline.labels import describe_hoax_label
from src.ufo_pipeline.modeling import baseline_always_not_hoax, train_and_evaluate
from src.ufo_pipeline.reporting import render_report, write_report


def main() -> None:
    csv_path = download_data(RAW_DATA)
    load_result = load_transmission(csv_path)
    frame, anomalies = convert_types(load_result.frame)
    label_result = describe_hoax_label(frame["comments"])
    target = label_result.labels

    leaky_features = add_basic_features(frame, include_leaky=True)
    clean_features = add_basic_features(frame, include_leaky=False)
    leaky_metrics = train_and_evaluate(leaky_features, target)
    clean_metrics = train_and_evaluate(clean_features, target)
    baseline_accuracy = baseline_always_not_hoax(target)

    report = render_report(
        load_result=load_result,
        anomalies=anomalies,
        label_result=label_result,
        leakage_rows=leakage_table(leaky_features.columns.tolist()),
        leaky_metrics=leaky_metrics,
        clean_metrics=clean_metrics,
        baseline_accuracy=baseline_accuracy,
    )
    write_report(REPORT, report)
    print(f"Rapport ecrit dans {REPORT}")


if __name__ == "__main__":
    main()
