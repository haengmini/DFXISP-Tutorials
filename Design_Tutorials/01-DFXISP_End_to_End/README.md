# Design 튜토리얼 1: DFXISP 처음부터 끝까지

**필요한 것:** 앞선 튜토리얼 전부, ZCU104 보드, Vivado·Vitis HLS·PetaLinux 2024.1, Docker와 Vitis AI 3.5 | **PC만으로 되는 부분:** 1단계, 2단계

## 소개

카메라가 어두운 장면을 찍으면 물체 검출 AI가 사람, 자동차, 자전거를 잘 못 찾습니다. 이 연구는 **판단기(checker)가 장면의 밝기를 보고, 밝으면 일반 ISP, 어두우면 저조도 ISP를 FPGA 위에서 실제로 바꿔 끼운 뒤(DFX)**, 그 영상에서 검출기(DPU 위의 YOLOv8n)가 물체를 찾게 합니다.

```text
카메라 RAW -> 판단기(checker) -> 재구성 영역(RP)에 일반 ISP 또는 저조도 ISP -> DPU(YOLOv8n) -> 검출 결과
                  |
        히스테리시스(진입 64%, 이탈 60%): 판단이 흔들려도 회로를 자주 바꾸지 않는다
```

이 튜토리얼은 연구 전체를 네 단계로 따라갑니다. 각 단계에 **이 저장소에서 직접 확인한 것**과 **연구 기록을 근거로 한 것**을 구분해 적었습니다.

## 1단계: PC에서 전체 흐름 맛보기 (직접 확인함)

실제 RAW 샘플 6장에 판단기, 두 ISP, YOLOv8n 검출을 차례로 적용하고 정답과 비교합니다.

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install torch==2.11.0 torchvision==0.26.0 --index-url https://download.pytorch.org/whl/cpu
pip install -r reference_files/requirements.txt
python reference_files/isp_detector_demo.py --root <선행 저장소 4개가 있는 폴더> --save out
```

스크립트는 `JNU_DFXISP_ISP`, `JNU_DFXISP_FPGA`, `JNU_DFXISP_AI` 세 저장소의 폴더를 `--root` 아래에서 찾습니다. 저장소 이름을 폴더 이름으로 쓰세요.

**확인한 결과** (CPU 추론, Ultralytics 8.4.174, 약 25초): 정답 50개 중 `default_ISP`가 35개, `lowlight_ISP`가 36개를 맞췄습니다(재현율 0.70과 0.72, 정밀도 0.73과 0.80). 샘플이 6장뿐이라 통계적 의미는 없습니다. **`lowlight_ISP`가 낫다는 근거로 쓰면 안 되고**, 흐름이 이어져 동작하는지만 확인하는 용도입니다. 주간 샘플 1장은 판단기가 저조도로 오판정합니다(어두운 픽셀 비율 0.630이 기준 0.62를 아주 조금 넘기 때문입니다).

## 2단계: 설계 검증 (직접 확인함)

[ISP 튜토리얼](../../ISP_Feature_Tutorials/01-default_ISP_and_lowlight_ISP/README.md), [HLS 튜토리얼](../../HLS_Feature_Tutorials/01-RM_synthesis_and_csim/README.md), [DFX 튜토리얼](../../DFX_Feature_Tutorials/01-Fabric_only_DFX_flow/README.md)을 순서대로 마칩니다. 각 문서에 적은 기대 결과가 나와야 다음으로 넘어갑니다.

## 3단계: 보드에 통합 (연구 기록 근거, 새로 처음부터 재현하지는 않음)

2단계의 구조를 ZCU104 보드와 DPU에 통합합니다. 필요한 구성은 아래와 같습니다.

| 구성 | 사양 |
|---|---|
| 보드 | AMD ZCU104 (`xczu7ev-ffvc1156-2-e`), USB-UART |
| 호스트 | Ubuntu 22.04.5, Vivado·Vitis HLS·Vitis 2024.1, PetaLinux 2024.1 |
| DPU | `DPUCZDX8G_ISA1_B4096` |
| 모델 양자화 | Vitis AI 3.5 (Docker) |
| 부팅 | 보드의 콜드 부팅마다 PCAP_PR이 0인지 확인한 뒤 실행 |

보드 부팅 이미지와 양자화 모델은 **재빌드하지 않고 보관된 것을 재사용하는 재실행**이 현재 검증된 범위입니다. 재빌드와 고정 ISP 기준선 재측정은 별도 절차이며 이 튜토리얼이 보장하지 않습니다.

## 4단계: 결과 읽기

연구의 최종 비교(3시드 평균, 보드 실측)는 아래와 같습니다. 수치는 연구 기록에서 가져온 것이며 이 튜토리얼에서 새로 측정한 것이 아닙니다. 지표는 mAP50-95(0에서 1, 높을수록 좋음)입니다.

| 모델 | 구간 | Normal 고정 | Lowlight 고정 | DFX live |
|---|---|---:|---:|---:|
| YOLOv8n | 야간 | 0.3922 | 0.4095 | 0.4097 |
| YOLOv8n | 주간 | 0.6270 | 0.6305 | 0.6314 |
| YOLOv8n | 혼합 | 0.4473 | 0.4642 | 0.4636 |

전체 표(SSD-MobileNet 포함)와 표준편차는 연구 저장소의 `comparison.md`에 있습니다.

**읽을 때 반드시 알아 둘 점**

- 세 방식의 차이(예: 야간 0.4095 대 0.4097)는 **학습 시드 사이의 표준편차(약 0.007)보다 훨씬 작습니다.** 이 결과로 "DFX가 고정 ISP보다 정확하다"고 말할 수 없습니다. DFX의 이점으로 확인한 것은 정확도가 아니라 **자원 절감**입니다. 항상 두 ISP를 모두 올려 두는 방식(8월 연구 기록의 Arm2) 대비 DFX는 normal 모드에서 LUT 29.5%, low-light 모드에서 50.8%를 절감했습니다(같은 래퍼와 같은 Vivado 흐름으로 배치·배선한 실측, 2026년 8월 3개 구성 비교). 이 값은 연구 기록의 수치이고, [DFX 튜토리얼](../../DFX_Feature_Tutorials/01-Fabric_only_DFX_flow/README.md)이 새로 측정한 LUT와는 구성과 기준이 다릅니다.
- 시험 프레임은 이전 실험에 쓴 것을 다시 썼습니다. **새로운 장면으로 검증하지 않았습니다.**
- 3시드 표준편차는 독립 데이터셋 반복이 아니라 같은 방법의 반복입니다.
- 사진을 한 장씩 차례로 처리했습니다. **영상이 실시간으로 들어올 때 프레임을 놓치는지, 전력이 얼마나 드는지는 측정하지 않았습니다.**
- 개선의 대부분은 낮과 밤 사진을 함께 학습한 새 AI 모델 덕분이고, 회로를 바꿔 끼우는 방식 자체의 효과는 확인하지 못했습니다.

## 참고

- 연구 전체의 설계 근거와 실험 기록은 비공개로 보관되어 있습니다.
- 이 단계의 데이터는 [AI 튜토리얼](../../AI_Feature_Tutorials/01-Dataset_and_Labels/README.md)의 선정 20장을 쓰는 것이 가장 가깝지만, 연구 기록의 수치는 연구 당시의 200프레임(야간 100, 주간 100)으로 잰 것이라 20장으로는 같은 값이 나오지 않습니다.
