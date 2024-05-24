# Source:
# Strombom D, Mann RP,
# Wilson AM, Hailes S, Morton AJ, Sumpter DJT,
# King AJ. 2014 Solving the shepherding
# problem: heuristics for herding autonomous,
# interacting agents. J. R. Soc. Interface 11:
# 20140719.
# http://dx.doi.org/10.1098/rsif.2014.071

RENDER = True                   # render pygame

### Field Parameters
FIELD_LENGTH = 150              # field width and height
CLIP = False                     # clip to field boundary
TARGET_RADIUS = 15              # distance from target to trigger win condition

### Agent Parameters
MAX_NUM_AGENTS = 10             # number of agents [0, MAX_NUM_AGENTS]
R_S = 30                        # shepherd detection distance
R_A = 10                        # agent repulsion distance
# P_A > P_C > P_S (eliminate inertial term for discrete setting)

P_A = 2                         # agent repulsion weight
P_C = 1.                      # LCM attraction weight
P_S = 1                         # shepherd repulsion weight
P_H = 0.6                       # Heading weight
E = 0.3                         # relative strength of angular noise
GRAZE = 0.10                    # Probability of moving per time step while grazing
S_Speed = 1                     # Agent speed


### Shepherding parameters
D_Speed = 2                   # Shepherd speed
