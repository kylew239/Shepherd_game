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
OUTPUT = True       # output detailed game state information to terminal
RENDER = True       # render pygame
SAVE_TARGET = 60    # save and update target after x games

FIELD_LENGTH = 120      # field width and height
FRAME_RESET = 10*FIELD_LENGTH   # automatically reset game after x frames
CLIP = True            # clip to field boundary
MAX_NUM_AGENTS = 5      # number of agents [0, MAX_NUM_AGENTS]
R_S = 25        # shepherd detection distance
R_A = 2     # agent repulsion distance
TARGET_RADIUS = 20     # distance from target to trigger win condition
# P_A > P_C > P_S (eliminate inertial term for discrete setting)
P_A = 2     # agent repulsion weight
P_C = 1.2    # LCM attraction weight
P_S = 1     # shepherd repulsion weight
