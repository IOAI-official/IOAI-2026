import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap


DATASET = Path("dataset")

COLOURS = {
    0: "#e53935",
    1: "#43a047",
    2: "#1e88e5",
    3: "#8e24aa",
    4: "#fdd835",
    5: "#9e9e9e",
}
COLOUR_NAMES = {
    0: "red",
    1: "green",
    2: "blue",
    3: "purple",
    4: "yellow",
    5: "grey",
}
OBJECT_NAMES = {5: "key", 6: "ball", 7: "box", 11: "token"}
OBJECT_MARKERS = {
    5: ("$K$", 300),
    6: ("o", 500),
    7: ("s", 500),
    11: ("*", 550),
}
ROBOT_MARKERS = {0: "^", 1: "v", 2: "<", 3: ">"}
DIRECTIONS = {0: "up", 1: "down", 2: "left", 3: "right"}
ACTIONS = {
    0: "move up",
    1: "move down",
    2: "move left",
    3: "move right",
    4: "pick up",
    5: "drop",
}


def _read_json(path):
    with open(path) as file:
        return json.load(file)


DATA = {
    split: (
        _read_json(DATASET / split / "observations.json"),
        _read_json(DATASET / split / "labels.json"),
    )
    for split in ("train", "test_public")
}


def show_scene(split, index):
    observations, labels = DATA[split]
    observation = observations[index]
    image = np.asarray(observation["image"])
    objects, colours = image[..., 0], image[..., 1]

    _, (ax, legend_ax) = plt.subplots(
        1,
        2,
        figsize=(9, 6),
        gridspec_kw={"width_ratios": [4, 1.6]},
    )
    background = np.where(objects == 2, 0, 1)
    ax.imshow(
        background,
        cmap=ListedColormap(["#4a4a4a", "#ffffff"]),
        vmin=0,
        vmax=1,
    )

    for object_id, (marker, size) in OBJECT_MARKERS.items():
        rows, columns = np.where(objects == object_id)
        object_colours = [
            COLOURS[int(colours[row, column])] for row, column in zip(rows, columns)
        ]
        ax.scatter(
            columns,
            rows,
            marker=marker,
            s=size,
            c=object_colours,
            edgecolors="black",
            linewidths=1.5,
        )

    robot_row, robot_column = np.argwhere(objects == 10)[0]
    ax.scatter(
        robot_column,
        robot_row,
        marker=ROBOT_MARKERS[observation["direction"]],
        s=600,
        c="white",
        edgecolors="black",
        linewidths=2,
    )

    carrying = observation["carrying"]
    carrying_text = (
        "nothing"
        if carrying is None
        else f"{COLOUR_NAMES[carrying[1]]} {OBJECT_NAMES[carrying[0]]}"
    )
    action = labels[index]

    ax.set_title(observation["mission"], fontsize=13, pad=12)
    ax.set_xlabel(
        f"scene {index} | robot {observation['robot_id']} | "
        f"facing {DIRECTIONS[observation['direction']]} | carrying {carrying_text}\n"
        f"correct action: {action} — {ACTIONS[action]}",
        labelpad=10,
    )
    ax.set_xticks(range(8))
    ax.set_yticks(range(8))
    ax.set_xticks(np.arange(-0.5, 8, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, 8, 1), minor=True)
    ax.grid(which="minor", color="#bdbdbd", linewidth=1)
    ax.tick_params(which="minor", bottom=False, left=False)

    legend_ax.set_title("Legend", fontsize=13, pad=12)
    legend_ax.set_xlim(0, 1)
    legend_ax.set_ylim(0, 7)
    legend_ax.axis("off")

    legend_items = [
        ("^", 600, "Robot"),
        ("$K$", 300, "Key"),
        ("o", 500, "Ball"),
        ("s", 500, "Box"),
        ("*", 550, "Token"),
        ("s", 650, "Wall"),
    ]
    legend_colours = ["white", "#9e9e9e", "#9e9e9e", "#9e9e9e", "#9e9e9e", "#4a4a4a"]

    for row, ((marker, size, label), colour) in enumerate(
        zip(legend_items, legend_colours), start=1
    ):
        y = 7 - row
        legend_ax.scatter(
            0.16,
            y,
            marker=marker,
            s=size,
            c=colour,
            edgecolors="black",
            linewidths=1.5,
        )
        legend_ax.text(0.34, y, label, va="center", fontsize=10)

    legend_ax.text(
        0,
        0.15,
        "Symbol colour = object colour",
        fontsize=9,
        color="#555555",
    )
    plt.tight_layout()
    plt.show()
