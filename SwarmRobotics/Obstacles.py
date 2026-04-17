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
