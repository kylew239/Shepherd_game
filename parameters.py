# Source:
# Strombom D, Mann RP,
# Wilson AM, Hailes S, Morton AJ, Sumpter DJT,
# King AJ. 2014 Solving the shepherding
# problem: heuristics for herding autonomous,
# interacting agents. J. R. Soc. Interface 11:
# 20140719.
# http://dx.doi.org/10.1098/rsif.2014.071

MODEL_PATH = 'model_v3.pth'
# output/render while training (set to False when training on beast GPU server)
OUTPUT = True                   # output detailed game state information to terminal
RENDER = True                   # render pygame
SAVE_TARGET = 60                # save and update target after x games
TARGET_RADIUS = 20              # distance from target to trigger win condition


### Field Parameters
FIELD_LENGTH = 150              # field width and height
FRAME_RESET = 10*FIELD_LENGTH   # automatically reset game after x frames
CLIP = True                     # clip to field boundary


### Agent Parameters
MAX_NUM_AGENTS = 10             # number of agents [0, MAX_NUM_AGENTS]
R_S = 65                        # shepherd detection distance
R_A = 2                         # agent repulsion distance
# P_A > P_C > P_S (eliminate inertial term for discrete setting)

P_A = 2                         # agent repulsion weight
P_C = 1.05                      # LCM attraction weight
P_S = 1                         # shepherd repulsion weight
P_H = 0.5                       # Heading weight
E = 0.3                         # relative strength of angular noise
GRAZE = 0.05                    # Probability of moving per time step while grazing
S_Speed = 1                     # Agent speed


### Shepherding parameters
D_Speed = 1.5                   # Shepherd speed
