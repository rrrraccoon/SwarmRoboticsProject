import pygame

class Transport:
    # safe zone centre target for robots to move toward
    SAFE_ZONE_X = 270
    SAFE_ZONE_Y = 310

    def __init__(self):
        # grid cell, same size as used for pso exploration
        self.cell_size = 20 #changed from 40 to test
        self.pheromones = {}
        self.evaporation_rate = 0.07
        self.min_pheromone = 0.01
        self.max_pheromone = 5.0

    def deposit(self, x, y, amount):
        cell = (int(x // self.cell_size), int(y // self.cell_size))
        current = self.pheromones.get(cell, self.min_pheromone)
        self.pheromones[cell] = min(self.max_pheromone, current + amount)

    def get(self, x, y):
        cell = (int(x // self.cell_size), int(y // self.cell_size))
        return self.pheromones.get(cell, self.min_pheromone)

    def evaporate(self):
        for cell in list(self.pheromones.keys()):
            self.pheromones[cell] *= (1 - self.evaporation_rate)
            if self.pheromones[cell] < self.min_pheromone:
                del self.pheromones[cell]

    #for drawing pheromones
    def draw(self, screen):
        for (cx, cy), strength in self.pheromones.items():
            x = cx * self.cell_size
            y = cy * self.cell_size
            s = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
            s.fill((255, 140, 0, min(180, int(strength * 40))))
            screen.blit(s, (x, y))