import torch.nn as nn

class CustomModel(nn.Module):
    def __init__(self, hidden, dropout: float = 0.0):
        super().__init__()
        layers = []
        in_dim = 2
        for h in hidden:
            layers.append(nn.Linear(in_dim, h))
            layers.append(nn.ReLU())
            if dropout > 0.0:
                layers.append(nn.Dropout(dropout))
            in_dim = h
        layers.append(nn.Linear(in_dim, 1))
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x)