import pygame
import numpy as np
from parameters import *
from functools import reduce
import time
import csv
from utils import *

FPS = 60
fpsClock = pygame.time.Clock()


class Environment:
    def __init__(self):
        self.padding = np.array([30, 30])
        if RENDER:
            pygame.init()
            self.screen = pygame.display.set_mode((FIELD_LENGTH+2*self.padding[0],
                                                   FIELD_LENGTH+2*self.padding[1]))
        self.reset()

        # Game Params
        self.movespeed = 1.9

    def reset(self):
        """Reset the game by randomizing locations."""
        # Score and data tracking
        self.pos = []
        self.start_time = time.time()
        self.trav = []

        # TODO: Generates a random number of agents
        self.num_agents = np.random.randint(1, MAX_NUM_AGENTS+1)
        self.num_nearest = self.num_agents-1

        # Randomly place the dog
        self.dog = np.random.rand(2)*FIELD_LENGTH

        # Place the target in the bottom right corner
        self.target = np.array([FIELD_LENGTH-1, FIELD_LENGTH-1])

        # Randomely place the sheep
        self.sheep = R_S//2 + FIELD_LENGTH*.5 * \
            np.random.rand(self.num_agents, 2)

        # Record positions
        self.pos.append([self.dog, *self.sheep])

    def step(self, direction):
        """
        Calculate one game step.

        Args:
            direction (List): Movement direction of the dog
        """
        # Add direction to the coordinates
        self.dog += np.array(direction)

        # For each sheep, calculate distance to all the other sheep
        distances = [[dist(self.sheep[i], self.sheep[j]) if i < j else 0 for j in range(self.num_agents)]
                     for i in range(self.num_agents)]

        # Update movement for each sheep
        for i in range(self.num_agents):
            # local repulsion
            v_sheep_ = [unit_vect(self.sheep[i], self.sheep[j]) for j in range(self.num_agents)
                        if i != j and distances[min(i, j)][max(i, j)] < R_A]

            # if two agents in same location, unit_vect returns zero; need to map to random unit vector
            for v_index in range(len(v_sheep_)):
                if (v_sheep_[v_index] == 0).all():
                    v_sheep_[v_index] = rand_unit()
            v_sheep = 0 if len(v_sheep_) == 0 else unit_vect(
                reduce(np.add, v_sheep_))

            if (dist(self.dog, self.sheep[i]) < R_S):
                # agent outside of dog detection radius, only consider local repulsion
                # self.sheep[i] += unit_vect(v_sheep)
                # TODO: Doesn't do anything?
                pass
            else:
                # attracted to local center of mass of nearest agents (ignore self at index 0)
                v_COM = 0
                if self.num_nearest > 0:
                    # sort based on distance
                    sorted_agents = sorted(
                        self.sheep, key=lambda x: dist(self.sheep[i], x))

                    # ignore self at index 0
                    nearest_agents = sorted_agents[1:self.num_nearest+1]
                    com = reduce(np.add, nearest_agents)/self.num_nearest
                    v_COM = unit_vect(com, self.sheep[i])

                # repelled from dog (if in same location, run towards center of board)
                v_s = unit_vect(self.sheep[i], self.dog)
                if (v_s == 0).all():
                    v_s = unit_vect(
                        np.array([FIELD_LENGTH/2, FIELD_LENGTH/2]), self.sheep[i])

                self.sheep[i] = self.sheep[i] + \
                    unit_vect(P_A*v_sheep + P_C*v_COM + P_S*v_s)

        if CLIP:
            # Clip the locations to within the field
            self.dog = self.dog.clip(0, FIELD_LENGTH-1)
            self.sheep = self.sheep.clip(0, FIELD_LENGTH-1)

        # Record positions
        self.pos.append([self.dog, *self.sheep])

        # End game if all sheep are within the target
        max_agent_dist = max([dist(a, self.target) for a in self.sheep])
        if max_agent_dist < TARGET_RADIUS:
            return True

        return False

    def get_key_input(self):
        """Get key inputs for game controls."""
        x, y = 0, 0
        keys = pygame.key.get_pressed()

        # Movement
        if keys[pygame.K_RIGHT]:
            x += self.movespeed
        if keys[pygame.K_DOWN]:
            y += self.movespeed
        if keys[pygame.K_LEFT]:
            x -= self.movespeed
        if keys[pygame.K_UP]:
            y -= self.movespeed

        # Reset
        if keys[pygame.K_r]:
            self.reset()

        if keys[pygame.K_ESCAPE]:
            return False

        return (x, y)

    def render(self):
        """Render the game window."""
        self.screen.fill((19, 133, 16))

        # Dog
        pygame.draw.circle(self.screen, (255, 0, 0), tuple(
            self.padding + self.dog), 3, 0)

        # Goal
        pygame.draw.circle(self.screen, (0, 0, 0),
                           tuple(self.padding + self.target), 3, 0)

        # Sheep
        [pygame.draw.circle(self.screen, (255, 255, 255), tuple(self.padding + a), 3, 0)
            for a in self.sheep]

        # Update display
        pygame.display.update()

    def pygame_running(self):
        """
        Checks if pygame is still running.

        Useful for if the user manually closes the window
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True

    def save(self):
        """Save the data to a csv."""
        game_time = time.time() - self.start_time
        with open("{:.3f}".format(game_time) + '.csv', 'w', newline='') as csvfile:
            prev_row = np.round(self.pos[0], 3)
            writer = csv.writer(csvfile)
            writer.writerow(prev_row)

            # Iterate over each set of points
            for i in range(1, len(self.pos)):
                row = np.round(self.pos[i], 3)

                # Don't write duplicates
                if not np.array_equal(row, prev_row):
                    writer.writerow(row)

                prev_row = row

    def run(self):
        """Main function for running the game."""
        while not RENDER or self.pygame_running():
            if RENDER:
                self.render()

            # Get key input
            action = self.get_key_input()

            if action:
                # Run each step of the game
                ended = self.step(action)
            else:
                # If no action, end the game
                break

            # Reset game on reaching goal
            if ended:
                # self.save() # TODO: Uncomment
                self.reset()

            # Update the game clock
            fpsClock.tick(FPS)


if __name__ == "__main__":
    Environment().run()
