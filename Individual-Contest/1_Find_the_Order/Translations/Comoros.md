# Retrouvez l’ordre

- **Limite de temps :** 10 minutes
- **Environnement :** un GPU (≈16 GB VRAM), sans accès à Internet
- **Taille de la solution :** `solution.ipynb` ≤ 1 MB
- **Stockage :** 5 GB 

## Problème

Vous disposez de dialogues en anglais parlé entre deux participants, *Locuteur A* et *Locuteur B*. Chaque dialogue est segmenté en tours de parole, chaque tour contenant la parole d’un seul locuteur. Chaque tour est stocké dans un fichier audio `.wav` distinct ; un dialogue complet est donc représenté par un ensemble de fichiers `.wav`, un pour chaque tour. 

Malheureusement, les tours ont été mélangés aléatoirement, de sorte que la conversation n’a plus de sens. Dans le nom de fichier `chunk_{k}.wav`, `k` désigne le k-ième segment de l’ensemble mélangé, et non le k-ième tour du dialogue d’origine.

**‼️ Votre tâche consiste à reconstituer l’ordre chronologique d’origine de la conversation.**

![Retrouvez l’ordre](../find_the_order.jpg)

---

## Dataset

Chaque dialogue contient des fichiers audio `n` nommés `chunk_0.wav`, `chunk_1.wav`, …, `chunk_{n-1}.wav`. Les segments sont des tours de parole individuels. Les noms de fichiers correspondent uniquement à l’ordre mélangé. Ils n’indiquent pas la place d’un segment dans la conversation d’origine. Chaque dialogue comporte 7–20 segments, en mono, à 44.1 kHz (vous pouvez
rééchantillonner).

**`prefix.json` contient les indices des noms de fichiers des deux premiers segments de chaque dialogue.** Cela identifie le véritable début du dialogue et élimine l’ambiguïté entre la lecture de la conversation dans le sens chronologique ou dans le sens inverse.

Par exemple : `11: [7, 12]` signifie que les premier et deuxième tours du dialogue 11 sont respectivement `chunk_7.wav` et `chunk_12.wav`.

### Ce qui vous est fourni

Vous recevez **deux dossiers de format identique** :

| Dossier | Dialogues | `answers.json` ? | Utilisation |
|--------|-----------|-----------------|-----------|
| `dataset/train/` | 1,288 | ✅ inclus | entraîner / affiner votre modèle |
| `dataset/test_public/`  | 100   | ✅ inclus | exécuter votre pipeline et calculer vous-même votre score local |

Lors de l’évaluation, votre dossier `dataset/test_public/` est remplacé de manière transparente par
un `hidden evaluation set` (`test_leaderboard_a` pour le classement public et `test_leaderboard_b` pour le classement final) — ceux-ci ont la même taille et le même format que `dataset/test_public/`, mais sans `answers.json`.

Votre notebook est exécuté à nouveau sur ces données, et le fichier `answers.json` qu’il produit est utilisé pour le calcul du score. Les dialogues de test mis de côté proviennent de la même distribution que `train` ; votre score `test_public` local constitue donc un aperçu fidèle.

### Structure des répertoires

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

## Sortie

Pour chaque dialogue, déterminez l’ordre chronologique d’origine de ses segments audio. Votre prédiction doit être une permutation `P` de `{0, 1, …, n−1}`, où `P[i]` est la position chronologique prédite de `chunk_i.wav` (0 = premier).

Votre fichier de sortie `answers.json` doit associer chaque identifiant de dialogue à la permutation prédite correspondante :

```json
{
  "17": [2, 0, 1],
  "42": [0, 1],
  "108": [3, 1, 0, 4, 2, 5]
}
```

### Exemple

Un dialogue comporte 3 segments mélangés `chunk_0, chunk_1, chunk_2` :

| segment mélangé | contenu parlé | position réelle (rang) |
|----------------|----------------|----------------------|
| `chunk_0.wav` | *"No worries — I'll send you the notes afterwards."* | 2 (dernier) |
| `chunk_1.wav` | *"Hey, are you coming to the three o'clock meeting?"* | 0 (premier) |
| `chunk_2.wav` | *"I can't — I've got a dentist appointment then."* | 1 |

