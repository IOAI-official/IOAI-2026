# Atrodi kārtību

- **Laika ierobežojums:** 10 minūtes
- **Vide:** viens GPU (≈16 GB VRAM), bez interneta
- **Risinājuma izmērs:** `solution.ipynb` ≤ 1 MB
- **Krātuve:** 5 GB 

## Uzdevums

Jums ir doti runāti dialogi angļu valodā starp diviem dalībniekiem — *Speaker A* un *Speaker B*. Katrs dialogs ir sadalīts runātāju replikās (turns), un katra replika satur runu tikai no viena runātāja. Katra replika ir saglabāta kā atsevišķs `.wav` audio fails, tāpēc pilnu dialogu attēlo `.wav` failu kopa — pa vienam katrai replikai. 

Diemžēl replikas ir nejauši sajauktas, tāpēc sarunai vairs nav jēgas. Faila nosaukumā `chunk_{k}.wav` `k` apzīmē k-to fragmentu sajauktajā kopā, nevis k-to repliku sākotnējā dialogā.

**‼️ Jūsu uzdevums ir rekonstruēt sarunas sākotnējo hronoloģisko kārtību.**

![Atrodi kārtību](../../find_the_order.jpg)

---

## Datu kopa

Katrs dialogs satur `n` audio failus ar nosaukumiem `chunk_0.wav`, `chunk_1.wav`, …, `chunk_{n-1}.wav`. Fragmenti (chunks) ir atsevišķas replikas. Failu nosaukumi atbilst tikai sajauktajai kārtībai. Tie nenorāda, kur fragments atrodas sākotnējā sarunā. Katram dialogam ir 7–20 fragmenti, mono, 44.1 kHz (jūs varat pārveidot iztveršanas frekvenci).

**`prefix.json` satur pirmo divu fragmentu failu nosaukumu indeksus katrā dialogā.** Tas norāda dialoga īsto sākumu un novērš neviennozīmīgumu starp sarunas lasīšanu uz priekšu vai atmuguriski.

Piemēram: `11: [7, 12]` nozīmē, ka 11. dialoga pirmā un otrā replika ir attiecīgi `chunk_7.wav` un `chunk_12.wav`.

### Ko jūs saņemat

Jūs saņemat **divas mapes identiskā formātā**:

| Mape | Dialogi | `answers.json`? | Izmantojiet to, lai |
|--------|-----------|-----------------|-----------|
| `dataset/train/` | 1,288 | ✅ iekļauts | trenētu / precizētu (fine-tune) savu modeli |
| `dataset/test_public/`  | 100   | ✅ iekļauts | palaistu savu pipeline un lokāli pašnovērtētu rezultātu |

Vērtēšanas laikā jūsu `dataset/test_public/` mape tiek nemanāmi aizstāta ar
`hidden evaluation set` (`test_leaderboard_a` publiskajam līderu sarakstam un `test_leaderboard_b` galīgajam līderu sarakstam) — tām ir tāds pats izmērs un formāts kā `dataset/test_public/`, bet bez `answers.json`.

Jūsu notebook tiek izpildīts vēlreiz uz šiem datiem, un vērtēšanai tiek izmantots `answers.json` fails, ko tas izveido. Atliktie (held-out) testa dialogi ir no tā paša sadalījuma kā `train`, tāpēc jūsu lokālais `test_public` rezultāts ir uzticams priekšskatījums.

### Direktoriju struktūra

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

## Izvade

Katram dialogam nosakiet tā audio fragmentu sākotnējo hronoloģisko kārtību. Jūsu prognozei jābūt `{0, 1, …, n−1}` permutācijai `P`, kur `P[i]` ir prognozētā `chunk_i.wav` hronoloģiskā pozīcija (0 = pirmā).

Jūsu izvades failam `answers.json` katram dialoga ID jāpiekārto tā prognozētā permutācija:

```json
{
  "17": [2, 0, 1],
  "42": [0, 1],
  "108": [3, 1, 0, 4, 2, 5]
}
```

### Piemērs

Dialogam ir 3 sajaukti fragmenti `chunk_0, chunk_1, chunk_2`:

| sajauktais fragments | runas saturs | patiesā pozīcija (rangs) |
|----------------|----------------|----------------------|
| `chunk_0.wav` | *"No worries — I'll send you the notes afterwards."* | 2 (pēdējā) |
| `chunk_1.wav` | *"Hey, are you coming to the three o'clock meeting?"* | 0 (pirmā) |
| `chunk_2.wav` | *"I can't — I've got a dentist appointment then."* | 1 |

