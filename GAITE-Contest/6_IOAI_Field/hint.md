# Hints for IOAI Field

## Hint: Check the score for each region

The final score is the average score over five regions. A low training loss does not always mean a high final score.

Check the score for every region. Find the region with the lowest score. Read output like this carefully:

```text
[I]
  I: ...
  score = ...

[O]
  O: ...
  score = ...

[I_entropy]
  I_entropy: ...
  score = ...

[param multiplier]
  Params: ... < 20260 => no penalty.

[total]
  Total: weighted mean of region scores * 100 = ...
```

## Hint: Balance the data or ignore some letters first

Uniform sampling gives you many background points and only a few points inside the letters.

You can make a batch for only some regions:

```python
xy, y = make_batch(
    batch_size,
    cfg,
    include_regions=("A", "bg"),
    stratified=True,
)
```

You can first learn easy regions such as `A` and the background. If you ignore a region, you cannot get points for that region in the final score.

## Hint: Try a larger model, but check the limit

A model with `20,260` parameters or more gets a score penalty.

Always count the parameters:

```python
num_params = sum(p.numel() for p in model.parameters())
print("Number of parameters:", num_params)
```

Start with the baseline. Try another hidden size or dropout value:

```python
model = CustomModel(
    hidden=[64, 64, 64],
    activation="gelu",
    dropout=0.2,
)
```

Do not only make the model wider. Simple features that match the shape of the field may work better.

## Hint: Detect the region first

The letters are in different parts of the field. You can first predict the region of each point. Then you can use a small part of the model for that region.

Here is a small example. It uses trainable parts for the first `I` and `O`. It uses fixed values for `A` and the background. It uses dropout for the last `I`.

```python
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


class SmallNet(nn.Module):
    def __init__(self, out_dim, hidden=32):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(2, hidden),
            nn.GELU(),
            nn.Linear(hidden, hidden),
            nn.GELU(),
            nn.Linear(hidden, out_dim),
        )

    def forward(self, xy):
        return self.net(xy)


class LastIPart(nn.Module):
    def __init__(self, value=2025.0):
        super().__init__()
        self.dropout = nn.Dropout(0.5)
        self.linear = nn.Linear(1, 1)

        with torch.no_grad():
            self.linear.weight.fill_(value)
            self.linear.bias.fill_(-value)

    def forward(self, xy):
        ones = torch.ones_like(xy[:, :1])
        return self.linear(self.dropout(ones))


class CustomModel(nn.Module):
    I, O, A, I_ENTROPY, BG = range(5)

    def __init__(self, i_min, i_max, hidden=32):
        super().__init__()
        self.router = SmallNet(5, hidden)
        self.i_part = SmallNet(1, hidden)
        self.o_part = SmallNet(1, hidden)
        self.last_i_part = LastIPart()
        self.i_min = float(i_min)
        self.i_range = float(i_max - i_min)

    def forward(self, xy):
        region = self.router(xy).argmax(dim=1)
        out = torch.zeros(
            (len(xy), 1),
            device=xy.device,
            dtype=xy.dtype,
        )

        mask = region == self.I
        if mask.any():
            normalized = torch.sigmoid(self.i_part(xy[mask]))
            out[mask] = self.i_min + self.i_range * normalized

        mask = region == self.O
        if mask.any():
            out[mask] = torch.tanh(self.o_part(xy[mask]))

        out[region == self.A] = -1.0

        mask = region == self.I_ENTROPY
        if mask.any():
            out[mask] = self.last_i_part(xy[mask])

        # Background points stay at zero.
        return out
```

## Hint: Train the router and the parts one by one

The router is a classification model. Its target is the region ID, not the field value.

Make a balanced batch with the same number of points from every region:

```python
region_names = ("I", "O", "A", "I_entropy", "bg")
xs = []
labels = []

for region_id, name in enumerate(region_names):
    xy, _ = make_batch(
        512,
        cfg,
        include_regions=(name,),
        stratified=True,
    )
    xs.append(xy)
    labels.append(
        np.full(len(xy), region_id, dtype=np.int64)
    )

x = torch.as_tensor(
    np.concatenate(xs),
    dtype=torch.float32,
    device=device,
)
label = torch.as_tensor(
    np.concatenate(labels),
    dtype=torch.long,
    device=device,
)
```

Train only the router with cross-entropy:

```python
optimizer = torch.optim.Adam(
    model.router.parameters(),
    lr=2e-3,
)

optimizer.zero_grad()
logits = model.router(x)
loss = F.cross_entropy(logits, label)
loss.backward()
optimizer.step()
```

Make new batches and repeat this step many times.

## Hint: Train each part on its own region

Train each part only on points from its region. For example, train the `O` part like this:

```python
x, y = make_batch(
    2048,
    cfg,
    include_regions=("O",),
    stratified=True,
)

x = torch.as_tensor(x, dtype=torch.float32, device=device)
y = torch.as_tensor(y, dtype=torch.float32, device=device).unsqueeze(1)

optimizer = torch.optim.Adam(
    model.o_part.parameters(),
    lr=2e-3,
)

optimizer.zero_grad()
prediction = torch.tanh(model.o_part(x))
loss = F.mse_loss(prediction, y)
loss.backward()
optimizer.step()
```

The first `I` has very large values. Change them to values between `0` and `1` before training its part:

```python
x, y = make_batch(
    2048,
    cfg,
    include_regions=("I",),
    stratified=True,
)

x = torch.as_tensor(x, dtype=torch.float32, device=device)
y = (y - cfg.i_grad_min) / (cfg.i_grad_max - cfg.i_grad_min)
y = torch.as_tensor(y, dtype=torch.float32, device=device).unsqueeze(1)

prediction = torch.sigmoid(model.i_part(x))
loss = F.mse_loss(prediction, y)
```

The hard `argmax` in the router does not give a useful gradient to the router. This is why it is easier to train the router and the parts separately.

## Hint: Control the random output

The last `I` needs different outputs for the same point. Use `nn.Dropout` for this.


```python
X, Y = 1, -1  # or maybe other values?

class LastIPart(nn.Module):
    def __init__(self):
        super().__init__()
        self.softmax = nn.Softmax(dim=1)
        self.dropout = nn.Dropout(0.5)
        self.linear = nn.Linear(1, 1)
        self.linear.weight.data = torch.Tensor([[X]])
        self.linear.bias.data = torch.Tensor([[Y]])

    def forward(self, xy):
        o = self.softmax(xy[:, :1])
        o = self.dropout(o)
        o = self.linear(o)
        return o
```
