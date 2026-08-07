# 이중 스파이 딜레마 (Double Agent Dilemma)

- **제한 시간:** 12분.
- **저장 공간:** 5 GB
- **환경:** GPU 1개(≈16 GB VRAM), 인터넷 없음
- **솔루션 크기:** `solution.ipynb` ≤ 1 MB
- **베이스라인 점수:** 0 
- **학술위원회 점수:** 96.99 

아스타나의 국립 AI 센터에서 두 개의 컴퓨터 모델 — Model R(ResNet-18)과 Model V(ViT-Tiny) — 가 사진을 분석하고 있습니다. 현재 두 모델은 모두 완벽하게 작동하여 100% 정확도를 기록하고 있으며, 모든 이미지에 대해 서로 일치된 판단을 내리고 있습니다. 이 모델들의 똑똑한 "두뇌"가 실제로 얼마나 다른지 시험하기 위해, 수석 과학자는 여러분에게 다음과 같은 과제를 제시합니다. 각 사진에 거의 눈에 띄지 않는 아주 작은 픽셀 변화를 가하여 Model R과 Model V가 완전히 다른 판단을 내리도록 만드십시오.

![img](../../dilemma.jpg)

## 1. 과제

사전 학습된 두 개의 이미지 분류기(classifier)가 동일한 이미지를 봅니다. 본 과제에서 제공되는 이미지들에 대해 두 분류기는 모두 100% 정확도로 동작합니다.

- **Model R**: `torchvision.models.resnet18` (CNN, ResNet18).
- **Model V**: `timm`의 `vit_tiny_patch16_224` (Transformer, ViT-Tiny).

여러분의 과제는 두 모델이 서로 다른 판단을 내리도록 각 이미지에 대해 작은 변화("섭동(perturbation)")를 만드는 것입니다. 모든 이미지에 대해 **서로 다른 두 개의** 섭동을 만들어야 합니다.

- **Type A**: 이를 추가한 후 Model R은 여전히 이미지를 올바르게 분류하지만, Model V는 잘못 분류합니다.
- **Type B**: 이를 추가한 후 Model V는 여전히 이미지를 올바르게 분류하지만, Model R은 잘못 분류합니다.

각 섭동은 알아채기 어려울 만큼 충분히 *작아야* 합니다. 섭동이 작을수록 점수가 높습니다(5절 참조). 섭동은 원본 이미지에 픽셀 수준에서 직접 적용됩니다.

## 2. 공개 데이터

과제와 함께 이미지 집합이 제공되며, 두 개의 split — `train`(이미지 100장) 및
`test_public`(이미지 100장) — 으로 구성되어 있고, 각 split에는 해상도가 서로 다른 이미지들이 포함되어 있습니다. 모든 이미지는 ImageNet-1K의 1000개 클래스에서 가져온 것이며, Model R과 Model V는 두 split 모두에서 100% 정확도를 달성합니다.

다음 파일들이 제공됩니다.

```text
train/images/*.png         # 100 images in PNG format
train/labels.json          # maps each image index to its correct class
test_public/images/*.png   # 100 images in PNG format
test_public/labels.json    # maps each image index to its correct class
```

채점 시에는 여러분의 `dataset/test_public/` 폴더가 공식 채점을 위해 두 개의 비공개 이미지 집합(`test_leaderboard_a` 및 `test_leaderboard_b`)으로 투명하게 대체됩니다. 각 집합은 PNG 형식의 **이미지 100장**과 레이블 파일을 포함합니다. 

**참고: 본 과제에서는 테스트 데이터셋의 레이블에 접근할 수 있습니다.**

## 3. 출력 형식

각 이미지에 대해 두 개의 파일을 생성해야 합니다.

```text
{index}_a.pt   # Type A perturbation
{index}_b.pt   # Type B perturbation
```

