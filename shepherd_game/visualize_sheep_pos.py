import os

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np

from shepherd_game.parameters import FIELD_LENGTH, PADDING


def main(data_dir: str, start: int = 0, end: int = None):
    """
    Generate an image showcasing the spawn positions of the sheep and goals

    Args:
        data_dir (str): Path where the data is saved
        start (int): Which data folder to start at. Defaults to 0
        end (int or None): Which data folder to stop at. If none, it will use
            all of the data. Defaults to None
    """
    # Build a list of data directories to check
    dir_list = sorted(os.listdir(data_dir), key=int)
    if end is not None:
        dir_list = dir_list[start:end]
    else:
        dir_list = dir_list[start]

    goals = []
    sheep = []
    for dir in dir_list:
        goals.append(np.loadtxt(data_dir + dir + "/pos.csv",
                                delimiter=',', skiprows=0)[0, 7:9])
        sheep.append(np.loadtxt(data_dir + dir + "/sheep_pos.csv",
                                delimiter=',', skiprows=0)[0, :])

    # # Plot and display goals
    fig, ax = plt.subplots()
    x_coords = [point[0] for point in goals]
    y_coords = [point[1] for point in goals]
    plt.scatter(x_coords, y_coords, c='black')

    # Plot and display sheep positions
    x_coords = []
    y_coords = []

    # Loop through each array of points and extract x and y coordinates
    for point_array in sheep:
        # Take every other element starting from index 0 (x)
        x_coords.extend(point_array[::2])
        # Take every other element starting from index 1 (y)
        y_coords.extend(point_array[1::2])

    # Create a scatter plot
    plt.scatter(x_coords, y_coords, c='blue')

    # Set limits and aspect
    ax.set_xlim(-PADDING[0], FIELD_LENGTH + PADDING[0])
    ax.set_ylim(-PADDING[1], FIELD_LENGTH + PADDING[1])
    ax.set_aspect('equal', 'box')

    # Legend
    goal_patch = mpatches.Patch(color='black', label='Goal')
    sheep_patch = mpatches.Patch(color='blue', label='Sheep')
    plt.legend(handles=[goal_patch, sheep_patch])

    # Add grid and labels
    ax.grid(True)
    plt.title("Plot of positions")
    plt.xlabel("X Position")
    plt.ylabel("Y Position")

    # Display the plot
    ax.invert_yaxis()
    plt.show()


if __name__ == '__main__':
    main(data_dir='data/', start=100, end=200)
