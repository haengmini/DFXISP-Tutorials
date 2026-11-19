#!/usr/bin/env python3
"""PC 통합 실습: 실제 RAW 샘플 6장 -> checker -> ISP 2종 -> YOLOv8n 검출.

ISP·FPGA·AI 저장소 3개를 같은 폴더(작업 폴더)에 받아 두면 보드 없이 PC에서 돈다.
  python isp_detector_demo.py [--root 작업폴더] [--save 결과폴더]

각 프레임마다 (1) checker가 고른 모드, (2) default_isp와 lowlight_isp 출력에
YOLOv8n(JNU_DFXISP_AI의 학습 가중치)을 돌린 결과를
정답 라벨과 IoU 0.5로 맞춰 재현율/정밀도를 보여 준다. 3프레임씩이라 통계적 의미는 없다.
"""
import argparse
import csv
import sys
import time
from pathlib import Path

import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
ap.add_argument("--save", type=Path, default=None, help="ISP 출력 PNG를 저장할 폴더")
ap.add_argument("--conf", type=float, default=0.25)
args = ap.parse_args()

root = args.root.resolve()
for repo, item in (("JNU_DFXISP_ISP", "python/checker.py"),
                   ("JNU_DFXISP_FPGA", "data"),
                   ("JNU_DFXISP_AI", "models/yolov8n/yolov8n.pt")):
    if not (root / repo / item).exists():
        ap.error(f"필요한 실습 파일이 없습니다: {root / repo / item}")
sys.path.insert(0, str(root / "JNU_DFXISP_ISP" / "python"))
import checker  # noqa: E402
import default_isp_pipeline as DP  # noqa: E402
import lowlight_isp_pipeline as LP  # noqa: E402
from ultralytics import YOLO  # noqa: E402

model = YOLO(str(root / "JNU_DFXISP_AI" / "models" / "yolov8n" / "yolov8n.pt"))
# 샘플 라벨은 COCO 번호(0 사람, 1 자전거, 2 자동차)이고 YOLOv8n 가중치는 프로젝트 번호
# (0 사람, 1 자동차, 2 자전거)를 쓴다. 두 번호를 맞추려고 라벨의 1과 2를 서로 바꾼다.
LABEL_TO_MODEL = {0: 0, 1: 2, 2: 1}


def load_labels(path):
    rows = []
    if path.exists():
        for ln in path.read_text().split("\n"):
            p = ln.split()
            if len(p) >= 5:
                c, x, y, w, h = LABEL_TO_MODEL[int(p[0])], *map(float, p[1:5])
                rows.append((c, x - w / 2, y - h / 2, x + w / 2, y + h / 2))
    return rows


def iou(a, b):
    ix = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = ix * iy
    union = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / union if union > 0 else 0.0


def detect(rgb):
    r = model.predict(rgb[..., ::-1].copy(), imgsz=640, conf=args.conf, device="cpu", verbose=False)[0]
    H, W = rgb.shape[:2]
    return [(int(c), *(b / [W, H, W, H]))
            for c, b in zip(r.boxes.cls.tolist(), r.boxes.xyxy.cpu().numpy())]


def match(gt, pr):
    used, tp = set(), 0
    for p in pr:
        best, bi = 0.0, None
        for i, g in enumerate(gt):
            if i in used or g[0] != p[0]:
                continue
            v = iou(g[1:], p[1:])
            if v > best:
                best, bi = v, i
        if bi is not None and best >= 0.5:
            used.add(bi)
            tp += 1
    return tp


print(f"{'프레임':<24}{'checker':<10}{'dark16':>7}  {'ISP':<13}{'정답':>4}{'검출':>5}{'TP':>4}{'재현율':>7}{'정밀도':>7}")
tot = {"default_isp": [0, 0, 0], "lowlight_isp": [0, 0, 0]}
for ds in ("sonynod_test", "pascalraw_test"):
    d = root / "JNU_DFXISP_FPGA" / "data" / ds
    meta = {r["stem"]: r for r in csv.DictReader(open(d / "frames_meta.csv"))} if (d / "frames_meta.csv").exists() else {}
    frames = sorted((d / "raw_bin").glob("*.bin"))
    if len(frames) != 3:
        ap.error(f"{d}에 RAW 샘플 3장이 필요합니다 (현재 {len(frames)}장).")
    for f in frames:
        raw = np.fromfile(f, dtype="<u2")
        if ds == "sonynod_test":
            w, h = 5472, 3648
        else:
            w, h = int(meta[f.stem]["w"]), int(meta[f.stem]["h"])
        assert raw.size == w * h, (f, raw.size, w * h)
        mode, dr = checker.selected_mode(raw, w, h), checker.dark_ratio(raw)
        label = d / "labels" / f"{f.stem}.txt"
        if not label.is_file():
            ap.error(f"정답 라벨이 없습니다: {label}")
        gt = load_labels(label)
        for arm, fn in (("default_isp", DP.run_default_isp), ("lowlight_isp", LP.run_lowlight_isp)):
            out = fn(raw, w, h)
            if args.save:
                from PIL import Image
                args.save.mkdir(parents=True, exist_ok=True)
                Image.fromarray(out).save(args.save / f"{ds}_{f.stem}_{arm}.png")
            pr = detect(out)
            tp = match(gt, pr)
            t = tot[arm]; t[0] += len(gt); t[1] += len(pr); t[2] += tp
            rec = tp / len(gt) if gt else float("nan")
            pre = tp / len(pr) if pr else float("nan")
            print(f"{ds[:5]+'/'+f.stem:<24}{mode:<10}{dr:>7.3f}  {arm:<13}{len(gt):>4}{len(pr):>5}{tp:>4}{rec:>7.2f}{pre:>7.2f}")
print()
for arm, (g, p, tp) in tot.items():
    rec, pre = (tp / g if g else 0), (tp / p if p else 0)
    print(f"합계 {arm:<13} 정답 {g} / 검출 {p} / 맞춤 {tp}  -> 재현율 {rec:.2f}, 정밀도 {pre:.2f}")
