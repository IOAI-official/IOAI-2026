# Brambora

- **Časový limit:** 10 minutes
- **Prostředí:** jedno GPU (≈16 GB VRAM), bez internetu
- **Velikost řešení:** `solution.ipynb` ≤ 1 MB
- **Úložiště:** 5 GB 

## Úloha
 
Váš přítel navrhuje zahrát si hádací hru.
Jako rozhodčí vybere jedno skryté slovo z pevně daného slovníku a vy je musíte najít nejvýše za 30 tahů.
V každém tahu rozhodčí porovná dvě slova a oznámí, které z nich je sémanticky bližší
skrytému slovu. Každá hra začíná
pevně danou dvojicí `lamp vs potato`, protože jde o dvě z nejoblíbenějších věcí vašeho přítele. Váš program poté
navrhne jedno nové slovo. Vítěz porovnání zůstane zachován
a je porovnán s vaším dalším návrhem. 
Hru vyhrajete v okamžiku, kdy navrhnete přesně skryté slovo. Při porovnávání
se rozlišují velká a malá písmena. Každé slovo, které navrhnete, musí být v `dataset/vocabulary.json`.

Úplný příklad s protokolem a načítáním dat je v `solution.ipynb`. 
Třídu PublicEmbeddingPlayer můžete změnit. Váš program je inicializován jednou a odehraje všechny hry v rámci jediného spuštění;
protokol na začátku každé hry vytvoří nový objekt PublicEmbeddingPlayer.

## Rozhodčí

Váš program odešle rozhodčímu jeden objekt JSON a rozhodčí odpoví jedním objektem JSON. 

Propracovaný příklad, ve kterém je skryté slovo uvedeno pouze pro vysvětlení protokolu:

```text
Hidden word: shovel          Fixed opening: lamp vs potato

<- {"turn": 1, "winner_word": "potato", "verdict": "second", "word1": "lamp",   "word2": "potato"}
-> {"new_word": "rock"}
<- {"turn": 2, "winner_word": "rock",   "verdict": "second", "word1": "potato", "word2": "rock"}
-> {"new_word": "hammer"}
<- {"turn": 3, "winner_word": "hammer", "verdict": "second", "word1": "rock",   "word2": "hammer"}
-> {"new_word": "shovel"}                                    <- matches: game won
-> {"status": "win"}
```

Tahy jsou číslovány od 1 do 30.

Možnosti `verdict` jsou `first`, což znamená, že word1 je bližší, `second`, což znamená, že word2 je bližší, nebo
`same`, což znamená, že obě slova jsou ke skrytému slovu stejně blízko. 

`winner_word` je slovo zachované pro další porovnání. Při verdiktu `same` zůstává první slovo.

## Dataset

Společné pro všechna rozdělení:

- `dataset/vocabulary.json` — 1602 unikátních slov psaných malými písmeny. Skryté slovo je vždy
  jedním z nich.
- `dataset/public_embeddings.npy` — `float32`, tvar `(1602, 2560)`. Řádek `i`
  odpovídá slovu `i` ve slovníku. Jde o *veřejné* embeddingy;
  rozhodčí používá jinou, skrytou reprezentaci.

Rozdělení jsou množiny skrytých slov:

| Rozdělení | Slova | Odpovědi | Použití |
|---|---|---|---|
| `test_public` | 120 | ✅ `dataset/test_public.json` | spuštění vašeho řešení a vlastní vyhodnocení |
| `test_leaderboard_a` | 120 | skryté | průběžný žebříček |
| `test_leaderboard_b` | 120 | skryté | konečné pořadí |

Rozdělení `train` neexistuje — z označených řádků se nic neučí.

### Poskytnuté modely

S úlohou jsou dodávány dva předtrénované modely embeddingů, které lze použít:

```text
models/Qwen/Qwen3-Embedding-0.6B
[Qwen Embedding model card](https://yastatic.net/s3/contest/ioai/3/01_Qwen_Qwen3-Embedding-0.6B_MODEL_CARD.html)
models/BAAI/bge-m3
[bge-m3 model card](https://yastatic.net/s3/contest/ioai/3/02_BAAI_bge-m3_MODEL_CARD.html)
```

Oba musí být načteny ze své lokální cesty; ID hubu Hugging Face, například
`"BAAI/bge-m3"`, spustí stahování a selže, protože vyhodnocování probíhá offline. Každý
adresář obsahuje spustitelný soubor `example.py`, který ukazuje volání offline.

Dostupné knihovny: `numpy`, `torch`, `sentence-transformers`. Bez internetu, bez
stahování, bez dalších balíčků.

## Výstup

Žádný. Toto je interaktivní úloha: vaše řešení nezapisuje žádný soubor s odpovědí; komunikuje
s rozhodčím prostřednictvím stdin/stdout, jak je popsáno výše.

## Metrika

Hra vyřešená v tahu `t` získá skóre `1.0 - 0.02 × max(0, t - 10)`; hra nevyřešená
během 30 tahů získá skóre `0`. Tahy 1–10 tedy získají skóre `1.00`, tah 20 získá skóre `0.80` a tah
30 získá skóre `0.60`.

Vaše skóre za úlohu je průměrné skóre hry × 100, mezi `0.00` a `100.00`.

Limit 10 minut je jediné společné omezení zahrnující spuštění, přípravu a všech 120
her v testovací sadě. 

## Jak odevzdat řešení

1. Otevřete `solution.ipynb`, upravte `PublicEmbeddingPlayer` a spusťte všechny buňky, abyste se ujistili, že vše funguje.
2. Volitelně je zkontrolujte lokálně: `python local_test.py solution.ipynb --limit 5`.
   Lokální rozhodčí používá *veřejné* embeddingy, takže jeho skóre je
   pouze orientační.
3. Uložte `solution.ipynb`.
4. Otevřete kartu Git v levém postranním panelu JupyterLab.
5. Přidejte `solution.ipynb` do staging area (ikona **+** vedle něj).
6. Zadejte zprávu commitu a klikněte na Commit.
7. Kliknutím na ikonu mraku se šipkou nahoru proveďte push.
8. Vraťte se na tuto stránku soutěže a klikněte na Submit; zpráva commitu se musí shodovat se zprávou, kterou jste uvedli.

Odevzdejte právě jeden soubor s názvem `solution.ipynb`, který zahrnuje veškerou nezbytnou přípravu a inferenci.
