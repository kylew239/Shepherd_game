import csv
import math
import time
from typing import Optional

import numpy as np
import obstacles
import pygame
from parameters import *
from pygame.locals import *
from utils import *

FPS = 20
fpsClock = pygame.time.Clock()
OBSTACLE_COLOR = (139, 69, 19)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


class Game:
    def __init__(self):
        self.padding = np.array([40, 40])
        # self.joystick = pygame.joystick.Joystick(0)
        if RENDER:
            pygame.init()
            self.screen =\
                pygame.display.set_mode((FIELD_LENGTH+2*self.padding[0],
                                         FIELD_LENGTH+2*self.padding[1]),
                                        SCALED)

        self.reset()

    def reset(self):
        """Reset the game by randomizing locations."""
        # Score and data tracking
        self.pos = []
        self.start_time = time.time()
        self.trav = []

        # Time display
        self.font = pygame.font.SysFont('Consolas', 20, True)
        self.start_time = pygame.time.get_ticks()

        # TODO: Generates a random number of agents
        self.num_agents = np.random.randint(2, MAX_NUM_AGENTS+1)
        self.num_nearest = self.num_agents-1

        # Randomly place the dog in the bottom left quarter
        self.dog = np.random.rand(2)*FIELD_LENGTH/2
        self.dog[1] += FIELD_LENGTH/2

        # Place the target in the bottom left corner
        self.target = np.array([0, FIELD_LENGTH-1])

        # Randomely place the sheep in the top right quarter
        self.sheep = np.random.rand(self.num_agents, 2)*FIELD_LENGTH/2
        self.sheep[:, 0] += FIELD_LENGTH/2
        self.CoM = np.mean(self.sheep, axis=0)

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
        # TODO: Turn into unit or smaller?
        self.dog = self.calculate_movement(self.dog, direction)

        # Iterate through each sheep to calculate movement
        for i, sheep in enumerate(self.sheep):
            # if sheep is far from dog or if sheep cannot see dog
            if (dist(sheep, self.dog) > R_S) or self.cannot_see(sheep, self.dog):
                # Random chance of moving in any direction / Grazing
                if np.random.rand() < GRAZE:
                    sheep[:] = self.calculate_movement(sheep, rand_unit())

            # if sheep is close to dog, calculate movement
            else:
                # repulsion direction away from shepherd
                dog_repul = unit_vect(sheep, self.dog)

                # Sort sheep based on distance
                nearest_sheep = sorted(
                    self.sheep, key=lambda x: dist(sheep, x))[1:]

                # Remove sheep that cannot be seen
                seen_sheep = []
                for neighbor in nearest_sheep:
                    if not self.cannot_see(sheep, neighbor):
                        seen_sheep.append(neighbor)

                # attraction to LCM
                if len(seen_sheep) == 0:
                    lcm_attract = np.array([0,0])
                else:
                    LCM = np.mean(
                        seen_sheep[:max(self.num_nearest, len(seen_sheep))+1], axis=0)
                    lcm_attract = unit_vect(LCM, sheep)

                # Filter sheep that are within a certain distance
                neighbor_sheep = []
                for neighbor in seen_sheep:
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

        # Update sheep location with obstacle clipping
        for index, sheep in enumerate(self.sheep):
            self.sheep[index] = self.calculate_movement(
                sheep, S_Speed*next_heading[index])
        # self.sheep += S_Speed*next_heading

        # Update heading for next iteration
        self.heading = next_heading

        if CLIP:
            # Clip the locations to within the field
            self.dog = self.dog.clip(0, FIELD_LENGTH-1)
            self.sheep = self.sheep.clip(0, FIELD_LENGTH-1)

        # Record positions
        self.pos.append([self.dog, *self.sheep])

        # End game if CoM of sheep is within the target
        self.CoM = np.mean(self.sheep, axis=0)
        if dist(self.CoM, self.target) < TARGET_RADIUS:
            return True

        return False

    def get_key_input(self):
        """Get key inputs for game controls."""
        x, y = 0, 0
        keys = pygame.key.get_pressed()

        # # Movement
        if keys[pygame.K_RIGHT]:
            x += D_Speed
        if keys[pygame.K_DOWN]:
            y += D_Speed
        if keys[pygame.K_LEFT]:
            x -= D_Speed
        if keys[pygame.K_UP]:
            y -= D_Speed

        # Get joystick movements
        # pygame.event.get()
        # x = self.joystick.get_axis(3)
        # y = self.joystick.get_axis(4)

        # Reset
        if keys[pygame.K_r]:
            self.reset()

        if keys[pygame.K_ESCAPE]:
            return False

        return (x, y)

    def cannot_see(self,
                   point1: np.ndarray,
                   point2: np.ndarray) -> bool:
        """
        Checks to see if two objects (sheep or dog) can see each other.

        Args:
            point1 (np.ndarray): Object 1
            point2 (np.ndarray): Object 2

        Returns:
            bool: True if there are obstacles directly in between
        """
        # Check line obstacles
        for line in obstacles.lines:
            if line_intersects(point1, point2, line.start, line.end):
                return True

        # Check circle obstacles
        for circle in obstacles.circles:
            if circle_intersects(point1, point2, circle.center, circle.radius):
                return True

        return False

    def calculate_movement(self,
                           start: np.ndarray,
                           movement: np.ndarray) -> np.ndarray:
        """
        Calculate movement after checking for obstacle collisions

        Args:
            start (np.ndarray): Starting point
            movement (np.ndarray): Direction of Travel

        Returns:
            np.ndarray: New position
        """
        end = start + movement

        # Check line obstacles
        for line in obstacles.lines:
            if line_intersects(start, end, line.start, line.end):
                # Projection of movement onto the line obstacle
                vec_movement = np.array([end[0] - start[0], end[1] - start[1]])
                vec_obstacle = np.array(
                    [line.end[0] - line.start[0], line.end[1] - line.start[1]])
                proj = np.dot(vec_movement, vec_obstacle) / \
                    np.linalg.norm(vec_obstacle)

                # Calculate new position by getting the projection vector and adding to start
                return start + (proj * unit_vect(vec_obstacle))

        # Check circle obstacles
        for circle in obstacles.circles:
            if circle_intersects(start, end, circle.center, circle.radius):
                # Calculate collision slide
                coll_ang = math.atan2(
                    end[1] - circle.center[1], end[0] - circle.center[0])

                return np.array([
                    circle.center[0] + circle.radius * math.cos(coll_ang),
                    circle.center[1] + circle.radius * math.sin(coll_ang),
                ])

        return end

    def render(self):
        """Render the game window."""
        self.screen.fill((19, 133, 16))

        # Target Radius
        pygame.draw.circle(self.screen, BLACK, tuple(
            self.padding + self.target), TARGET_RADIUS, 4)

        # Goal
        pygame.draw.circle(self.screen, BLACK,
                           tuple(self.padding + self.target), 3, 0)

        # Dog
        pygame.draw.circle(self.screen, (25, 25, 255), tuple(
            self.padding + self.dog), 2, 0)

        # Sheep
        [pygame.draw.circle(self.screen, WHITE, tuple(self.padding + a), 3, 0)
            for a in self.sheep]
        pygame.draw.circle(self.screen, BLACK,
                           tuple(self.padding + self.CoM), 4, 0)
        pygame.draw.circle(self.screen, (200, 200, 200),
                           tuple(self.padding + self.CoM), 2, 0)

        # Draw obstacles
        for circle in obstacles.circles:
            pygame.draw.circle(self.screen, OBSTACLE_COLOR, tuple(
                circle.center + self.padding), circle.radius)

        for line in obstacles.lines:
            pygame.draw.aaline(self.screen, OBSTACLE_COLOR, tuple(
                line.start + self.padding), tuple(line.end + self.padding))

        # Time
        time_passed = (pygame.time.get_ticks() - self.start_time)/1000
        message = 'Seconds: ' + str(time_passed)
        self.screen.blit(self.font.render(message, True, BLACK), (0, 0))

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
        with open("{:.3f}".format(game_time) + '.csv', 'w', newline=''
                  )as csvfile:
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
                self.save() # TODO: Uncomment
                self.reset()

            # Update the game clock
            fpsClock.tick(FPS)


if __name__ == "__main__":
    Game().run()
