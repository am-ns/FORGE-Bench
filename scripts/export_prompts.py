"""Export all prompts to a readable markdown file for easy copy-paste."""
import json
from pathlib import Path

with open("C:/Users/assd/S_I_Eval/dataset/annotations/samples.json", encoding="utf-8") as f:
    samples = json.load(f)

main = [s for s in samples if not s["task_id"].startswith(("SA","SB","SC"))]
sens = [s for s in samples if s["task_id"].startswith(("SA","SB","SC"))]

lines = ["# FORGE Prompt Reference\n"]
lines.append("每条格式：`task_id` | 参考图 | **Prompt**\n")

domain_order = ["aerospace","vehicle","energy","manufacturing","microelectronics","robotics"]
domain_cn = {
    "aerospace":"航空航天","vehicle":"地面车辆","energy":"能源",
    "manufacturing":"制造业","microelectronics":"微电子","robotics":"机器人"
}

for domain in domain_order:
    group = [s for s in main if s["domain"] == domain]
    lines.append(f"\n## {domain_cn[domain]}（{domain}）\n")
    for s in group:
        img = s["image_path"].split("/")[-1]
        lines.append(f"### `{s['task_id']}` — {img}")
        lines.append(f"> {s['text']}")
        lines.append("")

lines.append("\n---\n## 敏感性实验（SA / SB / SC）\n")
for gk in ["SA","SB","SC"]:
    group = [s for s in sens if s["task_id"].startswith(gk)]
    lines.append(f"### {gk} — {group[0]['text'].split('.')[0][:40]}...")
    for s in group:
        lines.append(f"- **`{s['task_id']}`** `{s['vfa_target']}`")
        lines.append(f"  > {s['text']}")
    lines.append("")

out = Path("C:/Users/assd/S_I_Eval/prompts.md")
out.write_text("\n".join(lines), encoding="utf-8")
print(f"Wrote {len(samples)} prompts to {out}")
