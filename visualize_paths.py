import os

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection

from shepherd_game.parameters import FIELD_LENGTH, PADDING


def main(data_dir: str, start: int = 0, end: int = None):
    """
    Generate an image showcasing the paths of the shepherds

    Args:
        data_dir (str): Path where the data is saved
        start (int): Which data folder to start at. Defaults to 0
        end (int or None): Which data folder to stop at. If none, it will use
            all of the data. Defaults to None
    """
    fig, ax = plt.subplots()

    # Colormap for the paths drawn
    cmap = plt.get_cmap('plasma')  # Choose a colormap
    norm = plt.Normalize(0, 1)  # Normalize to [0, 1]

    # Build a list of data directories to check
    dir_list = sorted(os.listdir(data_dir), key=int)
    if end is not None:
        dir_list = dir_list[start:end]

    # Draw each path
    for dir in dir_list:
        # Read the points and convert into line segments
        data = np.loadtxt(data_dir + dir + "/pos.csv",
                          delimiter=',', skiprows=0)[:, :2]
        points = np.array([data[:, 0], data[:, 1]]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)

        # Normalized values
        colors = np.linspace(0, 1, segments.shape[0])

        # Create a LineCollection
        lc = LineCollection(segments, cmap=cmap, norm=norm)
        lc.set_array(colors)
        lc.set_linewidth(1)
        ax.add_collection(lc)

    # Set limits and aspect
    ax.set_xlim(-PADDING[0], FIELD_LENGTH + PADDING[0])
    ax.set_ylim(-PADDING[1], FIELD_LENGTH + PADDING[1])
    ax.set_aspect('equal', 'box')

    # Add grid and labels
    ax.grid(True)
    plt.title("Plot of trajectories")
    plt.xlabel("X Position")
    plt.ylabel("Y Position")

    # Display the plot
    ax.invert_yaxis()
    plt.show()


if __name__ == "__main__":
    main("data/", end=20)