Patiesā kārtība ir **chunk_1 → chunk_2 → chunk_0**, tāpēc `P = [2, 0, 1]`, un `prefix.json` satur `[1, 2]`.

⚠️ **P jābūt īstai permutācijai:** garums n, indeksēts no 0, katra vērtība tieši vienu reizi. Dublikāti, iztrūkstošas vērtības vai ieraksti ārpus diapazona (piem., indeksēti no 1) dod 0 punktus par šo dialogu, tāpat kā failā iztrūkstošs dialogs. Nepareizi noformēts vai ne-JSON fails tiek atmests.

## Vērtēšana

Šī uzdevuma vērtēšana ir **pāru sakārtojuma precizitāte (pairwise ordering accuracy)**. Tā pārbauda katru fragmentu pāri un noskaidro: _kuram no diviem jābūt pirmajam?_ Pāris ir pareizs, ja jūsu prognoze dod to pašu atbildi kā patiesās vērtības (ground truth). Dialogam ar `n` fragmentiem ir $$M = n(n-1)/2$$ pāru; lai `I` ir inversiju skaits — pāru skaits, kas sakārtoti atšķirīgi no patiesajām vērtībām:

$$\text{score} = 1 - \frac{I}{M} \in [0, 1]$$

ℹ️ **Galīgais rezultāts ir vidējais no atsevišķu dialogu rezultātiem pār visiem
dialogiem attiecīgajā sadalījumā.**

## Atļautie modeļi

Šī uzdevuma risināšanai gan trenēšanas, gan novērtēšanas laikā jūs varat izmantot tikai turpmāk norādītos iepriekš apmācītos modeļus. Visi šie modeļi jau ir lejupielādēti un pieejami vidē. Piemērus, kā tos lietot, jūs varat redzēt baseline notebook `solution.ipynb`. Ņemiet vērā, ka jūs nevarat izmantot nekādus citus modeļus, un jūsu programmai nav interneta piekļuves.

- **Runas reprezentācijas:** **wav2vec 2.0**. Var izmantot arī **Whisper encoder** kā pazīmju ekstraktoru.
[wav2vec modeļa kartīte](https://yastatic.net/s3/contest/ioai/1/01_facebook_wav2vec2-base-960h_MODEL_CARD.html)

- **Automātiskā runas atpazīšana (ASR):** **OpenAI Whisper** (jebkurš izmērs).
[Whisper modeļa kartīte](https://yastatic.net/s3/contest/ioai/1/03_openai_whisper-small_MODEL_CARD.html)
- **Valodas modelis:** **Qwen2.5-0.5B**, ko var izmantot vai nu zero-shot, vai precizētu (fine-tuned) uz dotā `train` sadalījuma.
[Qwen modeļa kartīte](https://yastatic.net/s3/contest/ioai/1/02_Qwen_Qwen2.5-0.5B_MODEL_CARD.html)
Ņemiet vērā, ka 10 minūšu ierobežojumā jāietilpst jebkurai trenēšanai vai precizēšanai, ko veicat vērtēšanas laikā, kā arī inferencei uz novērtēšanas kopas.

## Kā iesniegt

- Atveriet `solution.ipynb` un izpildiet visas šūnas. Pārliecinieties, ka tas darba direktorijā izveido `answers.json` ar permutāciju katram dialogam mapē `dataset/test_public/` (100 dialogi). Vērtēšanas laikā notebook tiek izpildīts atkārtoti uz slēptās testa kopas, un tiek vērtēts `answers.json`, ko tas tur izveido.
- Uzlabojiet risinājumu, ja vēlaties — vai neuzlabojiet; baseline vien apstiprina, ka pipeline darbojas.
- Atveriet Git cilni JupyterLab kreisajā sānjoslā.
- **Stage** `solution.ipynb` (+ ikona blakus tam).
- Ievadiet commit ziņojumu un noklikšķiniet **Commit**.
- Noklikšķiniet uz mākoņa ar augšupvērstu bultu, lai veiktu push.
- Atgriezieties šajā Contest lapā un noklikšķiniet **Submit**.

Iesniedziet tieši vienu failu ar nosaukumu `solution.ipynb`.
