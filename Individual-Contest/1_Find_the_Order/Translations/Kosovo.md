# Gjeni Rendin

- **Kufiri kohor:** 10 minuta
- **Mjedisi:** një GPU (≈16 GB VRAM), pa internet
- **Madhësia e zgjidhjes:** `solution.ipynb` ≤ 1 MB
- **Hapësira ruajtëse:** 5 GB 

## Problemi

Ju jepen dialogë të folur në anglisht ndërmjet dy pjesëmarrësve, *Folësi A* dhe *Folësi B*. Çdo dialog është segmentuar në radhë të folësve, ku çdo radhë përmban të folur vetëm nga një folës. Çdo radhë ruhet si një audio file i veçantë `.wav`, prandaj një dialog i plotë përfaqësohet nga një bashkësi me `.wav` files, një për çdo radhë. 

Fatkeqësisht, radhët janë përzier rastësisht, prandaj biseda nuk ka më kuptim. Në emrin e file `chunk_{k}.wav`, `k` i referohet segmentit të k-të në bashkësinë e përzier, jo radhës së k-të në dialogun origjinal.

**‼️ Detyra juaj është të rindërtoni rendin kronologjik origjinal të bisedës.**

![Gjeni rendin](../find_the_order.jpg)

---

## Dataset

Çdo dialog përmban  `n` audio files të emërtuar `chunk_0.wav`, `chunk_1.wav`, …, `chunk_{n-1}.wav`. Segmentet janë radhë individuale. Emrat e files përkojnë vetëm me rendin e përzier. Ata nuk tregojnë se ku i përket një segment në bisedën origjinale. Çdo dialog ka 7–20 segmente, mono, 44.1 kHz (mund t'i
rimostrëzoni).

**`prefix.json` përmban indekset e emrave të files të dy segmenteve të para në çdo dialog.** Kjo identifikon fillimin e vërtetë të dialogut dhe eliminon paqartësinë ndërmjet leximit të bisedës përpara ose prapa.

Për shembull: `11: [7, 12]` do të thotë se radha e parë dhe e dytë e dialogut 11 janë përkatësisht `chunk_7.wav` dhe `chunk_12.wav`.

### Çfarë merrni

Ju merrni **dy folderë me format identik**:

| Folderi | Dialogët | `answers.json`? | Përdoreni për të |
|--------|-----------|-----------------|-----------|
| `dataset/train/` | 1,288 | ✅ përfshihet | trajnuar / bërë fine-tuning të modelit tuaj |
| `dataset/test_public/`  | 100   | ✅ përfshihet | ekzekutuar pipeline-in tuaj dhe llogaritur vetë rezultatin lokalisht |

Gjatë vlerësimit, folderi juaj `dataset/test_public/` zëvendësohet në mënyrë transparente me
një `hidden evaluation set` (`test_leaderboard_a` për tabelën publike të renditjes dhe `test_leaderboard_b` për tabelën përfundimtare të renditjes) — këto kanë të njëjtën madhësi dhe format si `dataset/test_public/`, por pa `answers.json`.

Notebook-u juaj ekzekutohet përsëri me ato të dhëna dhe file `answers.json` që ai prodhon përdoret për vlerësim. Dialogët e testimit të mbajtur veçmas vijnë nga e njëjta shpërndarje si `train`, prandaj rezultati juaj lokal `test_public` është një parashikim i mirë.

### Struktura e direktorive

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

## Output

Për çdo dialog, përcaktoni rendin kronologjik origjinal të audio segmenteve të tij. Parashikimi juaj duhet të jetë një permutacion `P` i `{0, 1, …, n−1}`, ku `P[i]` është pozicioni kronologjik i parashikuar i `chunk_i.wav` (0 = i pari).

Output file i juaj `answers.json` duhet të lidhë çdo ID dialogu me permutacionin e tij të parashikuar:

```json
{
  "17": [2, 0, 1],
  "42": [0, 1],
  "108": [3, 1, 0, 4, 2, 5]
}
```

### Shembull

Një dialog ka 3 segmente të përziera `chunk_0, chunk_1, chunk_2`:

