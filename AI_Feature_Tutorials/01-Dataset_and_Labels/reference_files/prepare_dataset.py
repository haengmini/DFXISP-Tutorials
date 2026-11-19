#!/usr/bin/env python3
"""선정 목록(dataset_selection.json)대로 원본 RAW를 모아 해시를 검증한다.

사용법:
  python prepare_dataset.py --sel dataset_selection.json \
      --lod-raw <LOD_test/raw> --lod-labels <LOD_test/labels> \
      --pascal-raw <PASCAL_test/raw> --pascal-labels <PASCAL_test/labels> --out work

원본 RAW는 이 저장소에 없다. 원 배포처에서 받은 폴더를 인자로 준다.
각 파일의 SHA256이 선정 목록과 다르면 즉시 중단한다.
"""
import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--sel", type=Path, required=True)
ap.add_argument("--lod-raw", type=Path, required=True)
ap.add_argument("--lod-labels", type=Path, required=True)
ap.add_argument("--pascal-raw", type=Path, required=True)
ap.add_argument("--pascal-labels", type=Path, required=True)
ap.add_argument("--out", type=Path, required=True)
a = ap.parse_args()

sel = json.loads(a.sel.read_text(encoding="utf-8"))
src = {"night": (a.lod_raw, a.lod_labels), "day": (a.pascal_raw, a.pascal_labels)}
bad = 0
for name, (raw_dir, lab_dir) in src.items():
    (a.out / name / "raw").mkdir(parents=True, exist_ok=True)
    (a.out / name / "labels").mkdir(parents=True, exist_ok=True)
    for fr in sel["sets"][name]["frames"]:
        rp = raw_dir / fr["raw_file"]
        lp = lab_dir / f"{fr['stem']}.txt"
        if not rp.is_file() or not lp.is_file():
            print(f"없음: {rp if not rp.is_file() else lp}")
            bad += 1
            continue
        h = hashlib.sha256(rp.read_bytes()).hexdigest()
        n = len([x for x in lp.read_text().splitlines() if x.strip()])
        ok = h == fr["raw_sha256"] and n == fr["n_objects"]
        print(f"{'OK  ' if ok else 'FAIL'} {name} {fr['stem']} 객체 {n}/{fr['n_objects']}")
        if not ok:
            bad += 1
            continue
        shutil.copy2(rp, a.out / name / "raw" / rp.name)
        shutil.copy2(lp, a.out / name / "labels" / lp.name)
print("검증 통과" if bad == 0 else f"실패 {bad}건")
sys.exit(1 if bad else 0)
