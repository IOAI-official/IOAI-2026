# 순서 찾기

- **제한 시간:** 10분
- **환경:** GPU 1개(≈16 GB VRAM), 인터넷 없음
- **솔루션 크기:** `solution.ipynb` ≤ 1 MB
- **저장 공간:** 5 GB

## 문제

두 참가자 *Speaker A* 와 *Speaker B* 사이의 영어 음성 대화가 주어집니다. 각 대화는 화자 턴(turn) 단위로 분할되어 있으며, 각 턴은 오직 한 화자의 발화만 포함합니다. 모든 턴은 별개의 `.wav` 오디오 파일로 저장되어 있으므로, 하나의 완전한 대화는 각 턴에 대응하는 `.wav` 파일들의 집합으로 표현됩니다.

안타깝게도 턴들이 무작위로 섞여 있어서 대화가 더 이상 의미가 통하지 않습니다. 파일 이름 `chunk_{k}.wav`에서 `k`는 섞인 집합에서의 k번째 청크를 의미하며, 원래 대화에서의 k번째 턴을 의미하지 않습니다.

**‼️ 여러분의 과제는 대화의 원래 시간 순서를 복원하는 것입니다.**

![순서 찾기](../../find_the_order.jpg)

---

## 데이터셋

각 대화는 `chunk_0.wav`, `chunk_1.wav`, …, `chunk_{n-1}.wav` 이라는 이름의 `n` 오디오 파일들을 포함합니다. 청크는 개별 턴입니다. 파일 이름은 섞인 순서에만 대응합니다. 파일 이름은 해당 청크가 원래 대화에서 어디에 위치하는지를 나타내지 않습니다. 각 대화는 7–20개의 청크로 이루어지며, 모노, 44.1 kHz입니다(리샘플링해도 됩니다).

**`prefix.json`에는 각 대화의 처음 두 청크의 파일 이름 인덱스가 들어 있습니다.** 이는 대화의 진짜 시작점을 알려 주며, 대화를 앞에서 뒤로 읽을지 뒤에서 앞으로 읽을지에 대한 모호성을 제거합니다.

예를 들어, `11: [7, 12]`은 11번 대화의 첫 번째 턴과 두 번째 턴이 각각 `chunk_7.wav`과 `chunk_12.wav`임을 의미합니다.

### 제공되는 것

**형식이 동일한 두 개의 폴더**를 받습니다:

| 폴더 | 대화 수 | `answers.json`? | 용도 |
|--------|-----------|-----------------|-----------|
| `dataset/train/` | 1,288 | ✅ 포함 | 모델 학습 / 파인튜닝 |
| `dataset/test_public/`  | 100   | ✅ 포함 | 파이프라인 실행 및 로컬 자체 채점 |

채점 시에는 여러분의 `dataset/test_public/` 폴더가 투명하게 `hidden evaluation set`(공개 리더보드용은 `test_leaderboard_a`, 최종 리더보드용은 `test_leaderboard_b`)로 대체됩니다 — 이들은 `dataset/test_public/`와 크기 및 형식이 동일하지만 `answers.json`가 없습니다.

여러분의 노트북이 해당 데이터에 대해 다시 실행되며, 그때 생성된 `answers.json` 파일이 채점에 사용됩니다. 비공개 테스트 대화들은 `train`와 동일한 분포에서 추출되었으므로, 로컬 `test_public` 점수는 충실한 예측 지표가 됩니다.

### 디렉터리 구조

```bash
dataset/train/
    prefix.json  # {dialogue_id: [first_idx, second_idx]} filename index 
    answers.json  # {dialogue_id: P}  ground-truth order (rank convention)
    <dialogue_id>/
        chunk_0.wav
        ...
        chunk_{n-1}.wav

dataset/test_public/
    prefix.json
    answers.json     # present only in the development copy
    <dialogue_id>/
        chunk_0.wav
        ...
        chunk_{n-1}.wav
```

---

## 출력

각 대화에 대해 오디오 청크들의 원래 시간 순서를 결정하십시오. 여러분의 예측은 `{0, 1, …, n−1}`의 순열 `P`이어야 하며, 여기서 `P[i]`는 `chunk_i.wav`의 예측된 시간 순서상 위치입니다(0 = 첫 번째).

출력 파일 `answers.json`는 각 대화 ID를 예측된 순열에 매핑해야 합니다:

```json
{
  "17": [2, 0, 1],
  "42": [0, 1],
  "108": [3, 1, 0, 4, 2, 5]
}
```

### 예시

