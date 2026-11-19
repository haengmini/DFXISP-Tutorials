# Getting Started 2: PetaLinux로 HLS 가속기를 보드에서 쓰는 기본 흐름

**소요 시간:** 테스트벤치 1분. 보드 실습은 PetaLinux 빌드 포함 수 시간 | **필요한 것:** g++. 보드 실습은 Vivado, Vitis HLS, PetaLinux 2024.1과 ZCU104 | **PC만으로 되는 부분:** 4단계의 C++ 테스트벤치

## 소개

이후 DFXISP 보드 실험은 같은 흐름을 씁니다: **HLS로 회로를 만들고, Vivado에서 칩 전체를 구성하고, PetaLinux로 리눅스를 만들어 SD 카드로 부팅한 뒤, 리눅스 프로그램이 회로를 제어합니다.** 이 흐름을 가장 작은 예제인 행렬 곱셈 가속기(`mmult`)로 먼저 익힙니다.

```text
리눅스 사용자 프로그램 (C++ 또는 Python)
        | mmap()
리눅스 커널 UIO 드라이버
        | AXI-Lite 제어              | DDR 직접 접근
PS (ARM Cortex-A53)  <---->  PL (FPGA: HLS 행렬 곱셈 가속기)
```

| 경로 | 값 |
|---|---|
| 제어(AXI-Lite) | `0xA0000000`, 64KiB |
| 데이터(예약한 물리 DDR) | `0x70000000`, 16MiB |

## 원본 튜토리얼

이 예제는 TRAN VAN DINH의 [Xilinx-PetaLinux-Based-FPGA-Acceleration-Design-Tutorial](https://github.com/vandinhtranengg/Xilinx-PetaLinux-Based-FPGA-Acceleration-Design-Tutorial)을 따라 한 것입니다. **PetaLinux 설치, BSP 준비, 프로젝트 생성, 빌드, SD 카드 부팅의 단계별 절차는 원본을 직접 보세요.** 원본에 라이선스 표기가 없어서 이 저장소에는 원본의 설명을 옮기지 않았고, 이 폴더에는 직접 작성한 소스와 이 안내만 있습니다.

## 진행 순서

1. Vitis HLS 2024.1에서 `reference_files/hls/mmult.cpp`를 합성하고 IP로 패키징합니다. 대상은 `xczu7ev-ffvc1156-2-e`입니다.
2. Vivado에서 ZynqMP PS와 가속기 IP를 연결해 비트스트림과 XSA를 만듭니다.
3. PetaLinux 프로젝트에 XSA를 가져옵니다. 디바이스 트리가 자동 생성됩니다.
4. 사용자 디바이스 트리 오버레이로 가속기를 UIO로 노출하고 DDR 영역을 예약합니다.
5. `reference_files/app`의 C++ 또는 Python 프로그램을 루트 파일 시스템에 포함해 빌드합니다.
6. SD 카드로 부팅해 보드에서 실행하고 CPU 결과와 FPGA 결과가 같은지 확인합니다.

## PC에서 확인하기 (4단계 전 단계)

가속기의 계산 자체는 C++ 테스트벤치로 PC에서 먼저 검증합니다.

```bash
cd reference_files/hls
g++ -std=c++17 -Wno-unknown-pragmas -Wno-unused-label -I. mmult.cpp mmult_tb.cpp -o mmult_tb
./mmult_tb
```

기대 결과는 `TEST PASSED`입니다. Ubuntu 22.04, g++ 11.4에서 확인했습니다.

## 보드 단계의 상태

PetaLinux 빌드와 SD 부팅은 원본 튜토리얼의 절차대로 진행하며, 이 저장소의 확인 범위는 위 테스트벤치까지입니다. 연구 과정에서 같은 흐름으로 보드를 부팅했지만, 이 튜토리얼 문서 기준으로 새로 처음부터 재현해 보지는 않았습니다.

## 다음 단계

[ISP_Feature_Tutorials/01-default_ISP_and_lowlight_ISP](../../ISP_Feature_Tutorials/01-default_ISP_and_lowlight_ISP/README.md)로 넘어가 연구의 ISP를 익힙니다.
