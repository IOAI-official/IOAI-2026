# Duch maszyny

- **Limit czasu:** 10 minut
- **Wynik bazowy:** 28.6
- **Wynik Komitetu Naukowego:** 93.41
- **Środowisko:** jeden GPU (≈16 GB VRAM), bez dostępu do internetu
- **Rozmiar rozwiązania:** `solution.ipynb` ≤ 20 MB
- **Pamięć masowa:** 5 GB
- **Modele wstępnie wytrenowane:** wyłącznie **[bge-base-en-v1.5](https://yastatic.net/s3/contest/ioai/5/01_BAAI_bge-base-en-v1.5_MODEL_CARD.html)** — tekstowy **enkoder** (model osadzeń, ang. embedding model).


## Zadanie

W Archiwum Narodowym Kazachstanu dzieją się dziwne rzeczy. Bibliotekarze twierdzą, że niektóre książki kończyły się kiedyś inaczej, ale nikt nie potrafi tego udowodnić — każdy egzemplarz jest taki sam, a każda historia nadal ma sens. Zaproszono Cię jako badacza AI, aby zlokalizować zmiany.
![Duch](../../ghost.jpg)

Fragment rozpoczyna się tekstem napisanym przez człowieka, a w pewnym momencie niepostrzeżenie przechodzi
w kontynuację wygenerowaną przez model językowy. Czytany jako całość wygląda jak
jeden spójny utwór — ale gdzieś w środku autor zmienia się z człowieka
w maszynę. Twoim zadaniem jest **znalezienie tego przejścia: indeksu znaku, w którym
kończy się część napisana przez człowieka, a zaczyna część wygenerowana przez maszynę**.

Każda próbka jest pojedynczym ciągiem znaków `text`. Istnieje dokładnie jedna granica. Wszystko
przed nią zostało napisane przez człowieka; wszystko od niej począwszy zostało wygenerowane przez maszynę.

## Zbiór danych

Angielskie fragmenty zwykłego tekstu, z jedną granicą w każdym z nich.

- **Część A** (przed granicą): fragment tekstu napisanego przez człowieka.
- **Część B** (od granicy): kontynuacja utworzona przez model językowy,
  uwarunkowana Częścią A.
- Każda część ma co najmniej 180 słów; łączna długość wynosi ~500–800 słów.
- **`boundary_char_index`** jest przesunięciem znakowym, przy którym kończy się Część A:
  `text[:boundary_char_index]` jest częścią napisaną przez człowieka, a
  `text[boundary_char_index:].lstrip()` jest częścią wygenerowaną przez maszynę.

#### Co otrzymujesz

Otrzymujesz **dwa foldery**:

| Folder | Próbki | `answers.jsonl`? | Wykorzystanie |
|--------|---------|------------------|-----------|
| `dataset/train/` | 1,221 | ✅ dołączone | trenowanie / dostrajanie metody |
| `dataset/test_public/`  | 380   | ✅ dołączone (kopia deweloperska) | uruchomienie pipeline'u i lokalne obliczenie własnego wyniku |

Podczas **oceniania** Twój folder `dataset/test_public/` jest **zastępowany ukrytym
zbiorem ewaluacyjnym**. Ma on ten sam format, ale **bez `answers.jsonl`**. Twój
notebook jest na nim ponownie uruchamiany, a utworzony przez niego plik `answers.jsonl` jest oceniany.

- Publiczna tabela wyników korzysta z ukrytego zbioru **test_leaderboard_a** (380 próbek).

- Ostateczny ranking korzysta z ukrytego zbioru **test_leaderboard_b** (380 próbek).

Wszystkie trzy zbiory ewaluacyjne
mają ten sam rozmiar i pochodzą z tego samego rozkładu co `train`, więc Twój lokalny
wynik dla `dataset/test_public/` stanowi rozsądne oszacowanie wyniku w tabeli wyników.

#### Format na dysku

```
dataset/train/data.jsonl      # one JSON object per line: {"id": "...", "text": "..."}
dataset/train/answers.jsonl   # {"id": "...", "boundary_char_index": 1842}
dataset/test_public/data.jsonl       # {"id": "...", "text": "..."}
dataset/test_public/answers.jsonl    # dev copy only — ABSENT in the hidden grading set
```

- Identyfikatory w `answers.jsonl` odpowiadają identyfikatorom w `data.jsonl`.
- `dataset/train/` (z odpowiedziami) jest dostępny zawsze, gdy trenujesz lub dostrajasz model.

## Wyjście (format zgłoszenia)

Przesyłasz **pojedynczy notebook, który musi nosić nazwę `solution.ipynb`**. Ta dokładna nazwa pliku jest wymagana. Wszystkie inne pliki zostaną odrzucone bez uruchamiania.

Twój notebook musi **odczytać `dataset/test_public/data.jsonl`** i zapisać pojedynczy plik
**`answers.jsonl`** w katalogu głównym repozytorium — po jednym obiekcie JSON w każdym wierszu, odwzorowującym
identyfikator każdej próbki na przewidziany przez Ciebie indeks znaku granicy:

```json
{"id": "example_000123", "boundary_char_index": 1790}
{"id": "example_000124", "boundary_char_index": 2450}
```

- `boundary_char_index` musi być **liczbą całkowitą należącą do `[0, len(text)]`**.
- Każdy identyfikator w `dataset/test_public/data.jsonl` powinien wystąpić dokładnie raz. Próbka, której brakuje
  w `answers.jsonl` (albo której wartość nie jest liczbą całkowitą / wykracza poza zakres), otrzymuje 0
  punktów za tę próbkę.

## Ocenianie

Dla każdej próbki niech `p` będzie przewidzianym przez Ciebie indeksem, a `t` prawdziwą granicą. Wynik dla próbki maleje wykładniczo wraz z odległością wyrażoną w znakach:

$$\text{score} = \exp\!\left(-\frac{|p - t|}{\tau}\right) \in (0, 1], 
~ \text{where} ~ \tau = 100.$$

Prowadzi to do następującego zachowania wyniku:
- **=1.0** — dokładny znak granicy;
- **≈0.78** — błąd o 25 znaków; - **≈0.61** — błąd o 50 znaków;
- **≈0.37** — błąd o 100 znaków;
- **≈0.01** — błąd o 500 znaków.

**Wynik końcowy jest średnią** wyników dla próbek ze wszystkich próbek w danym podzbiorze
(podawaną w skali 0–100). Metryka nagradza znalezienie się *blisko*, a nie tylko dokładne trafienie.

## Ograniczenia

- **Środowisko:** jeden GPU (≈16 GB VRAM), bez dostępu do internetu podczas oceniania — dozwolony
  model (poniżej) jest już udostępniony. **Budżet czasu rzeczywistego: 10 minut** na
  całe uruchomienie — musi on obejmować wszelkie trenowanie / dostrajanie wykonywane podczas oceniania
  **oraz** inferencję na zbiorze ewaluacyjnym.
- **Dozwolony model wstępnie wytrenowany** — poniższa lista jest wyczerpująca; nie wolno
  używać żadnych innych wstępnie wytrenowanych wag. Jest on **z góry udostępniony w środowisku** (należy wczytać go w zwykły sposób, np.
  `from_pretrained`; podczas oceniania nie ma dostępu do internetu):
  - **bge-base-en-v1.5** — tekstowy **enkoder** o 110M parametrów (model osadzeń). Tworzy on
    osadzenia zdań/fragmentów; nie jest generatywnym modelem językowym. Możesz
    użyć go **bez zmian (zamrożone cechy) lub dostroić go na podzbiorze `train`**
    (pełne dostrajanie mieści się w budżecie 16 GB / 10 minut).
- Narzędzia klasyczne / statystyczne nie podlegają ograniczeniom: możesz zbudować dowolny model oparty na cechach
  (np. klasyfikatory lub regresory scikit-learn) na podstawie samodzielnie obliczonych cech osadzeń.
  Ograniczenie dotyczące *wstępnie wytrenowanych wag uczenia głębokiego* odnosi się wyłącznie do powyższej listy.

## Rozwiązanie bazowe

Udostępniony `solution.ipynb` jest trywialnym punktem odniesienia: szacuje pojedynczy
„średni ułamek położenia granicy” na podstawie `dataset/train/` i przewiduje ten sam ułamek
długości dla każdego fragmentu testowego. Uzyskuje wynik **28.6** na ukrytym
podzbiorze **test_leaderboard_a** i służy wyłącznie jako uruchamialny szablon pętli
odczytaj-`dataset/test_public/` → zapisz-`answers.jsonl`.

**Wynik Komitetu Naukowego wynoszący 93.41**, zmierzony na tym samym podzbiorze i przy tym samym
budżecie 10 minut, pochodzi z dostrojenia dozwolonego enkodera na `train` i zlokalizowania
przejścia jako punktu zmiany (ang. changepoint) w obrębie zdań. Nie jest to górne ograniczenie — maksymalny
wynik w tej metryce to 100.
