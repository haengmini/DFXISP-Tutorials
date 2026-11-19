# DFX 튜토리얼 1: 두 ISP를 같은 자리에 바꿔 끼우는 구현 (패브릭 전용)

**소요 시간:** 약 6분 (HLS 합성 약 45초 + Vivado 약 5분) | **필요한 것:** Vitis HLS 2024.1, Vivado 2024.1, 여유 메모리 8GB 이상, 디스크 수 GB | **보드:** 필요 없음

## 소개

DFX(Dynamic Function eXchange)는 FPGA가 동작하는 중에 칩의 한 구역만 다른 회로로 바꿔 끼우는 기술입니다. 이 튜토리얼은 아래 구조를 만듭니다.

```text
정적 영역(static)                       재구성 가능 영역(RP, 한 칸)
  고정된 회로, 항상 동작         <->      RM 0: 일반 ISP   |   RM 1: 저조도 ISP
                                          (한 번에 하나만 들어간다)
```

**패브릭 전용**이라는 것은 이 단계가 칩 안의 회로 구성까지만 다루고, 보드 부팅이나 DPU(AI 가속기)와 연결하지는 않는다는 뜻입니다. 보드 통합은 다음 단계(Design Tutorials)에서 합니다.

## 따라 하기

[HLS 튜토리얼](../../HLS_Feature_Tutorials/01-RM_synthesis_and_csim/README.md)에서 두 RM을 Verilog로 내보냈다고 가정합니다. 결과가 `/tmp/hls_dfxisp/dfxisp_accel/` 아래에 있어야 합니다.

```bash
source /tools/Xilinx/Vivado/2024.1/settings64.sh
export DFX_WORK_ROOT=$PWD/dfx_work
export DFX_HLS_ROOT=/tmp/hls_dfxisp/dfxisp_accel
cd reference_files/scripts
vivado -mode batch -source dfx_flow.tcl          # 1: RM 합성 2개, 정적 래퍼 생성, 일반 ISP 구현
vivado -mode batch -source dfx_flow_config2.tcl  # 2: 정적 영역 고정, 저조도 ISP 구현, pr_verify
vivado -mode batch -source write_bitstreams.tcl  # 3: 전체 비트스트림 1개와 부분 비트스트림 2개
```

스크립트가 하는 일은 다음과 같습니다.

1. 두 RM을 각각 단독으로(out-of-context) 합성하고, 포트만 남긴 껍데기(stub)를 만듭니다.
2. 파이썬 생성기가 두 껍데기를 읽어 정적 영역 최상위(`dfx_static_top.v`)를 만듭니다. 실제 칩 입출력은 클럭과 리셋만 노출합니다.
3. RP 자리(`u_rp`)에 `HD.RECONFIGURABLE`을 지정하고, 칩 위의 구역(pblock)을 `CLOCKREGION_X1Y0:CLOCKREGION_X2Y0`으로 잡습니다.
4. 구성 1(일반 ISP)을 배치·배선하고 저장합니다.
5. 구성 1에서 정적 영역만 남기고(`update_design -black_box`) 배선까지 고정(`lock_design -level routing`)한 뒤, 저조도 ISP를 넣어 구성 2를 배치·배선합니다.
6. `pr_verify`로 두 구성의 정적 영역이 같은지 검사합니다.
7. 이 단계의 칩 입출력 DRC 두 개(`NSTD-1`, `UCIO-1`)만 경고로 낮추고 비트스트림을 만듭니다. 입출력을 연결하지 않은 패브릭 전용 설계라서 그렇습니다.

## 기대 결과

아래는 Vivado 2024.1(빌드 5076996)에서 이 튜토리얼 그대로 실행해 확인한 값입니다. 전체 실행 시간은 343초였습니다.

| 항목 | 구성 1 (일반 ISP) | 구성 2 (저조도 ISP) |
|---|---:|---:|
| 최악 슬랙(WNS, 5.0ns) | +0.813 ns | +2.224 ns |
| 유지 슬랙(WHS) | +0.016 ns | +0.005 ns |
| CLB LUT | 2,630 | 1,843 |
| CLB 레지스터 | 2,920 | 2,330 |
| Block RAM 타일 | 1.5 | 3.5 |

`pr_verify`는 두 구성이 **호환**이라고 판정합니다. 비교한 정적 타일 29,573개, partition pin 3개, 정적 셀 91개, 정적 배선 노드 89개입니다.

| 비트스트림 | 바이트 |
|---|---:|
| `config1_full_final.bit` (전체) | 19,311,211 |
| `rm_normal_partial_final.bit` (일반 ISP 부분) | 1,447,424 |
| `rm_lowlight_partial_final.bit` (저조도 ISP 부분) | 1,447,424 |

두 부분 비트스트림의 크기가 같은 것이 정상입니다. 같은 구역을 덮어쓰기 때문입니다.

같은 환경에서 두 번 실행했을 때 WNS, LUT, BRAM, 비트스트림 **크기**는 모두 같았습니다. 비트스트림 파일의 **해시는 달랐습니다.** 파일 머리글에 생성 날짜와 시각이 들어가서 3~4바이트가 다르기 때문입니다. 설계 내용의 동일성은 해시가 아니라 `pr_verify`와 크기로 확인하세요.

## 읽는 법

- 이 LUT 수치는 **전체 설계(정적 영역 포함) 기준**입니다. 저조도 ISP의 LUT가 일반 ISP보다 적은 것은 이 단계의 구현 결과이며, HLS 추정(일반 5,202, 저조도 4,204)과 방향은 같지만 수치는 다릅니다.
- WNS와 LUT 값은 Vivado 버전, 배치 난수에 따라 달라질 수 있습니다. 같은 환경에서는 같게 나왔습니다.
- 같은 스크립트를 2026년 8월에 실행한 연구 기록과 비교하면 WNS, BRAM, 비트스트림 크기, `pr_verify` 결과가 같았습니다. LUT는 연구 기록의 구성 1 2,630, 구성 2 1,843과 같습니다.

## 파일

| 경로 | 내용 |
|---|---|
| `reference_files/scripts/` | `dfx_flow.tcl`, `dfx_flow_config2.tcl`, `write_bitstreams.tcl`, 정적 래퍼 생성기 등 |
| `reference_files/rtl/` | 체커 히스테리시스(`checker_hysteresis.v`), DFX 컨트롤러 어댑터, 시험용 테스트벤치 |
| [checker_hysteresis.md](checker_hysteresis.md) | 장면 판단 결과가 흔들리지 않게 하는 슈미트 밴드(진입 64%, 이탈 60%) 설계 |
| [dfxc_adapter.md](dfxc_adapter.md) | AMD DFX Controller IP와 연결하는 어댑터 설계 |

## 다음 단계

[Design_Tutorials/01-DFXISP_End_to_End](../../Design_Tutorials/01-DFXISP_End_to_End/README.md)에서 이 구조를 보드와 DPU에 통합한 연구 전체를 따라갑니다.
