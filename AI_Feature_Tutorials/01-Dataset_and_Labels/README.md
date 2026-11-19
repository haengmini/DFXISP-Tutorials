# AI 튜토리얼 1: 데이터셋과 라벨

**소요 시간:** 약 10분 | **필요한 것:** Python 3.10 이상, numpy, rawpy(변환 단계), 원본 RAW 데이터셋 | **FPGA 도구와 보드:** 필요 없음

## 소개

이 연구는 실제 카메라 RAW 영상 두 종류로 실험합니다.

| 데이터셋 | 카메라 | 장면 | 형식 | 블랙/화이트 레벨 |
|---|---|---|---|---|
| LOD(Low-light Object Detection, 이 튜토리얼에서 야간) | Sony RX100 VII | 저녁·야간 | 14비트 `.ARW` | 800 / 16380 |
| PASCALRAW(주간) | Nikon D3200 | 낮 | 12비트 `.NEF` | 0 / 4095 |

두 데이터셋 모두 사람, 자동차, 자전거 세 클래스의 정답 박스(YOLO 형식)가 있습니다.

## 데이터는 이 저장소에 없습니다

원 배포처의 이용 약관을 따라야 해서 원본 영상은 넣지 않았습니다. 대신 **같은 영상을 누구나 고를 수 있도록** 선정 규칙과 각 파일의 해시를 `reference_files/dataset_selection.json`에 두었습니다.

| 데이터셋 | 받는 곳 |
|---|---|
| PASCALRAW | [Stanford Digital Repository](https://purl.stanford.edu/hq050zr7488)(접속 조건에 "추가 라이선스와 이용 제한이 있을 수 있다"고 안내되어 있습니다) |
| LOD | Hong, Wei, Chen, Fu, "Crafting Object Detection in Very Low Light," BMVC 2021 논문의 [프로젝트 페이지](https://kxwei.net/) |

데이터를 쓰기 전에 각 배포처의 라이선스와 인용 조건을 직접 확인하세요. 이 튜토리얼은 두 데이터셋의 재배포 허용 여부를 확인하지 못했습니다.

## 1단계: 선정 20장 확인

선정 규칙은 데이터를 보기 전에 정했습니다. 정답 객체가 1개 이상 있는 프레임만 후보로 두고, 이름순으로 정렬한 뒤 `random.Random(20261119).sample(후보, 10)`으로 야간 10장, 주간 10장을 뽑습니다. 사람이 고른 것이 아닙니다.

받은 데이터셋의 폴더(`LOD_test/raw`, `LOD_test/labels`, `PASCAL_test/raw`, `PASCAL_test/labels`)를 아래에 넘깁니다.

```bash
cd reference_files
python prepare_dataset.py --sel dataset_selection.json \
  --lod-raw <LOD_test/raw> --lod-labels <LOD_test/labels> \
  --pascal-raw <PASCAL_test/raw> --pascal-labels <PASCAL_test/labels> --out work
```

각 파일의 SHA256과 정답 객체 수를 선정 목록과 대조합니다. 하나라도 다르면 중단합니다.

```text
OK   night DSC01153 객체 8/8
...
OK   day 2014_004237 객체 6/6
검증 통과
```

기대 결과는 야간 10장(객체 37개)과 주간 10장(객체 20개)이 모두 통과하는 것입니다. 원본 RAW 20장은 약 410MB입니다.

## 2단계: FPGA 입력 형식으로 변환

원본은 20메가픽셀이라 가속기에 그대로 넣을 수 없습니다. `build_hw_dataset.py`가 두 데이터셋을 같은 크기(1368×912, 12비트, RGGB)로 줄입니다. 줄일 때 **평균이 아니라 같은 색 화소를 솎아 내는 방식**을 씁니다. 평균은 저조도 ISP가 하는 묶기(binning)와 같은 연산이라, 검증하려는 효과를 전처리에서 미리 적용하게 되기 때문입니다.

```bash
pip install numpy rawpy
python build_hw_dataset.py --selftest
python build_hw_dataset.py --raw-dir work/night/raw --labels-dir work/night/labels --out hw/night
python build_hw_dataset.py --raw-dir work/day/raw   --labels-dir work/day/labels   --out hw/day
```

### 기대 결과

```text
10 frames -> hw/night  (1368x912, 12-bit)  boxes kept=37 clipped=6 dropped=0 errors=0
10 frames -> hw/day    (1368x912, 12-bit)  boxes kept=20 clipped=4 dropped=0 errors=0
```

프레임마다 `raw_bin`이 정확히 2,495,232바이트(1368×912×2)여야 합니다. 이 결과는 Ubuntu 22.04, Python 3.10, numpy 2.2.6, rawpy 0.27.1에서 확인했습니다.

## 주의: 클래스 번호

| 위치 | 번호 |
|---|---|
| 원본 데이터셋 라벨, 프로젝트 모델 | 0 사람, 1 자동차, 2 자전거 |
| `raw_bin`과 같이 변환된 라벨, 샘플 라벨 | COCO 번호: 0 사람, 1 자전거, 2 자동차 |

이 차이를 맞추지 않고 비교하면 검출이 맞아도 정확도가 크게 낮게 나옵니다(6장 샘플에서 재현율이 0.26으로 나온 적이 있고, 번호를 맞추자 0.70이 됐습니다).
