import csv
import glob
import math
import os
import time
from typing import Optional

import numpy as np
import pygame
from pygame.locals import *

from shepherd_game import obstacles
from shepherd_game.parameters import *
from shepherd_game.utils import *

FPS = 20
fpsClock = pygame.time.Clock()
OBSTACLE_COLOR = (139, 69, 19)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


class Game:
    def __init__(self,
                 save_dir: str = '',
                 display_time: bool = False,
                 start_run: Optional[int] = None):
        pygame.init()
        self.padding = np.array(PADDING)

        # Try to get the joystick, use keyboard if error
        try:
            self.joystick = pygame.joystick.Joystick(0)
            self.get_input = self.get_joy_input
        except pygame.error:
            self.get_input = self.get_keyboard_input

        if RENDER:
            self.screen =\
                pygame.display.set_mode((FIELD_LENGTH+2*self.padding[0],
                                         FIELD_LENGTH+2*self.padding[1]),
                                        SCALED)

        self.save = True if save_dir else False
        self.dir = save_dir
        self.trial = 0 if not start_run else start_run

        self.display_time = display_time
        self.frame = 0
        self.reset(new_game=True)

    def reset(self, new_game: bool = False):
        """Reset the game by randomizing locations."""
        # Score and data tracking
        self.pos = []
        self.start_time = time.time()

        # New game has been created
        if new_game:
            self.trial += 1
            if self.save:
                self.data_path = self.dir + f'{self.trial}/'
                self.img_path = self.data_path + "img/"

                os.mkdir(self.data_path)
                os.mkdir(self.img_path)

        # reset the game
        if self.frame != 0 and not new_game and self.save:
            # Delete stored data
            files = glob.glob(self.img_path + '*')
            for f in files:
                os.remove(f)

        self.frame = 0

        # Time display
        self.font = pygame.font.SysFont('Consolas', 20, True)
        self.start_time = pygame.time.get_ticks()

        # Generates a random number of agents
        self.num_agents = np.random.randint(2, MAX_NUM_AGENTS+1)
        self.num_nearest = self.num_agents-1

        # Randomly place the dog in the bottom left quarter
        self.dog = np.random.rand(2)*FIELD_LENGTH/2
        self.dog[1] += FIELD_LENGTH/2

        # Randomely place the sheep in the top right quarter
        self.sheep = np.random.rand(self.num_agents, 2)*FIELD_LENGTH/2
        self.sheep[:, 0] += FIELD_LENGTH/2
        self.CoM = np.mean(self.sheep, axis=0)

        # Place the target
        if RANDOMIZE_GOAL:
            # Randomize but make sure the game isn't "won"
            self.target = np.random.rand(2)*FIELD_LENGTH
            while dist(self.CoM, self.target) < TARGET_RADIUS:
                self.target = np.random.rand(2)*FIELD_LENGTH
        else:
            # Bottom left corner
            self.target = np.array([0, FIELD_LENGTH-1])

        # Heading arrays for sheep movement
        self.heading = np.zeros_like(self.sheep)

        # Record positions
        self.pos.append([*self.dog, 0, 0])

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
                    lcm_attract = np.array([0, 0])
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
        self.sheep += S_Speed*next_heading

        # Update heading for next iteration
        self.heading = next_heading

        if CLIP:
            # Clip the locations to within the field
            self.dog = self.dog.clip(0, FIELD_LENGTH-1)
            self.sheep = self.sheep.clip(0, FIELD_LENGTH-1)

        # Record positions and save frame
        self.pos.append([*self.dog, *direction])
        if self.save:
            pygame.image.save(
                self.screen, self.img_path+f"{self.frame}.bmp")
            self.frame += 1

        # End game if CoM of sheep is within the target
        self.CoM = np.mean(self.sheep, axis=0)
        if dist(self.CoM, self.target) < TARGET_RADIUS:
            return True

        return False

    def get_joy_input(self):
        """Key key inputs for game controls using joystick."""
        x, y = 0, 0
        keys = pygame.key.get_pressed()

        # Get joystick movements
        pygame.event.get()
        x = self.joystick.get_axis(3) * D_Speed
        y = self.joystick.get_axis(4) * D_Speed

        # Reset
        if keys[pygame.K_r]:
            self.reset()

        if keys[pygame.K_ESCAPE]:
            return False

        return (x, y)

    def get_keyboard_input(self):
        """Get key inputs for game controls using keyboard."""
        x, y = 0, 0
        keys = pygame.key.get_pressed()

        # Movement
        if keys[pygame.K_RIGHT]:
            x += D_Speed
        if keys[pygame.K_DOWN]:
            y += D_Speed
        if keys[pygame.K_LEFT]:
            x -= D_Speed
        if keys[pygame.K_UP]:
            y -= D_Speed

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
            self.padding + self.target), TARGET_RADIUS, 0)

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
        if self.display_time:
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

    def save_pos(self):
        """self.save the game data to a csv and video"""
        with open(self.data_path + 'pos.csv', 'w', newline=''
                  )as csvfile:
            row = np.round(self.pos[0], 3)
            writer = csv.writer(csvfile)
            writer.writerow(row)
            print("total_data: ", len(self.pos))

            # Iterate over each set of points
            for i in range(1, len(self.pos)):
                writer.writerow(np.round(self.pos[i], 3))

    def run(self, num_runs: Optional[int] = None):
        """
        Main function for running the game.

        Args:
            num_runs (Optional[int]): Number of runs to do. If none, the game
                will keep repeating
        """
        goal_runs = self.trial + num_runs if num_runs else self.trial
        while not RENDER or self.pygame_running():
            if RENDER:
                self.render()

            # Get key input
            action = self.get_input()

            if action:
                # Run each step of the game
                ended = self.step(action)
            else:
                if self.save:
                    # Delete stored data if saved
                    files = glob.glob(self.img_path + '*')
                    for f in files:
                        os.remove(f)

                    os.rmdir(self.img_path)
                    os.rmdir(self.data_path)

                # Close the game
                break

            # Reset game on reaching goal
            if ended:
                if self.save:
                    self.save_pos()
                if num_runs and self.trial >= goal_runs:
                    break

                self.reset(new_game=True)

            # Update the game clock
            fpsClock.tick(FPS)


if __name__ == "__main__":
    # Game(save_dir="data/", start_run=33).run(num_runs=17)
    Game(save_dir="data/", start_run=52).run(num_runs=1)
