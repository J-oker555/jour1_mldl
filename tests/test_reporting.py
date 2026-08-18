from src.ufo_pipeline.config import REPORT


def test_generated_report_contains_all_project_phases() -> None:
    content = REPORT.read_text(encoding="utf-8")

    for phase in range(1, 7):
        assert f"## Phase {phase}" in content

    assert "Matrice de confusion" in content
    assert "Rappel canular du stagiaire" in content
