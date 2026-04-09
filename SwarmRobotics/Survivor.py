import random
import pygame
class Survivor:

    #radius of all survivors (displayed as circles)
    RADIUS = 10
    #environment boundaries based on UI
    ENVIRONMENT_X_MIN = 220
    ENVIRONMENT_X_MAX = 880
    ENVIRONMENT_Y_MIN = 20
    ENVIRONMENT_Y_MAX = 620

    def __init__(self):
        #initially random positions within the centre area
        self.position = self.random_position()
        self.position_x, self.position_y = self.position[0], self.position[1]
        #
        self.survivor_colour = pygame.Color(0, 0, 255)
        self.found = False
        self.assigned_robot = None
        self.transported = False

    def mark_found(self):
        self.found = True

        #+100 makes it so that it doesnt spawn within safe zone
    def random_position(self):
        #get random number within bounds of environment and considering radius of robot
        position = []
        #get random x value
        position.append(random.randint(self.ENVIRONMENT_X_MIN + self.RADIUS +100, self.ENVIRONMENT_X_MAX - self.RADIUS))
        #get random y value
        position.append(random.randint(self.ENVIRONMENT_Y_MIN + self.RADIUS +100, self.ENVIRONMENT_Y_MAX - self.RADIUS))

        return position

    #getters
    def get_position_x(self):
        return self.position_x

    def get_position_y(self):
        return self.position_y

    def get_position(self):
        return self.position

    def get_found(self):
        self.found = True

    #setters
    def set_position_x(self, new_x):
        self.position_x = new_x
        self.position[0] = new_x

    def set_position_y(self, new_y):
        self.position_y = new_y
        self.position[1] = new_y

    def set_colour(self, survivor_colour):
        self.survivor_colour = survivor_colour

    #draw the survivor instance
    def display_survivor(self, screen):
        pygame.draw.circle(screen, self.survivor_colour, (self.position_x, self.position_y), self.RADIUS)


