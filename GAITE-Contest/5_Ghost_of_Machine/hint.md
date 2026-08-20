## Ghost of the Machine Hints

Every author has their own voice, including an LLM. I'm sure you can tell whether it's your mother writing you a message or your best friend.

So in machine learning, you can find features that help you detect exactly when the author has changed.

Let's dig into the problem. Each hint keeps the code from the hints before it --
hint 2 uses `candidates` and `snap` from hint 1, and so on.

### Hint 0

Before anything else -- a way to check yourself. Run it after every change. It's much cheaper than a submission! Score can go up and down, happy exploring.

```python
import math

def validate(preds):
    """How close are our predictions? 100 is perfect, the baseline gets 28.6."""
    answers = read_jsonl(f"{TEST_DIR}/answers.jsonl")
    total = 0
    for r in answers:
        total += math.exp(-abs(preds[r["id"]] - r["boundary_char_index"]) / 100)
    return 100 * total / len(answers)

print(validate(preds))
```

### Hint 1

Always look at the data. Find the split for a couple of sentences by index. If you look closely, you can spot a certain character that is always right before the switch. 

The baseline guesses a fixed fraction of the length. Keep that guess, but move it
to the nearest *candidate* -- a position where a new sentence could start.
Replace the `preds = ...` line in the baseline with this:

```python
# <-- will you find correct one instead of comma?
SEPARATOR = ", "

def candidates(text):
    """Character positions where a new sentence could start."""
    positions = [0]
    found = text.find(SEPARATOR)
    while found != -1:
        positions.append(found + len(SEPARATOR))
        found = text.find(SEPARATOR, found + 1)
    return positions

def snap(text, guess):
    """Move the guess to the closest candidate position."""
    best = 0
    for position in candidates(text):
        if abs(position - guess) < abs(best - guess):
            best = position
    return best

preds = {}
for r in test_rows:
    # lock to closest separators
    preds[r["id"]] = snap(r["text"], mean_frac * len(r["text"]))
```

### Hint 2

Try the most characteristic words -- e.g. if somebody sends you "67" messages, it's probably not your parents. And you certainly have a friend who overuses emojis.

An LLM also has its favorite words. Try to find the frequent ones.

```python
MARKERS = ["while", "despite", "however", "moreover", "furthermore"]

LOW, HIGH = 0.5, 0.7   # only look in the middle of the text

def sounds_like_llm(sentence):
    for word in MARKERS:
        if word in sentence.lower():
            return True
    return False

preds = {}
for r in test_rows:
    text = r["text"]
    starts = candidates(text)
    prediction = snap(text, mean_frac * len(text))
    for start, end in zip(starts, starts[1:] + [len(text)]):
        if LOW * len(text) < start < HIGH * len(text) and sounds_like_llm(text[start:end]):
            prediction = start
            break
    preds[r["id"]] = prediction
```

### Hint 3

There is only one change point, so if there are several suspicious sentences in a row, you can be much more sure. But walk backwards, from the end of the text: then `suspicion` tells you how
machine-like everything *after* this point is -- which is exactly what a boundary means.

```python
DECAY = 0.9                   # how well we remember the sentences before
GAIN = 0.2                    # how much one favorite word adds. 

preds = {}
for r in test_rows:
    text = r["text"]
    starts = candidates(text)
    ends = starts[1:] + [len(text)]
    sentences = list(zip(starts, ends))
    guess = mean_frac * len(text)

    suspicion = 0
    prediction = 0
    best_score = -1               # the score is never worse than this
    for start, end in reversed(sentences): # from the end back to the beginning
        suspicion = DECAY * suspicion + GAIN * sounds_like_llm(text[start:end])
        score = suspicion - abs(start - guess) / len(text)
        if score > best_score: # finding most suspect switch
            best_score = score
            prediction = start

    preds[r["id"]] = prediction
```

### Hint 4

Now it's time to remember that you have an embedding model! You can generate a representation for each sentence and train a binary classifier: is it human or LLM?

```python
import torch
from transformers import AutoTokenizer, AutoModel

MODEL = "models/bge-base-en-v1.5"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = AutoModel.from_pretrained(MODEL).eval().to(DEVICE)

BATCH_SIZE = 16               # how many sentences go through the model at once

def embed(sentences):
    """Turn every sentence into 768 numbers."""
    vectors = []
    for i in range(0, len(sentences), BATCH_SIZE):
        batch = tokenizer(sentences[i:i + BATCH_SIZE], padding=True, truncation=True,
                          max_length=128, return_tensors="pt").to(DEVICE)
        with torch.no_grad():
            hidden = model(**batch).last_hidden_state[:, 0]
        vectors.append(torch.nn.functional.normalize(hidden, dim=-1).cpu())
    return torch.cat(vectors).numpy()

# in dataset/train/ we know where the boundary is, so we know who wrote each sentence
train_sentences = []
train_labels = []
for r in train_rows:
    text = r["text"]
    starts = candidates(text)
    ends = starts[1:] + [len(text)]
    for start, end in zip(starts, ends):
        train_sentences.append(text[start:end])
        train_labels.append(int(start >= train_ans[r["id"]]))   # 1 = written by the LLM

print(len(train_sentences), "sentences,", sum(train_labels), "of them from the LLM")
X = embed(train_sentences)
print("embeddings:", X.shape)

# now train sklearn.linear_model.LogisticRegression or xgboost on X and train_labels.
# then embed the test sentences the same way and use
#
#     classifier.predict_proba(test_X)[:, 1]
#
# instead of sounds_like_llm -- it says how machine-like a sentence is,
# somewhere between 0 and 1, instead of just True or False.
#
# embedding all 35000 training sentences takes ~15 minutes on a CPU and under a
# minute on the GPU -- and you only have 10 minutes for the whole run.
```

### Hint 5

Try to combine some of the above!
