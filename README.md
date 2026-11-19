# DFXISP 튜토리얼

DFX(Dynamic Function eXchange, 동적 부분 재구성) 기반 AI-ISP 연구를 처음부터 끝까지 따라 하며 배우는 튜토리얼 모음입니다. 어두운 장면에서는 저조도용 ISP로, 밝은 장면에서는 일반 ISP로 FPGA 회로 일부를 바꿔 끼우고, 그 영상에서 물체 검출 AI가 사람·자동차·자전거를 찾는 시스템을 다룹니다.

이 저장소의 구성은 AMD의 [Vitis-Tutorials](https://github.com/Xilinx/Vitis-Tutorials)와 [Vivado-Design-Tutorials](https://github.com/Xilinx/Vivado-Design-Tutorials)의 틀(주제별 폴더, 튜토리얼마다 `README.md`와 `reference_files/`)을 참고했습니다. 내용과 그림은 직접 작성한 것입니다.

## 어디서부터 시작하나요

| 하고 싶은 것 | 시작할 곳 |
|---|---|
| 보드 없이 PC에서 ISP 계산만 확인 | [ISP_Feature_Tutorials/01-default_ISP_and_lowlight_ISP](ISP_Feature_Tutorials/01-default_ISP_and_lowlight_ISP/README.md) |
| 회로(HLS) 소스의 C 시뮬레이션과 합성 | [HLS_Feature_Tutorials/01-RM_synthesis_and_csim](HLS_Feature_Tutorials/01-RM_synthesis_and_csim/README.md) |
| 두 ISP를 바꿔 끼우는 DFX 구현 | [DFX_Feature_Tutorials/01-Fabric_only_DFX_flow](DFX_Feature_Tutorials/01-Fabric_only_DFX_flow/README.md) |
| ZCU104 보드와 PetaLinux 기본기 | [Getting_Started/02-PetaLinux_HLS_Accelerator](Getting_Started/02-PetaLinux_HLS_Accelerator/README.md) |
| 데이터셋 준비 | [AI_Feature_Tutorials/01-Dataset_and_Labels](AI_Feature_Tutorials/01-Dataset_and_Labels/README.md) |
| 처음부터 끝까지 한 번에 | [Design_Tutorials/01-DFXISP_End_to_End](Design_Tutorials/01-DFXISP_End_to_End/README.md) |

처음이라면 `Getting_Started` → `ISP_Feature_Tutorials` → `HLS_Feature_Tutorials` → `DFX_Feature_Tutorials` → `Design_Tutorials` 순서를 권합니다.

## 필요한 환경

각 튜토리얼 첫머리에 **PC만으로 되는 부분**과 **FPGA 도구나 보드가 필요한 부분**을 나눠 적었습니다. 아래는 이 튜토리얼을 검증한 환경입니다.

| 항목 | 사양 |
|---|---|
| 컴퓨터 | AMD Ryzen 7, 메모리 14GB, NVIDIA RTX 5060 Laptop GPU 8GB (GPU는 모델 양자화에만 사용) |
| 운영체제 | Ubuntu 22.04.5 LTS |
| FPGA 도구 | Vivado 2024.1, Vitis HLS 2024.1, Vitis 2024.1 (AMD 계정으로 직접 설치) |
| 보드용 리눅스 | PetaLinux 2024.1 |
| 모델 양자화 | Docker, Vitis AI 3.5 이미지 |
| 컴파일러, 언어 | g++ 11.4, Python 3.10 |
| 보드 | AMD ZCU104 (Zynq UltraScale+ `xczu7ev-ffvc1156-2-e`), USB-UART |
| DPU 설정 | `DPUCZDX8G_ISA1_B4096` |
| 목표 클럭 | 5.0ns (200MHz) |

디스크는 Vivado 합성과 PetaLinux 빌드를 하려면 여유 공간 300GB 이상을 권합니다.

## 한계

- 이 튜토리얼이 따라 하게 해 주는 것은 **연구 과정과 측정 방법**이고, 결과 수치가 항상 같게 나온다는 보장은 아닙니다. 보드 실험은 샘플 프레임을 재사용했고 새 장면으로 검증하지 않았습니다. 해석할 때의 조심할 점은 [Design_Tutorials/01-DFXISP_End_to_End](Design_Tutorials/01-DFXISP_End_to_End/README.md)에 있습니다.
- 데이터셋 원본(RAW 영상)은 이 저장소에 넣지 않았습니다. 원 배포처의 이용 약관을 따라 직접 받아야 하고, 프레임 목록과 해시로 같은 영상인지 확인합니다.

## 라이선스

MIT 라이선스입니다([LICENSE](LICENSE)). 다만 아래는 별도입니다.
- AMD의 도구, 문서, 그림은 각 저작권자의 약관을 따르며 이 저장소에 포함하지 않았습니다.
- 데이터셋은 원 배포처의 약관을 따릅니다.
- `Getting_Started/02-PetaLinux_HLS_Accelerator`는 외부 원본 튜토리얼([Xilinx-PetaLinux-Based-FPGA-Acceleration-Design-Tutorial](https://github.com/vandinhtranengg/Xilinx-PetaLinux-Based-FPGA-Acceleration-Design-Tutorial))을 따라 한 학습 기록입니다. 원본에 라이선스 표기가 없어서, 이 폴더의 문서는 원본의 구조와 설명을 옮기지 않고 직접 정리한 내용만 두었습니다.
