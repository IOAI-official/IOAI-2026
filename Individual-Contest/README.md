# IOAI 2026 — Individual Contest

The Individual Contest is the main competition of the International Olympiad in Artificial Intelligence 2026, held in Astana, Kazakhstan. It ran over two on-site days, with **three tasks per day** and a fresh notebook environment for each task.

The same six tasks were also used for the [GAITE Contest](../GAITE-Contest), which adds per-task hints and is scored on a separate ranking.

## Tasks

### Day 1

| # | Task | Time limit | Summary |
|---|---|---|---|
| 1 | [Find the Order](1_Find_the_Order) | 10 min | Spoken English dialogues are split into one `.wav` per speaker turn and shuffled. Reconstruct the original turn order. |
| 2 | [Robot Chasing](2_Robot_Chasing) | 5 min | Six robots in `6×6` gridworlds, each given a natural-language instruction. Predict the behaviour it describes. |
| 3 | [Potato](3_Potato) | 10 min | A word-guessing game: find a hidden word within 30 turns, given only pairwise "which is semantically closer" comparisons. |

### Day 2

| # | Task | Time limit | Summary |
|---|---|---|---|
| 4 | [Double Agent Dilemma](4_Double_Agent_Dilemma) | 12 min | A ResNet18 and a ViT-Tiny both classify the same images at 100% accuracy. Exploit where the two architectures disagree. |
| 5 | [Ghost of the Machine](5_Ghost_of_Machine) | 10 min | Machine-altered passages have been slipped into an archive of books. Locate the edits. |

Every task ran on **one GPU (≈16 GB VRAM) with no internet access** and 5 GB of storage. Solution size limits are stated in each task's statement.

## What's in each task folder

Every task folder has the same shape:

```
<N>_<Task_Name>/
  statement.md            official English statement (authoritative)
  statement.pdf           rendered English statement
  <figures>               images referenced by the statement
  Translations/           statements reviewed and corrected by team leaders
  AI-Translation/         machine translations, 44 languages — see its README
```

Data, baselines, and reference solutions are not included yet; they will be added later.

Two sets of translations are shipped, and they are **not** equivalent:

- **`Translations/`** — the versions actually handed to contestants. Each delegation's team leader read and corrected their own language. `.md` and `.pdf` per country. These take precedence.
- **`AI-Translation/`** — machine translations into 44 languages (plus the English source), generated automatically and **not** human-verified. Useful for coverage, but they may contain errors. See the README inside any `AI-Translation/` folder.

Translation coverage differs by day: Day 1 tasks have 74 country versions in `Translations/`, Day 2 tasks have 44. English appears as `United-Kingdom` on Day 1 and `ISC` on Day 2.

## Credits

### Task authors

| Task | Proposed by | Developed by |
|---|---|---|
| Find the Order | Nurdaulet Akhanov | Nurdaulet Akhanov |
| Robot Chasing | Salem Lahlou | Anuar Aimoldin · Kamalkhan Artykbayev · Nurdaulet Akhanov |
| Potato | Kirill Fedyanin | Ayana Mussabayeva · Kirill Fedyanin |
| Double Agent Dilemma | Tao Dajiang | Tao Dajiang · Zhuldyz-Zhan Sagimbayev · Kamalkhan Artykbayev |
| Ghost of the Machine | Alexander D'yakonov · Nurdaulet Akhanov | Nurdaulet Akhanov · Kirill Fedyanin |
| IOAI Field | Evgenii Tsymbalov | Evgenii Tsymbalov · Ekaterina Fadeeva · Daniil Kazantsev · Maiya Goloburda · Magauiya Zhussip |

The AI track was prepared by **Abhishek Divekar**, **Magauiya Zhussip**, **Kamalkhan Artykbayev**, and **Temiko Machavariani**.

### Host Scientific Committee

Ayana Mussabayeva · Anuar Aimoldin · Zhuldyz-Zhan Sagimbayev · Kamalkhan Artykbayev · Magauiya Zhussip · Temiko Machavariani · **Nurdaulet Akhanov**

### International Scientific Committee

Anuar Aimoldin · Nurdaulet Akhanov · Alexander D'yakonov · Abhishek Divekar · Kirill Fedyanin · Michael Guerzhoy · Yova Kementchedjhieva · Roy Ka-Wei Lee · Muhammad Rizki Maulana · Maxim Panov · Anna Piunova · Ali Sharifi-Zarchi · Paulina Tomaszewska · Evgenii Tsymbalov · Zijie Zheng

### International Jury

Nurdaulet Akhanov · Abhishek Divekar · Kirill Fedyanin · **Yova Kementchedjhieva** · Roy Ka-Wei Lee · Muhammad Rizki Maulana · Maxim Panov · Anna Piunova · Evgenii Tsymbalov · Zijie Zheng

### Special thanks

Aleksandr Domoratskiy · Damir Ismagilov · Tatiana Kolinkova · Davlet Sibgatullin · Nikita Sychev — and all members of the **Yandex Contest Platform Team**.

**АО НИТ**, for providing GPUs.

And thanks to the **delegation team leaders**, who translated and reviewed the statements in `Translations/` overnight between contest days.

Materials for **IOAI Field** (Day 2, task 6) are not published in this repository.
