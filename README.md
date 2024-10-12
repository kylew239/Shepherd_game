# Shephereding Pygame
This repository contains code for playing shephereding game. The goal is the control the shepherd (dog, blue circle) to herd the sheep (white circles) into the target zone (black circle). The game is "won" when the center of mass of the sheep (grey circle with a black border) reaches the goal area. The sheep behave as described by the [Strombom model](https://royalsocietypublishing.org/doi/10.1098/rsif.2014.0719)

# Features
This game features additional capabilities and parameters that are easy for the player to tune.
- Paramter Tuning: Can be changed in the [`parameters.py`](parameters.py) file
- Obstacles
    - Sheep will not "see" each other or the shephered if there is an obstacle in the way
    - Sheep and shepherd will slide along the obstacles if there is a collision
    - There is support for circular and linear obstacles
    - Obstacles can be added in the [`obstacles.py`](obstacles.py) file
- Data Saving
    - Saves the shepherd position and game state as a bmp in the following format:
```
ws
├── data                # Contains data for each game run
│   └── 1  
│       └── img         # Contains the image at each frame, as a bmp
│           └── 0.bmp
│           └── 1.bmp
│           └── ...
│       └── pos.csv     # Contains the shepherd positions, as (x,y) per frame
│   └── 2  
└── Shepherd_game       # this repo
```
- pygame autoscaling
    - The game will be automatically scaled up
    - Saved data images will remain at the original size


# Dependencies
The game has been successfully run in the following environment:

## Hardware
- xbox one controller
- USB keyboard

## Software:
- Ubuntu 22.04.3 LTS, 64-bit
- A python virtual environment described in [this repository]()
    - The game can be run with just the following `pip` packages
        - `numpy==1.26.4`
        - `pygame==2.1.2`
    