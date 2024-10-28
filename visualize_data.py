import os

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import pygame
from matplotlib.collections import LineCollection

from shepherd_game.game import Game
from shepherd_game.parameters import FIELD_LENGTH, PADDING, TARGET_RADIUS


def main(data_dir: str, seed: int = None, end: int = None):
    """
    Generate an image showcasing the paths of the shepherd

    Args:
        data_dir (str): Path where the data is saved
        seed (int or None): Seed to use for agent generation
        end (int or None): Which data folder to stop at
    """
    # Use the game to get the field and positions
    env = Game(seed=seed)
    target_pos = env.target
    sheep_pos = env.sheep

    # Close and delete the pygame window
    pygame.quit()
    del env

    fig, ax = plt.subplots()

    # Draw goal
    ax.add_patch(patches.Circle(target_pos, TARGET_RADIUS, edgecolor='Black',
                                facecolor='Black', linewidth=0))

    # Draw sheep
    for sheep in sheep_pos:
        ax.add_patch(patches.Circle(sheep, 2, edgecolor='Grey',
                                    facecolor='Grey', linewidth=0))

    # Colormap for the paths drawn
    cmap = plt.get_cmap('plasma')  # Choose a colormap
    norm = plt.Normalize(0, 1)  # Normalize to [0, 1]

    # Build a list of data directories to check
    dir_list = sorted(os.listdir(data_dir), key=int)
    if end is not None:
        dir_list = dir_list[:end]

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
    main("test/", 0, end=120)