L’ordre réel est **chunk_1 → chunk_2 → chunk_0** ; ainsi, `P = [2, 0, 1]`, et `prefix.json` contient `[1, 2]`.

⚠️ **P doit être une véritable permutation :** de longueur n, indexée à partir de 0, chaque valeur apparaissant exactement une fois. Les doublons, les valeurs manquantes ou hors limites (par exemple, une indexation à partir de 1) donnent un score de 0 pour ce dialogue, tout comme l’absence d’un dialogue dans le fichier. Un fichier mal formé ou qui n’est pas au format JSON est rejeté.

## Évaluation

La métrique d’évaluation de cette tâche est **l’exactitude de l’ordre par paires**. Elle examine chaque paire de segments et pose la question : _lequel des deux doit venir en premier ?_ Une paire est correcte si votre prédiction donne la même réponse que la vérité terrain. Pour un dialogue comportant `n` segments, il existe $$M = n(n-1)/2$$ paires ; soit `I` le nombre d’inversions — les paires ordonnées différemment de la vérité terrain :

$$\text{score} = 1 - \frac{I}{M} \in [0, 1]$$

ℹ️ **Le score final est la moyenne des scores par dialogue sur l’ensemble des
dialogues du split.**

## Modèles autorisés

Vous pouvez uniquement utiliser les modèles préentraînés suivants pour résoudre cette tâche, aussi bien pendant l’entraînement que pendant l’évaluation. Tous ces modèles sont déjà téléchargés et disponibles dans l’environnement. Vous trouverez des exemples d’utilisation dans le notebook baseline `solution.ipynb`. Veuillez noter que vous ne pouvez utiliser aucun autre modèle et que votre programme n’a pas accès à Internet.

- **Représentations de la parole :** **wav2vec 2.0**. L’**encodeur Whisper** peut également être utilisé comme extracteur de caractéristiques.
[Fiche du modèle wav2vec](https://yastatic.net/s3/contest/ioai/1/01_facebook_wav2vec2-base-960h_MODEL_CARD.html)

- **Reconnaissance automatique de la parole (ASR) :** **OpenAI Whisper** (toute taille).
[Fiche du modèle Whisper](https://yastatic.net/s3/contest/ioai/1/03_openai_whisper-small_MODEL_CARD.html)
- **Modèle de langage :** **Qwen2.5-0.5B**, qui peut être utilisé soit en zero-shot, soit affiné sur le split `train` fourni.
[Fiche du modèle Qwen](https://yastatic.net/s3/contest/ioai/1/02_Qwen_Qwen2.5-0.5B_MODEL_CARD.html)
Notez que la limite de 10 minutes doit couvrir tout entraînement ou affinement que vous effectuez au moment de l’évaluation, ainsi que l’inférence sur l’ensemble d’évaluation.

## Procédure de soumission

- Ouvrez `solution.ipynb` et exécutez toutes les cellules. Vérifiez qu’il écrit `answers.json` dans le répertoire de travail, avec une permutation pour chaque dialogue de `dataset/test_public/` (100 dialogues). Au moment de l’évaluation, le notebook est exécuté à nouveau sur l’ensemble de test caché, et le fichier `answers.json` qu’il y produit est évalué.
- Améliorez la solution si vous le souhaitez — ou ne le faites pas ; le baseline suffit à valider le pipeline.
- Ouvrez l’onglet Git dans la barre latérale gauche de JupyterLab.
- **Ajoutez à la zone de préparation** `solution.ipynb` (l’icône + à côté).
- Saisissez un message de commit et cliquez sur **Commit**.
- Cliquez sur l’icône de nuage avec une flèche vers le haut pour effectuer le push.
- Revenez sur cette page du concours et cliquez sur **Submit**.

Soumettez exactement un fichier, nommé `solution.ipynb`.
