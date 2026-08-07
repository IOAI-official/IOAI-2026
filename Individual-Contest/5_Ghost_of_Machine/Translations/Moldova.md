# Fantoma mașinii

- **Limită de timp:** 10 minute
- **Scor de referință:** 28.6
- **Mediu:** un GPU (≈16 GB VRAM), fără internet
- **Dimensiunea soluției:** `solution.ipynb` ≤ 20 MB
- **Spațiu de stocare:** 5 GB
- **Modele preantrenate:** doar **[bge-base-en-v1.5](https://yastatic.net/s3/contest/ioai/5/01_BAAI_bge-base-en-v1.5_MODEL_CARD.html)** — un **encoder** de text (model de embedding).


## Sarcină

La Arhiva Națională a Kazahstanului se întâmplă lucruri ciudate. Bibliotecarii spun că unele cărți aveau înainte finaluri diferite, dar nimeni nu poate dovedi acest lucru — fiecare exemplar este identic și fiecare poveste continuă să aibă sens. Sunteți invitați, în calitate de cercetători în IA, să localizați modificările.
![Fantomă](../ghost.jpg)

Un pasaj începe ca text scris de un om și, la un moment dat, trece neobservat
la o continuare generată de un model lingvistic. Citit în întregime, pare
un text coerent — dar undeva, la mijloc, autorul se schimbă dintr-o persoană
într-o mașină. Sarcina dumneavoastră este să **găsiți acea trecere: indicele caracterului la care
partea scrisă de om se încheie și începe partea generată de mașină**.

Fiecare eșantion este un singur șir de caractere `text`. Există exact o singură graniță. Tot ce se află
înaintea ei este scris de om; tot ce se află începând de la ea este generat de mașină.

## Dataset

Pasaje în limba engleză, în format text simplu, fiecare având o singură graniță.

- **Partea A** (înainte de graniță): un fragment de text scris de un om.
- **Partea B** (începând de la graniță): o continuare produsă de un model lingvistic,
  condiționată de Partea A.
- Fiecare parte are cel puțin 180 de cuvinte; lungimea totală este de ~500–800 de cuvinte.
- **`boundary_char_index`** este decalajul în caractere la care se încheie Partea A:
  `text[:boundary_char_index]` este partea scrisă de om, iar
  `text[boundary_char_index:].lstrip()` este partea generată de mașină.

#### Ce primiți

Primiți **două directoare**:

| Director | Eșantioane | `answers.jsonl`? | Folosiți-l pentru |
|--------|---------|------------------|-----------|
| `dataset/train/` | 1,221 | ✅ inclus | antrenarea / ajustarea fină a metodei dumneavoastră |
| `dataset/test_public/`  | 380   | ✅ inclus (copie dev) | rularea pipeline-ului dumneavoastră și calcularea locală a propriului scor |

La **momentul evaluării**, directorul dumneavoastră `dataset/test_public/` este **înlocuit cu un set de
evaluare ascuns**. Acesta are același format, dar **fără `answers.jsonl`**. Notebook-ul dumneavoastră
este rulat din nou pe acesta, iar `answers.jsonl` pe care îl produce este evaluat.

- Clasamentul public folosește un set ascuns **test_leaderboard_a** (380 de eșantioane).

- Clasamentul final folosește un set ascuns **test_leaderboard_b** (380 de eșantioane).

Toate cele trei seturi de evaluare
au aceeași dimensiune și sunt extrase din aceeași distribuție ca `train`, astfel încât scorul dumneavoastră local
`dataset/test_public/` reprezintă o estimare rezonabilă a scorului dumneavoastră din clasament.

#### Formatul de pe disc

```
dataset/train/data.jsonl      # one JSON object per line: {"id": "...", "text": "..."}
dataset/train/answers.jsonl   # {"id": "...", "boundary_char_index": 1842}
dataset/test_public/data.jsonl       # {"id": "...", "text": "..."}
dataset/test_public/answers.jsonl    # dev copy only — ABSENT in the hidden grading set
```

- ID-urile din `answers.jsonl` corespund ID-urilor din `data.jsonl`.
- `dataset/train/` (cu răspunsuri) este disponibil ori de câte ori antrenați sau efectuați ajustarea fină.

## Ieșire (formatul trimiterii)

Trimiteți **un singur notebook, care trebuie să fie denumit `solution.ipynb`**. Este obligatoriu acest nume exact de fișier. Orice altceva este respins fără a fi rulat.

Notebook-ul dumneavoastră trebuie să **citească `dataset/test_public/data.jsonl`** și să scrie un singur fișier
**`answers.jsonl`** în rădăcina repository-ului — câte un obiect JSON pe linie, care asociază
fiecare ID de eșantion cu indicele în caractere prezis pentru graniță:

```json
{"id": "example_000123", "boundary_char_index": 1790}
{"id": "example_000124", "boundary_char_index": 2450}
```

- `boundary_char_index` trebuie să fie un **număr întreg din `[0, len(text)]`**.
- Fiecare ID din `dataset/test_public/data.jsonl` trebuie să apară exact o dată. Un eșantion care lipsește
  din `answers.jsonl` (sau are o valoare care nu este un număr întreg / este în afara intervalului) primește scorul 0
  pentru acel eșantion.

## Evaluare

Pentru fiecare eșantion, fie `p` indicele prezis de dumneavoastră și `t` granița reală. Scorul per eșantion scade exponențial în funcție de distanța în caractere:

$$\text{score} = \exp\!\left(-\frac{|p - t|}{\tau}\right) \in (0, 1], 
~ \text{where} ~ \tau = 100.$$

Aceasta conduce la următorul comportament al scorului:
- **=1.0** — caracterul exact al graniței;
- **≈0.78** — abatere de 25 de caractere; - **≈0.61** — abatere de 50 de caractere;
- **≈0.37** — abatere de 100 de caractere;
- **≈0.01** — abatere de 500 de caractere.

**Scorul final este media** scorurilor per eșantion pentru toate eșantioanele din subset
(raportată pe o scară de la 0–100). Metrica recompensează apropierea, nu doar exactitatea.

## Constrângeri

- **Mediu:** un GPU (≈16 GB VRAM), fără internet la momentul evaluării — modelul permis
  (de mai jos) este deja furnizat. **Buget de timp efectiv: 10 minute** pentru întreaga
  rulare — acesta trebuie să includă orice antrenare / ajustare fină pe care o efectuați la momentul evaluării,
  **precum și** inferența pe setul de evaluare.
- **Model preantrenat permis** — această listă este exhaustivă; nu pot fi utilizate alte ponderi
  preantrenate. Acesta este **furnizat în prealabil în mediu** (încărcați-l în mod normal, de exemplu
  `from_pretrained`; nu există internet la momentul evaluării):
  - **bge-base-en-v1.5** — un **encoder** de text cu 110M de parametri (model de embedding). Acesta
    produce embedding-uri pentru propoziții/pasaje; nu este un model lingvistic generativ. Îl
    puteți utiliza **ca atare (cu caracteristici înghețate) sau îl puteți ajusta fin pe subsetul `train`**
    (ajustarea fină completă se încadrează în bugetul de 16 GB / 10 minute).
- Instrumentele clasice / statistice nu sunt restricționate: puteți construi orice model bazat pe
  caracteristici (de exemplu, clasificatori sau regresori scikit-learn) peste caracteristicile de embedding pe care le
  calculați dumneavoastră. Restricția privind *ponderile preantrenate de deep learning* se aplică doar listei de mai sus.
