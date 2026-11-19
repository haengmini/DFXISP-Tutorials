# ISP 튜토리얼 1: default_ISP와 lowlight_ISP

**소요 시간:** 5분 이내 | **필요한 것:** PC, g++(C++17), make, Python 3.10 이상, numpy | **FPGA 도구와 보드:** 필요 없음

## 소개

ISP는 카메라 센서가 낸 원본 데이터(RAW)를 사람이 보는 컬러 영상으로 바꾸는 처리입니다. 이 튜토리얼은 연구에서 쓰는 두 ISP를 정수 연산으로 구현한 C++ 코드와, 같은 계산을 Python으로 다시 구현한 코드가 **한 픽셀도 다르지 않게 일치하는지** 확인합니다.

| ISP | 쓰임 | 처리 순서 |
|---|---|---|
| `default_ISP` | 밝은 장면 | 블랙 레벨 보정 → 게인 → 디모자이킹 → 자동 화이트 밸런스 → 색 보정 행렬 → 양자화 → 감마 |
| `lowlight_ISP` | 어두운 장면 | 2x2 묶기(binning) → 블랙 레벨 보정 → 노출 게인 → 색 보정 행렬 → 톤 변환 |

설계 이유와 상수의 근거는 [default_isp.md](default_isp.md), [lowlight_isp.md](lowlight_isp.md)에 있습니다.

## 따라 하기

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
make test
```

`make test`는 세 가지를 차례로 확인합니다.

1. **C++ 골든 비교.** 정수 C++ ISP가 미리 만들어 둔 정답 값(골든 벡터)과 일치하는지 봅니다.
2. **Python 대조.** 큰 영상을 빠르게 처리하려고 따로 만든 Python 구현이 C++ 기준 구현과 비트 단위로 일치하는지 40회 무작위 시험으로 봅니다.
3. **골든 재생성.** Python이 새로 만든 골든 벡터가 저장소의 CSV와 바이트 단위로 같은지 봅니다.

## 기대 결과

```text
default_ISP golden vector compare passed (528 pixels)
lowlight_ISP golden vector compare passed (147 pixels)
[verify_new_arm_pipelines] PASS: 40 trials, 15966 channel samples, vectorised proxies bit-exact ...
```

이 결과는 Ubuntu 22.04, g++ 11.4, Python 3.10, numpy 환경에서 확인했습니다.

## 폴더 구성

| 경로 | 내용 |
|---|---|
| `reference_files/cpp/` | 정수 C++ ISP 소스, 시험 코드, 골든 벡터 CSV |
| `reference_files/python/` | Python 기준 구현, 골든 생성기, 장면 밝기 판단기(`checker.py`) |
| `Makefile` | `make test` 정의 |

## 다음 단계

[HLS_Feature_Tutorials/01-RM_synthesis_and_csim](../../HLS_Feature_Tutorials/01-RM_synthesis_and_csim/README.md)에서 같은 ISP를 FPGA 회로(HLS)로 합성합니다.