| segmenti i përzier | përmbajtja e folur | pozicioni i vërtetë (renditja) |
|----------------|----------------|----------------------|
| `chunk_0.wav` | *"No worries — I'll send you the notes afterwards."* | 2 (i fundit) |
| `chunk_1.wav` | *"Hey, are you coming to the three o'clock meeting?"* | 0 (i pari) |
| `chunk_2.wav` | *"I can't — I've got a dentist appointment then."* | 1 |

Rendi i vërtetë është **chunk_1 → chunk_2 → chunk_0**, prandaj `P = [2, 0, 1]`, dhe `prefix.json` përmban `[1, 2]`.

⚠️ **P duhet të jetë një permutacion i mirëfilltë:** gjatësi n, i indeksuar nga 0, çdo vlerë saktësisht një herë. Vlerat e përsëritura, vlerat që mungojnë ose elementet jashtë intervalit (p.sh. të indeksuara nga 1) marrin rezultat 0 për atë dialog, njësoj si një dialog që mungon nga file. Një file me format të gabuar ose që nuk është JSON refuzohet.

## Vlerësimi

Vlerësimi për këtë detyrë është **saktësia e renditjes në çifte**. Ai kontrollon çdo çift segmentesh dhe pyet: _cili nga të dy duhet të vijë i pari?_ Një çift është i saktë nëse parashikimi juaj jep të njëjtën përgjigje si renditja e vërtetë. Për një dialog me `n` segmente kemi $$M = n(n-1)/2$$ çifte; le të jetë `I` numri i inversioneve — çifte të renditura ndryshe nga renditja e vërtetë:

$$\text{score} = 1 - \frac{I}{M} \in [0, 1]$$

ℹ️ **Rezultati përfundimtar është mesatarja e rezultateve për dialog mbi të gjithë
dialogët në ndarje.**

## Modelet e lejuara

Për ta zgjidhur këtë detyrë, si gjatë trajnimit, ashtu edhe gjatë vlerësimit, mund të përdorni vetëm modelet e mëposhtme të paratrajnuara. Të gjitha këto modele janë tashmë të shkarkuara dhe të disponueshme në mjedis. Mund të shihni shembuj të përdorimit të tyre në notebook-un baseline `solution.ipynb`. Kini parasysh se nuk mund të përdorni asnjë model tjetër dhe programi juaj nuk ka qasje në internet.

- **Përfaqësimet e të folurit:** **wav2vec 2.0**. **Whisper encoder** mund të përdoret gjithashtu si nxjerrës veçorish.
[Karta e modelit wav2vec](https://yastatic.net/s3/contest/ioai/1/01_facebook_wav2vec2-base-960h_MODEL_CARD.html)

- **Njohja automatike e të folurit (ASR):** **OpenAI Whisper** (çfarëdo madhësie).
[Karta e modelit Whisper](https://yastatic.net/s3/contest/ioai/1/03_openai_whisper-small_MODEL_CARD.html)
- **Modeli gjuhësor:** **Qwen2.5-0.5B**, i cili mund të përdoret ose zero-shot, ose me fine-tuning në ndarjen e dhënë `train`.
[Karta e modelit Qwen](https://yastatic.net/s3/contest/ioai/1/02_Qwen_Qwen2.5-0.5B_MODEL_CARD.html)
Kini parasysh se kufiri prej 10 minutash duhet të përfshijë çdo trajnim ose fine-tuning që bëni gjatë vlerësimit, plus inferencën në bashkësinë e vlerësimit.

## Si të dorëzoni

- Hapni `solution.ipynb` dhe ekzekutoni të gjitha qelizat. Konfirmoni se ai shkruan `answers.json` në direktorinë e punës me një permutacion për çdo dialog në `dataset/test_public/` (100 dialogë). Gjatë vlerësimit, notebook-u riekzekutohet në bashkësinë e fshehur të testimit dhe vlerësohet `answers.json` që ai prodhon atje.
- Përmirësojeni zgjidhjen nëse dëshironi — ose mos e bëni; baseline-i vet e validon pipeline-in.
- Hapni Git tab në shiritin anësor të majtë të JupyterLab.
- Kryeni **Stage** për `solution.ipynb` (ikona + pranë tij).
- Shkruani një mesazh commit-i dhe klikoni **Commit**.
- Klikoni renë me shigjetë lart për të kryer push.
- Kthehuni në këtë faqe të Garës dhe klikoni **Submit**.

Dorëzoni saktësisht një file, të emërtuar `solution.ipynb`.