어떤 대화에 섞인 청크 3개 `chunk_0, chunk_1, chunk_2`가 있습니다:

| 섞인 청크 | 발화 내용 | 실제 위치(순위) |
|----------------|----------------|----------------------|
| `chunk_0.wav` | *"No worries — I'll send you the notes afterwards."* | 2 (마지막) |
| `chunk_1.wav` | *"Hey, are you coming to the three o'clock meeting?"* | 0 (첫 번째) |
| `chunk_2.wav` | *"I can't — I've got a dentist appointment then."* | 1 |

실제 순서는 **chunk_1 → chunk_2 → chunk_0**이므로 `P = [2, 0, 1]`이며, `prefix.json`는 `[1, 2]`를 담습니다.

⚠️ **P는 진정한 순열이어야 합니다:** 길이 n, 0부터 시작하는 인덱스, 각 값이 정확히 한 번씩 등장. 중복, 누락된 값, 범위를 벗어난 항목(예: 1부터 시작하는 인덱스)이 있으면 해당 대화는 0점이며, 파일에서 누락된 대화도 0점입니다. 형식이 잘못되었거나 JSON이 아닌 파일은 거부됩니다.

## 채점

이 과제의 채점 기준은 **쌍별 순서 정확도(pairwise ordering accuracy)**입니다. 모든 청크 쌍을 확인하여 다음을 묻습니다: _둘 중 어느 것이 먼저 와야 하는가?_ 여러분의 예측이 정답(ground truth)과 같은 답을 준다면 그 쌍은 정답입니다. 청크가 `n`개인 대화에는 $$M = n(n-1)/2$$개의 쌍이 있습니다. `I`를 역전(inversion)의 수, 즉 정답과 다르게 정렬된 쌍의 수라고 하면:

$$\text{score} = 1 - \frac{I}{M} \in [0, 1]$$

ℹ️ **최종 점수는 해당 스플릿의 모든 대화에 대한 대화별 점수의 평균입니다.**

## 허용 모델

이 과제를 해결하기 위해 학습과 평가 모두에서 다음의 사전학습 모델만 사용할 수 있습니다. 이 모델들은 모두 이미 환경에 다운로드되어 사용 가능합니다. 사용 예시는 베이스라인 노트북 `solution.ipynb`에서 확인할 수 있습니다. 다른 모델은 사용할 수 없으며, 프로그램은 인터넷에 접근할 수 없음을 유의하십시오.

- **음성 표현(speech representations):** **wav2vec 2.0**. **Whisper encoder** 또한 피처 추출기로 사용할 수 있습니다.
[wav2vec model card](https://yastatic.net/s3/contest/ioai/1/01_facebook_wav2vec2-base-960h_MODEL_CARD.html)

- **자동 음성 인식(ASR):** **OpenAI Whisper**(임의의 크기).
[Whisper model card](https://yastatic.net/s3/contest/ioai/1/03_openai_whisper-small_MODEL_CARD.html)
- **언어 모델:** **Qwen2.5-0.5B**. 제로샷으로 사용하거나 제공된 `train` 스플릿에서 파인튜닝하여 사용할 수 있습니다.
[Qwen model card](https://yastatic.net/s3/contest/ioai/1/02_Qwen_Qwen2.5-0.5B_MODEL_CARD.html)
채점 시 수행하는 모든 학습 또는 파인튜닝과 평가 세트에 대한 추론이 10분 제한 안에 모두 포함되어야 함을 유의하십시오.

## 제출 방법

- `solution.ipynb`을 열고 모든 셀을 실행하십시오. 작업 디렉터리에 `answers.json`가 작성되며 `dataset/test_public/`의 모든 대화(100개 대화)에 대한 순열이 포함되어 있는지 확인하십시오. 채점 시에는 노트북이 비공개 테스트 세트에 대해 다시 실행되고, 거기서 생성된 `answers.json`가 채점됩니다.
- 원한다면 솔루션을 개선하십시오 — 하지 않아도 됩니다. 베이스라인만으로도 파이프라인이 검증됩니다.
- JupyterLab 왼쪽 사이드바에서 Git 탭을 여십시오.
- `solution.ipynb`를 **스테이지(Stage)** 하십시오(옆의 + 아이콘).
- 커밋 메시지를 입력하고 **Commit**을 클릭하십시오.
- 위쪽 화살표가 있는 구름 아이콘을 클릭하여 푸시하십시오.
- 이 Contest 페이지로 돌아와 **Submit**을 클릭하십시오.

정확히 한 개의 파일, 이름이 `solution.ipynb`인 파일을 제출하십시오.
