import csv
import json

from scripts.evaluate_pairwise_judges import finalize, score


def _jsonl(path, rows):
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


def test_reasonableness_is_a_hard_gate_and_judges_are_ranked(tmp_path):
    manifest = tmp_path / "pairs.jsonl"
    _jsonl(manifest, [{"pair_id": "p1"}, {"pair_id": "p2"}, {"pair_id": "p3"}])
    labels = tmp_path / "labels.csv"
    with labels.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["pair_id", "human_label", "both_reasonable"])
        writer.writeheader()
        writer.writerows([
            {"pair_id": "p1", "human_label": "A", "both_reasonable": "yes"},
            {"pair_id": "p2", "human_label": "B", "both_reasonable": "no"},
            {"pair_id": "p3", "human_label": "tie", "both_reasonable": "yes"},
        ])
    final_path = tmp_path / "final.jsonl"
    final = finalize(manifest, labels, final_path)
    assert [row["pair_id"] for row in final] == ["p1", "p3"]

    strong = tmp_path / "strong.jsonl"
    weak = tmp_path / "weak.jsonl"
    _jsonl(strong, [{"pair_id": "p1", "choice": "A", "judge_model": "strong"}, {"pair_id": "p3", "choice": "tie"}])
    _jsonl(weak, [{"pair_id": "p1", "choice": "B", "judge_model": "weak"}, {"pair_id": "p3", "choice": "tie"}])
    ranked = score(final, [weak, strong], tmp_path / "ranking.json")
    assert ranked[0]["judge_model"] == "strong"
    assert ranked[0]["exact_agreement"] == 1.0