- `{index}` (`0`, `1`, `2`, ...)는 데이터셋에 있는 이미지의 이름과 일치합니다.
- 각 파일은 `torch.save`으로 저장된 단일 텐서입니다. 그 shape는 반드시`3 x H x W`이어야 하며, 여기서 `H`와 `W`은 해당 이미지의 **원본** 해상도와 일치해야 합니다(`224 x 224`이 아님).
- 코드는 단 하나의 ZIP 파일, 즉 `submission.zip`만 생성해야 합니다. 모든 `.pt` 파일을 ZIP 아카이브의 최상위 레벨에 두고, 이를 감싸는 폴더나 하위 디렉터리가 없도록 하십시오. 

```text
submission.zip
├── 0_a.pt
├── 0_b.pt
└── 1_a.pt
└── ...
```

출력 형식에 문제가 있으면 노트북이 알려줍니다.

## 4. 제약 조건

- **모델:** 반드시 `torchvision.models.resnet18(pretrained=True)`과 `timm.create_model('vit_tiny_patch16_224', pretrained=True)`을 사용해야 합니다. 다른 사전 학습 모델은 허용되지 않습니다.
- **변환 파이프라인(평가 시 강제 적용):** `Resize(256) → CenterCrop(224) →
  Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])`. See Section 3 of `baseline.ipynb` 에서 자세한 내용을 확인하십시오. 
- **섭동 해상도:** 반드시 **원본** 원시 이미지 해상도와 일치해야 합니다(224×224가 아님). 텐서는 변환 파이프라인 *이전에* 원시 이미지에 더해집니다.
- **출력 형식:** `.pt` 파일만 허용됩니다 — PNG/JPG는 안 됩니다. 텐서는 원시 이미지에 더해지며, 전처리 전에 픽셀 값은 `[0, 1]`로 클리핑됩니다.
- **파일 이름:** 평면 목록 형태이며, 엄격히 `{index}_a.pt` / `{index}_b.pt` 형식을 따릅니다. zip 내부에 하위 디렉터리가 없어야 합니다.
- **라이브러리:** `torch`, `torchvision`, `timm`. 

## 5. 채점

최종 점수는 다음과 같이 계산됩니다. `M`을 해당 split의 이미지 수, $Score_A$을 성공한 Type A 섭동의 수, $Score_B$를 성공한 Type B 섭동의 수라고 하겠습니다.
$$
S_{final} = \frac{Score_A + Score_B}{2M} \times PF
$$

PF는 노름(norm)이 큰 섭동에 벌점을 주고 성능의 상한 근처에서 매우 민감하도록 설계된 함수입니다. 그 값은 0.5에서 1 사이의 범위로 제한됩니다. 전체 구현은 `solution.ipynb`의 8절에서 확인할 수 있습니다. 

![img](../../curves.jpeg)
그림: 벌점 함수의 곡선.

## 6. 제출물 확인

노트북에는 형식 문제가 있을 경우 이를 알려주는 검사가 포함되어 있으며, `solution.ipynb` 노트북의 7절에 있습니다.

## 7. 로컬 테스트

`solution.ipynb`에는 완전하게 동작하는 예제가 들어 있습니다. 이 예제는 공개 데이터, 두 모델, 공식 채점기를 불러오고 제출용 ZIP 파일을 작성합니다. 시작하기 전에 읽어 보십시오.

## 8. 제출 방법

- 변경 사항을 `solution.ipynb`에 저장하십시오.
- JupyterLab 왼쪽 사이드바에서 Git 탭을 여십시오.
- `solution.ipynb`을(를) **Stage** 하십시오(옆에 있는 + 아이콘).
- 커밋 메시지를 입력하고 **Commit**을 클릭하십시오.
- 위쪽 화살표가 있는 구름 아이콘을 클릭하여 푸시하십시오.
- 이 Contest 페이지로 돌아와 **Submit**을 클릭하십시오.

정확히 하나의 파일, 즉 `solution.ipynb`이라는 이름의 파일을 제출하십시오.
