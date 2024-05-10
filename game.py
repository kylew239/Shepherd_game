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

        # Game params
        # TODO: too slow for irl
        self.dog_speed = D_Speed
        self.sheep_speed = S_Speed

    def reset(self):
        """Reset the game by randomizing locations."""
        # Score and data tracking
        self.pos = []
        self.start_time = time.time()
        self.trav = []

        # TODO: Generates a random number of agents
        self.num_agents = np.random.randint(1, MAX_NUM_AGENTS+1)
        self.num_nearest = self.num_agents-1

        # Randomly place the dog in the bottom left quarter
        self.dog = np.random.rand(2)*FIELD_LENGTH/2
        self.dog[1] += FIELD_LENGTH/2

        # Place the target in the bottom left corner
        self.target = np.array([0, FIELD_LENGTH-1])

        # Randomely place the sheep in the top right quarter
        self.sheep = np.random.rand(self.num_agents, 2)*FIELD_LENGTH/2
        self.sheep[:, 0] += FIELD_LENGTH/2

        # Heading arrays for sheep movement
        self.heading = np.zeros_like(self.sheep)

        # Record positions
        self.pos.append([self.dog, *self.sheep])

    def step(self, direction):
        """
        Calculate one game step.

        Args:
            direction (List): Movement direction of the dog
        """
        next_heading = np.zeros_like(self.heading)

        # Add direction to the coordinates
        self.dog += np.array(direction)

        # Iterate through each sheep to calculate movement
        for i, sheep in enumerate(self.sheep):
            # if sheep is far from dog, graze with a small chance of movement
            if dist(sheep, self.dog) > R_S:
                # Random chance of moving in any direction
                if np.random.rand() < GRAZE:
                    sheep += rand_unit()

            # if sheep is close to dog, calculate movement
            else:
                # repulsion direction away from shepherd
                dog_repul = unit_vect(sheep, self.dog)

                # calculate LCM by sorting sheep based on distance
                nearest_sheep = sorted(
                    self.sheep, key=lambda x: dist(sheep, x))[1:]
                LCM = np.mean(nearest_sheep[:self.num_nearest+1], axis=0)

                # attraction to LCM
                lcm_attract = unit_vect(LCM, sheep)

                # Filter sheep that are within a certain distance
                neighbor_sheep = []
                for neighbor in nearest_sheep:
                    if dist(sheep, neighbor) <= R_A:
                        neighbor_sheep.append(neighbor)
                    else:
                        break

                # Calculate local repulsion
                local_repul = np.zeros(2)
                for neighbor in neighbor_sheep:
                    local_repul += unit_vect(sheep, neighbor)
                local_repul = unit_vect(local_repul)

                # Calculate heading agent using local attractions
                next_heading[i] = P_C*lcm_attract + \
                    P_A*local_repul + P_S*dog_repul

        # Update heading to include previous headings
        next_heading = next_heading + P_H*self.heading

        # Update sheep location
        self.sheep += self.sheep_speed*next_heading

        # Update heading for next iteration
        self.heading = next_heading

        # TODO: Not in strombom
        if CLIP:
            # Clip the locations to within the field
            self.dog = self.dog.clip(0, FIELD_LENGTH-1)
            self.sheep = self.sheep.clip(0, FIELD_LENGTH-1)

        # Record positions
        self.pos.append([self.dog, *self.sheep])

        # End game if CoM of sheep is within the target
        if dist(np.mean(self.sheep, axis=0), self.target) < TARGET_RADIUS:
            return True

        return False

    def get_key_input(self):
        """Get key inputs for game controls."""
        x, y = 0, 0
        keys = pygame.key.get_pressed()

        # Movement
        if keys[pygame.K_RIGHT]:
            x += self.dog_speed
        if keys[pygame.K_DOWN]:
            y += self.dog_speed
        if keys[pygame.K_LEFT]:
            x -= self.dog_speed
        if keys[pygame.K_UP]:
            y -= self.dog_speed

        # Reset
        if keys[pygame.K_r]:
            self.reset()

        if keys[pygame.K_ESCAPE]:
            return False

        return (x, y)

    def render(self):
        """Render the game window."""
        self.screen.fill((181, 179, 172))
        pygame.draw.rect(self.screen,
                         (19, 133, 16),
                         (self.padding[0], self.padding[1], FIELD_LENGTH, FIELD_LENGTH))

        # Target Radius
        pygame.draw.circle(self.screen, (0, 0, 0), tuple(
            self.padding + self.target), TARGET_RADIUS, 4)

        # Borders
        pygame.draw.rect(self.screen,
                         (181, 179, 172),
                         (0, FIELD_LENGTH, self.padding[0], self.padding[1]*2))
        pygame.draw.rect(self.screen,
                         (181, 179, 172),
                         (0, FIELD_LENGTH+self.padding[1], self.padding[0]*2, self.padding[1]))

        # Goal
        pygame.draw.circle(self.screen, (0, 0, 0),
                           tuple(self.padding + self.target), 3, 0)

        # Dog
        pygame.draw.circle(self.screen, (25, 25, 255), tuple(
            self.padding + self.dog), 3, 0)

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
