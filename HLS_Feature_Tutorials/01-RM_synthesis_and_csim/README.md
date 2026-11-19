# HLS 튜토리얼 1: 재구성 모듈(RM) 합성과 C 시뮬레이션

**소요 시간:** C 시뮬레이션 1분, 합성 약 1분(RM 2개) | **필요한 것:** g++(C++17), make. 합성은 Vitis HLS 2024.1 | **보드:** 필요 없음

## 소개

HLS(High-Level Synthesis)는 C++ 코드를 FPGA 회로로 바꿔 줍니다. 이 연구는 장면에 따라 칩 일부를 바꿔 끼우므로, 바꿔 끼울 회로를 **재구성 모듈(RM, Reconfigurable Module)** 두 개로 만듭니다.

| RM(HLS 탑 함수) | 쓰임 |
|---|---|
| `rm_normal_tone_top` | 밝은 장면용 전체 ISP |
| `rm_low_light_tone_top` | 어두운 장면용 전체 ISP |

DFX에서는 같은 자리에 들어가는 RM이 **입출력 포트가 완전히 같아야** 합니다. 두 RM은 110개 포트가 모두 같게 설계되어 있습니다.

## 1단계: C 시뮬레이션 (PC만으로)

```bash
make csim
```

회로 소스를 일반 C++로 컴파일해 골든 벡터와 비교합니다.

```text
DFXISP golden vector compare passed (726 pixels)
DFXISP RM golden compare: checked=2816 mismatch=0 cases=20
default_ISP golden vector compare passed (528 pixels)
lowlight_ISP golden vector compare passed (163 pixels)
```

## 2단계: Vitis HLS 합성 (Vitis HLS 2024.1 필요)

RM 하나씩 합성하고 Verilog IP로 내보냅니다. **소스를 평평한 임시 폴더에 복사한 뒤 그곳에서 실행해야 합니다.** 중첩된 프로젝트 경로에서는 `add_files`로 넣은 소스가 누락되어 `undefined symbol` 링크 오류가 납니다.

```bash
source /tools/Xilinx/Vitis_HLS/2024.1/settings64.sh
mkdir -p /tmp/hls_dfxisp/dfxisp_accel
cp reference_files/src/dfxisp_accel.cpp reference_files/include/*.hpp /tmp/hls_dfxisp/dfxisp_accel/
for top in rm_normal_tone_top rm_low_light_tone_top; do
  RM_TOP=$top HLS_FLAT=/tmp/hls_dfxisp/dfxisp_accel vitis_hls -f hls_rm_export.tcl
done
```

`hls_rm_export.tcl`은 이 폴더에 있습니다. 대상은 `xczu7ev-ffvc1156-2-e`, 목표 클럭 5.0ns입니다.

### 기대 결과

| RM | LUT | FF | BRAM_18K | DSP | 추정 Fmax |
|---|---:|---:|---:|---:|---:|
| `rm_normal_tone_top` | 5,202 | 3,797 | 4 | 12 | 273.97MHz |
| `rm_low_light_tone_top` | 4,204 | 3,243 | 8 | 9 | 273.97MHz |

이 값은 Vitis HLS 2024.1(빌드 5069499)에서 합성해 확인했고, 연구 기록과 같았습니다. 합성 시간은 RM마다 약 23초였습니다.

## 주의

- HLS가 만든 RTL을 다른 곳으로 복사할 때 `cp *.v`만 하면 감마 ROM `.dat` 파일이 조용히 빠져 합성 결과가 달라집니다. **`.dat`을 항상 `.v`와 함께 복사하세요.**
- 자원 수치를 비교할 때 **파티션 빌드와 평면(flat) 빌드의 수치를 섞지 마세요.** 같은 넷리스트에서도 약 24% 차이가 났고 원인은 밝히지 못했습니다.

## 다음 단계

[DFX_Feature_Tutorials/01-Fabric_only_DFX_flow](../../DFX_Feature_Tutorials/01-Fabric_only_DFX_flow/README.md)에서 두 RM을 같은 칩 자리에 바꿔 끼우는 구현을 합니다.
