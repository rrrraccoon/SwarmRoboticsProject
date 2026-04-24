import math

import pygame

class Obstacles:
    def __init__(self, option):

        self.obstacles = []
        self.colour = pygame.Color(0,0,0)

        #create obstacles based on option user chose (1 or 2)
        if option == 1:
            self.obstacles = [pygame.Rect(600, 150, 30, 30),
                         pygame.Rect(400, 300, 30, 30),
                         pygame.Rect(550, 500, 30, 30),
                         pygame.Rect(550, 400, 30, 30),
                         pygame.Rect(550, 200, 60, 30),
                         pygame.Rect(800, 250, 30, 30)]

        else:
            self.obstacles = [pygame.Rect(600, 150, 30, 30),
                         pygame.Rect(400, 300, 30, 30),
                         pygame.Rect(550, 500, 30, 30),
                         pygame.Rect(800, 250, 30, 30)]


    def display_obstacles(self, screen):
        for o in self.obstacles:
            pygame.draw.rect(screen, self.colour, o)

    def get_obstacles(self):
        return self.obstacles

    def remove_obstacles(self, screen):

        for o in self.obstacles:
            pygame.draw.rect(screen, pygame.Color(255,255,255), o)

    def collision_points(self, x, y):
        for obstacle in self.obstacles:
            if obstacle.collidepoint(x, y):
                return True
        return False

    def collision_robot(self, robot_x, robot_y, robot_radius):
        for obstacle in self.obstacles:
            # Find the closest point on the rect to the robot's centre
            closest_x = max(obstacle.left, min(robot_x, obstacle.right))
            closest_y = max(obstacle.top, min(robot_y, obstacle.bottom))

            # If the distance from that point to the centre is less than the radius, they overlap
            distance = math.sqrt((robot_x - closest_x) ** 2 + (robot_y - closest_y) ** 2)
            if distance < robot_radius:
                return True
        return False
