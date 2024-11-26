# Shepherding Pygame
This repository contains code for playing shephereding game. The goal is the control the shepherd (dog, blue circle) to herd the sheep (white circles) into the target zone (black circle). The game is "won" when the center of mass of the sheep (grey circle with a black border) reaches the goal area. The sheep behave as described by the [Strombom model](https://royalsocietypublishing.org/doi/10.1098/rsif.2014.0719)

# Table of Contents
1. [Quickstart](README.md#quickstart)
2. [Features](README.md#features)
3. [Data Visualization](README.md#data-visualization)
4. [Dependencies](README.md#dependencies)
5. [Controller Mapping](README.md#controller-mapping)


# Quickstart
1. Create a `ws` folder and clone this repo into it. Refer to the diagram [in Features](#features)

2. Install pygame using `pip install pygame`

3. Create the `data/` folder in the `ws`

4. Add the package to your python path. You may need to do this everytime you reopen the terminal
```
export PYTHONPATH=.:$PYTHONPATH

# OR

export PYTHONPATH=~/ws/:$PYTHONPATH
```

5. OPTIONAL: Setup up your controller. You can also use the arrow keys on a standard keyboard

6. Edit parameters and/or save information. Run the game from `ws` using `python3 shepherd_game/game.py`

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
├── data                    # Contains data for each game run
│   └── 1  
│       └── img             # Contains the image at each frame, as a bmp
│           └── 0.bmp
│           └── 1.bmp
│           └── ...
│       └── pos.csv         # Contains the shepherd positions per frame
│       └── sheep_pos.csv   # Contains the sheep positions per frame
│   └── 2  
└── Shepherd_game           # this repo
```
- pygame autoscaling
    - The game will be automatically scaled up
    - Saved data images will remain at the original size

# Data Visualization
Some data visualization tools are included. These are setup to use the same format that the data is saved in

- `visualize_paths.py` will graph the path that the shepherds take
    - Start of the path is Purple, end of the path is Yellow
    - Can specify which trial to start and stop at for displaying data
    - Only supports 1 shepherd as of now
    ![](media/example_paths.png)
- `visualize_sheep_pos.py` will graph the positions that the sheep and dog spawn in
    - Sheep are blue, goals are black
    - Can specify which trial to start and stop at for displaying data
    ![](media/example_pos.png)

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
    
# Controller mapping
These are the mappings on my controller. I am using an xBox One Wireless controller, connected through a USB C Cable. You can run `python3 shepherd_game/joy.py` to see if your controller has the same mappings.

## Buttons
- 0: A
- 1: B
- 2: X
- 3: Y
- 4: Left button
- 5: Right Button
- 6: Toggle View (Center Left)
- 7: Menu Button (Center Right)
- 8: xBox button (Center Top, xBox logo)
- 9: Left Joystick Press
- 10: Right Joystick Press
- 11: Center Bottom Button

## Joystick Axis
- 0: Left Joystick, Horizontal (Left is negative)
- 1: Left Joystick, Vertical (Up is negative)
- 2: Left Trigger
- 3: Right Joystick, Horizontal (Left is negative)
- 4: Right Joystick, Vertical (Up is negative)
- 5: Right Trigger

## Joystick Hat
This is the d-pad. Example usage:
```
pygame.init()
joystick = pygame.joystick.Joystick(0)
joystick.get_hat(0)
```
`joystick.get_hat()` returns a tuple, where the first value represents the x-axis and the second value represents the y-axis. Left and Down are negative, while Right and Up are positive
