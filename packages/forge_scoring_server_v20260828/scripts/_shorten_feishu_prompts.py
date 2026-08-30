#!/usr/bin/env python3
"""Shorten FULL_PROMPTS and SCENE_CONCEPT_OVERRIDES in build_feishu_doc.py."""
import re

src = open('scripts/build_feishu_doc.py', encoding='utf-8').read()

# ---- extract & exec FULL_PROMPTS ----
fp_start = src.index('FULL_PROMPTS = {')
fp_end   = src.index('\n}\n', fp_start) + 3
g = {}
exec(src[fp_start:fp_end], g)
FULL_PROMPTS = g['FULL_PROMPTS']

# ---- extract & exec SCENE_CONCEPT_OVERRIDES ----
ov_start = src.index('SCENE_CONCEPT_OVERRIDES = {')
ov_end   = src.index('\n}\n', ov_start) + 3
g2 = {}
exec(src[ov_start:ov_end], g2)
SCENE_CONCEPT_OVERRIDES = g2['SCENE_CONCEPT_OVERRIDES']

PREFIX = (
    "Use the provided reference image as the first frame. "
    "Generate a 5-8 second realistic industrial video. "
)

STOP_RE = re.compile(
    r'\s+(?:Reference subject:|Industrial logic|Geometric integrity'
    r'|Physical plausibility|Do not|Temporal consistency)',
    re.DOTALL,
)

def shorten_prompt(full):
    text = re.sub(r'\s+', ' ', full)
    m = re.search(r'Scene:\s*(.+)', text, re.DOTALL)
    if not m:
        return full
    rest = m.group(1)
    stop = STOP_RE.search(rest)
    scene = rest[:stop.start()].strip().rstrip('.') if stop else rest.strip().rstrip('.')
    return PREFIX + scene + '.'

new_fp = {k: shorten_prompt(v) for k, v in FULL_PROMPTS.items()}
new_ov = {}
for k, v in SCENE_CONCEPT_OVERRIDES.items():
    entry = dict(v)
    if 'full_prompt' in entry:
        entry['full_prompt'] = shorten_prompt(entry['full_prompt'])
    new_ov[k] = entry

# --- serialise back to Python source ---
import json

def render_str(s):
    # Use json.dumps for safe quoting, then strip outer quotes and use triple-quote block
    return '(\n        ' + json.dumps(s, ensure_ascii=False) + '\n    )'

lines_fp = ['FULL_PROMPTS = {']
for k, v in new_fp.items():
    lines_fp.append(f'    {json.dumps(k)}: {json.dumps(v, ensure_ascii=False)},')
lines_fp.append('}')
new_fp_src = '\n'.join(lines_fp)

lines_ov = ['SCENE_CONCEPT_OVERRIDES = {']
for k, v in new_ov.items():
    lines_ov.append(f'    {json.dumps(k)}: {{')
    for sk, sv in v.items():
        lines_ov.append(f'        {json.dumps(sk)}: {json.dumps(sv, ensure_ascii=False)},')
    lines_ov.append('    },')
lines_ov.append('}')
new_ov_src = '\n'.join(lines_ov)

# replace in source
new_src = src[:fp_start] + new_fp_src + '\n' + src[fp_end:]
ov_start2 = new_src.index('SCENE_CONCEPT_OVERRIDES = {')
ov_end2   = new_src.index('\n}\n', ov_start2) + 3
new_src = new_src[:ov_start2] + new_ov_src + '\n' + new_src[ov_end2:]

open('scripts/build_feishu_doc.py', 'w', encoding='utf-8').write(new_src)
print(f'Updated {len(new_fp)} FULL_PROMPTS and {len(new_ov)} SCENE_CONCEPT_OVERRIDES.')
print()
for k in list(new_fp)[:4]:
    p = new_fp[k]
    print(f'  [{k}] {len(p.split())}w: {p[:100]}...')
print()
for k, v in new_ov.items():
    if 'full_prompt' in v:
        p = v['full_prompt']
        print(f'  [override {k}] {len(p.split())}w: {p[:100]}...')
