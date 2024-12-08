import csv
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

FPS = 15
fpsClock = pygame.time.Clock()
OBSTACLE_COLOR = (139, 69, 19)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


class Game:
    def __init__(self,
                 save_dir: str = None,
                 display_time: bool = False,
                 start_run: Optional[int] = None,
                 seed: Optional[int] = None,
                 random_goal: bool = False,
                 start_in_goal: bool = True,
                 sheep_top_right: bool = True,
                 num_dog: int = 1,
                 num_sheep: int = 5,
                 scaling: int = 5):
        """
        Create a shepherding game instance.

        Args:
            save_dir (str): Directory to save to. If no directory is
                provided, the game will not be saved
            display_time (bool): Display the game time on the window.
                Defaults to False.
            start_run (Optional[int]): Which run number to start on.
                Used with save_dir. Defaults to None.
            seed (Optional[int]): Seed the sheep position. Defaults to None.
            random_goal (bool): Randomize the goal location. Defaults to False.
            start_in_goal (bool): Start the shepherd in the goal location. If
                False, the shepherd will spawn in the bottom left. Defaults to True.
            sheep_top_right (bool): Start the sheep in the top right corner. If
                False, the sheep can spawn anywhere. Defaults to True
            num_dog (int): The number of dogs to spawn. Defaults to 1
            num_agents (int): The number of sheep to spawn. Defaults to 5
            scaling (int): Scaling factor for the pygame display. Defaults to 5
        """
        pygame.init()
        self.padding = np.array(PADDING)

        # Try to get the joystick, use keyboard if error
        try:
            self.joystick = pygame.joystick.Joystick(0)
            self.get_input = self.get_joy_input
        except pygame.error:
            self.get_input = self.get_keyboard_input

        if RENDER:
            self.scale = scaling
            x_size = FIELD_LENGTH+2*self.padding[0]
            y_size = FIELD_LENGTH+2*self.padding[1]
            self.screen =\
                pygame.display.set_mode((x_size * self.scale,
                                         y_size * self.scale))

        self.save = True if save_dir is not None else False
        self.trial = 0 if not start_run else start_run
        self.seed = seed
        self.random_goal = random_goal
        self.start_in_goal = start_in_goal
        self.sheep_top_right = sheep_top_right
        self.num_agents = num_sheep
        self.num_nearest = self.num_agents-1
        self.num_dog = num_dog
        self.dir = save_dir
        if save_dir is not None:
            if not os.path.exists(self.dir):
                os.mkdir(self.dir)

        self.display_time = display_time
        self.reset()

    def reset(self):
        """Reset the game by randomizing locations."""
        # Score and data tracking
        self.pos = []
        self.img_list = []
        self.sheep_pos = []
        self.start_time = time.time()

        # Time display
        self.font = pygame.font.SysFont('Consolas', 20, True)
        self.start_time = pygame.time.get_ticks()

        np.random.seed(self.seed)
        if self.sheep_top_right:
            # Randomely place the sheep in the top right quarter
            self.sheep = np.random.rand(self.num_agents, 2)*FIELD_LENGTH/2
            self.sheep[:, 0] += FIELD_LENGTH/2
        else:
            # Randomly place the sheep anywhere
            self.sheep = np.random.rand(self.num_agents, 2)*FIELD_LENGTH
        CoM = np.mean(self.sheep, axis=0)
        np.random.seed(None)  # Reset the seed

        # Place the target
        if self.random_goal:
            # Randomize but make sure the game isn't "won"
            self.target = np.random.rand(2)*FIELD_LENGTH/2
            self.target[1] += FIELD_LENGTH/2
            while dist(CoM, self.target) < TARGET_RADIUS:
                self.target = np.random.rand(2)*FIELD_LENGTH
        else:
            # Bottom left corner
            self.target = np.array([0, FIELD_LENGTH-1])

        if self.start_in_goal:
            # Randomly place the dog target circle
            th = np.random.uniform(0, 2*np.pi)
            r = TARGET_RADIUS * np.sqrt(np.random.uniform(0, 1))
            self.dog = np.array([np.array([
                r * np.cos(th) + self.target[0],  # x position
                r * np.sin(th) + self.target[1]   # y position
            ]) for _ in range(self.num_dog)])
        else:
            # Randomly place the dog in the bottom left corner
            self.dog = np.random.rand(self.num_dog, 2)*FIELD_LENGTH/2
            self.dog[:, 1] += FIELD_LENGTH/2

        # Heading arrays for sheep movement
        self.heading = np.zeros_like(self.sheep)

        self.dog_dir = np.zeros_like(self.dog)
        self.sheep_dir = np.zeros_like(self.sheep)

    def step(self, direction):
        """
        Calculate one game step.

        Args:
            direction (List): Movement direction of the dog
        """
        assert direction.shape == self.dog.shape, "Wrong number of actions"
        next_heading = np.zeros_like(self.heading)

        # Iterate for each dog
        for idx, dog in enumerate(self.dog):
            # Add direction to the coordinates
            # Update dog position but don't overwrite the reference to self.dog
            dog[:] = self.calculate_movement(dog, direction[idx])

            # Iterate through each sheep to calculate movement
            for i, sheep in enumerate(self.sheep):
                # if sheep is far from dog or if sheep cannot see dog
                if (dist(sheep, dog) > R_S) or self.cannot_see(sheep, dog):
                    # Random chance of moving in any direction / Grazing
                    if np.random.rand() < GRAZE:
                        sheep[:] = self.calculate_movement(sheep, rand_unit())

                # if sheep is close to dog, calculate movement
                else:
                    # repulsion direction away from shepherd
                    dog_repul = unit_vect(sheep, dog)

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
                            seen_sheep[:max(self.num_nearest,
                                            len(seen_sheep))+1], axis=0)
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
                    next_heading[i] += P_C*lcm_attract + \
                        P_A*local_repul + P_S*dog_repul

                    # Update heading to include previous headings
                    next_heading[i] = next_heading[i] + P_H*self.heading[i]

                    self.sheep_dir[i] = next_heading[i]

        # Update sheep location with obstacle clipping
        for idx in range(self.num_agents):
            self.sheep[idx] = self.calculate_movement(
                self.sheep[idx], S_Speed*unit_vect(next_heading[idx]))

        # Update heading for next iteration
        self.heading = next_heading

        if CLIP:
            # Clip the locations to within the field
            self.dog = self.dog.clip(0, FIELD_LENGTH-1)
            self.sheep = self.sheep.clip(0, FIELD_LENGTH-1)

        # Record positions and save frame
        if self.save:
            self.pos.append([pos for dog in self.dog for pos in dog])
            self.sheep_pos.append(
                [pos for sheep in self.sheep for pos in sheep])
            self.img_list.append(pygame.surfarray.array3d(self.screen))

        for sheep in self.sheep:
            if dist(sheep, self.target) > TARGET_RADIUS:
                return False

        # End game if all the sheep are inside the target radius
        return True

    def get_joy_input(self):
        """Key key inputs for game controls using joystick."""
        # Refer to the Controller Mapping section in the README to
        # understand what buttons are being used
        if (self.joystick.get_button(8)):
            return False
        if (self.joystick.get_button(5)):
            self.reset()

        # Get joystick movements
        x = self.joystick.get_axis(3)
        y = self.joystick.get_axis(4)

        # Build movement based on num dog
        if self.num_dog == 1:
            move = np.array([[x, y]])
        elif self.num_dog == 2:
            move = np.array([
                [x, y],
                [self.joystick.get_axis(0), self.joystick.get_axis(1)]
            ])
        else:
            raise NotImplementedError

        return move * D_Speed

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

        # Build movement based on num dog
        if self.num_dog == 1:
            move = np.array([[x, y]])
        elif self.num_dog == 2:
            x2, y2 = 0, 0
            if keys[pygame.K_d]:
                x2 += D_Speed
            if keys[pygame.K_s]:
                y2 += D_Speed
            if keys[pygame.K_a]:
                x2 -= D_Speed
            if keys[pygame.K_w]:
                y2 -= D_Speed
            move = np.array([
                [x, y],
                [x2, y2]
            ])
        else:
            raise NotImplementedError

        # Reset
        if keys[pygame.K_r]:
            self.reset()

        if keys[pygame.K_ESCAPE]:
            return False

        return move

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
        Calculate movement after checking for obstacle collisions.

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

    def render(self, draw: bool = True):
        """
        Render the game window.

        Args:
            draw (bool): Update the pygame display. Defaults to True
        """
        self.screen.fill((19, 133, 16))

        # Target
        target_loc = (self.padding + self.target) * self.scale
        pygame.draw.circle(self.screen, BLACK, target_loc,
                           TARGET_RADIUS * self.scale, 0)

        # Dog
        for idx, each in enumerate(self.dog):
            pos = (self.padding + each) * self.scale
            head = self.dog_dir[idx] * self.scale + pos
            pygame.draw.circle(self.screen, (25, 25, 255),
                               pos, self.scale + 2, 0)
            pygame.draw.polygon(self.screen, (25, 25, 255),
                                triangle(pos, head, self.scale+2))

        # Sheep
        for idx, each in enumerate(self.sheep):
            pos = (self.padding + each) * self.scale
            head = self.sheep_dir[idx] * self.scale + pos
            pygame.draw.circle(self.screen, WHITE,
                               pos, self.scale + 2, 0)
            pygame.draw.polygon(self.screen, WHITE,
                                triangle(pos, head, self.scale+2))

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
        if draw:
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

    def save_data(self):
        """Save the game data to a csv and images."""
        self.data_path = self.dir + f'{self.trial}/'
        self.img_path = self.data_path + "img/"
        self.trial += 1

        os.mkdir(self.data_path)
        os.mkdir(self.img_path)

        with open(self.data_path + 'pos.csv', 'w', newline=''
                  )as csvfile:
            row = np.round(self.pos[0], 3)
            writer = csv.writer(csvfile)
            writer.writerow(row)
            print("total_data: ", len(self.pos))

            # Iterate over each set of points
            for i in range(1, len(self.pos)):
                writer.writerow(np.round(self.pos[i], 3))

        with open(self.data_path + 'sheep_pos.csv', 'w', newline=''
                  )as csvfile:
            row = np.round(self.sheep_pos[0], 3)
            writer = csv.writer(csvfile)
            writer.writerow(row)

            # Iterate over each set of points
            for i in range(1, len(self.sheep_pos)):
                writer.writerow(np.round(self.sheep_pos[i], 3))

        # Save the target
        with open(self.data_path + 'target_pos.csv', 'w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(self.target)

        for idx, pix_array in enumerate(self.img_list):
            img = pygame.surfarray.make_surface(pix_array)
            pygame.image.save(img, self.img_path+f"{idx+1}.bmp")

    def run(self):
        """Main function for running the game."""
        while not RENDER or self.pygame_running():
            if RENDER:
                self.render()

            # Get key input
            action = self.get_input()

            if action is not False:
                # Run each step of the game
                ended = self.step(action)

                for idx in range(action.shape[0]):
                    if dist(action[idx]) > 0.1:
                        self.dog_dir[idx] = action[idx]
            else:
                # Close the game
                break

            # Reset game on reaching goal
            if ended:
                if self.save:
                    self.save_data()
                    print(f"Data saved in {self.data_path}")

                self.reset()

            # Update the game clock
            fpsClock.tick(FPS)


if __name__ == "__main__":
    # Game(save_dir=None, start_run=201, random_goal=False).run()
    # Game(save_dir="data/", start_run=1001, seed=0).run()
    Game(num_dog=1, num_sheep=1).run()
