import random
import pygame
class Robot:

    #radius of all robots (displayed as circles)
    RADIUS = 10
    #environment boundaries based on UI
    ENVIRONMENT_X_MIN = 220
    ENVIRONMENT_X_MAX = 880
    ENVIRONMENT_Y_MIN = 20
    ENVIRONMENT_Y_MAX = 620

    def __init__(self, swarm_size):

        #initially random positions within the centre area
        self.position = self.random_position()
        self.position_x, self.position_y = self.position[0], self.position[1]
        #initially red
        self.robot_colour = pygame.Color(255, 0, 0)

        #PSO
        self.personal_best = self.position[:]

        #scale max speed down for smaller swarms (avoid speed being too fast)
        speed = 0.6 + (swarm_size / 60.0)
        #print(speed)
        self.min_velocity = -speed
        self.max_velocity = speed

        #random initial velocity
        self.velocity = self.random_velocity()


        self.detection_radius = 50
        self.show_detection = True

        self.stagnation_counter = 0
        self.last_position = None
        self.STAGNATION_LIMIT = 15

        self.assigned_survivor = None

    def set_assigned_survivor(self, survivor):
        self.assigned_survivor = survivor


    def get_assigned_survivor(self):
        return self.assigned_survivor

    def random_position(self):
        #get random number within bounds of environment and considering radius of robot
        position = []
        #to restrict initial swarm to be in a smaller area in center
        bounds = 200
        #get random x value
        position.append(random.randint(self.ENVIRONMENT_X_MIN + self.RADIUS + bounds, self.ENVIRONMENT_X_MAX - self.RADIUS - bounds))
        #get random y value
        position.append(random.randint(self.ENVIRONMENT_Y_MIN + self.RADIUS + bounds, self.ENVIRONMENT_Y_MAX - self.RADIUS - bounds))

        return position

    #getters
    def get_position_x(self):
        #print(self.position_x)
        return self.position_x

    def get_position_y(self):
        #print(self.position_y)
        return self.position_y

    def get_position(self):
        #print(self.position_y)
        return self.position

    #setters
    def set_position_x(self, new_x):
        self.position_x = new_x
        self.position[0] = new_x

    def set_position_y(self, new_y):
        self.position_y = new_y
        self.position[1] = new_y

    def set_colour(self, robot_colour):
        self.robot_colour = robot_colour

    #draw the robot instance
    def display_robot(self, screen):
        pygame.draw.circle(screen, self.robot_colour, (self.position_x, self.position_y), self.RADIUS)

    def random_velocity(self):
        self.velocity = [random.uniform(self.min_velocity, self.max_velocity), random.uniform(self.min_velocity, self.max_velocity)]

        return self.velocity


    #bias will be used to adjust exploration
    def update_velocity(self, global_best, iteration, total_iterations,pso_evaluation, survivor_position, bias_x, bias_y):

        self.new_velocity = []
        c1 = 1.2
        c2 = 0.5
        #decrease overtime
        bias_strength = 3.0 - (iteration / total_iterations) * 2.0

        min_inertia = 0.4
        max_inertia = 0.9
        noise = random.uniform(-0.2, 0.2)
        inertia_weight = (max_inertia - min_inertia) * (
            (total_iterations - iteration) / total_iterations) + min_inertia

        if random.random() < 0.2:
            self.velocity = [
                random.uniform(self.min_velocity, self.max_velocity),
                random.uniform(self.min_velocity, self.max_velocity)
            ]
        else:
            for i in range(2):
                d1 = random.random()
                d2 = random.random()

                cognitive = c1 * d1 * (self.personal_best[i] - self.position[i])

                #more exploration if not in range of survivor
                if pso_evaluation(self.position, survivor_position) > 90:
                    social = social = c2 * d2 * (global_best[i] - self.position[i]) * 0.6
                else:
                    social = c2 * d2 * (global_best[i] - self.position[i])

                #add exploration bias for current area
                bias = bias_strength * ([bias_x, bias_y][i])

                v = inertia_weight * self.velocity[i] + cognitive + social + bias

                #have a chance of adding noise
                if random.random() < 0.1:
                    v += noise

                v = max(self.min_velocity, min(self.max_velocity, v))

                self.new_velocity.append(v)

            self.velocity = self.new_velocity.copy()

        return self.velocity

    def update_position(self):

        for x in range(2):
            self.position[x] += self.velocity[x]

        #reverse velocity if reaches bounds
        if self.position[0] <= self.ENVIRONMENT_X_MIN + self.RADIUS:
            self.position[0] = self.ENVIRONMENT_X_MIN + self.RADIUS
            self.velocity[0] = abs(self.velocity[0])  # push right
        elif self.position[0] >= self.ENVIRONMENT_X_MAX - self.RADIUS:
            self.position[0] = self.ENVIRONMENT_X_MAX - self.RADIUS
            self.velocity[0] = -abs(self.velocity[0])  # push left

        if self.position[1] <= self.ENVIRONMENT_Y_MIN + self.RADIUS:
            self.position[1] = self.ENVIRONMENT_Y_MIN + self.RADIUS
            self.velocity[1] = abs(self.velocity[1])  # push down
        elif self.position[1] >= self.ENVIRONMENT_Y_MAX - self.RADIUS:
            self.position[1] = self.ENVIRONMENT_Y_MAX - self.RADIUS
            self.velocity[1] = -abs(self.velocity[1])  # push up

        self.position_x = int(self.position[0])
        self.position_y = int(self.position[1])

        return self.position

    def get_exploration_bias(self, explored, cell_size):
        # get current cell/area
        cell_x = int(self.position_x // cell_size)
        cell_y = int(self.position_y // cell_size)

        # mark current cell as explored
        explored.add((cell_x, cell_y))

        #nudge away from explored neighbours
        bias_x, bias_y = 0, 0
        #the neighbour areas in the x and y axis
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                #get the current neighbour area
                neighbour = (cell_x + dx, cell_y + dy)
                #if it has been explored, there will be a slight push to go opposite that direction
                if neighbour in explored:
                    bias_x -= dx
                    bias_y -= dy

        return bias_x, bias_y

    def display_pso_robot(self, screen):
        #show the yellow detection radius
        if self.show_detection:
            d = self.detection_radius
            detection_surface = pygame.Surface((d * 2, d * 2), pygame.SRCALPHA)
            pygame.draw.circle(detection_surface, (255, 255, 0, 30), (d, d), d)

            #the top-left of the detection surface
            blit_x = self.position_x - d
            blit_y = self.position_y - d

            #clamp blit position to the environment boundaries, so detection radius doesnt go past wall
            env_x_min = self.ENVIRONMENT_X_MIN
            env_y_min = self.ENVIRONMENT_Y_MIN
            env_x_max = self.ENVIRONMENT_X_MAX
            env_y_max = self.ENVIRONMENT_Y_MAX

            #how much to shift the blit position
            clamped_blit_x = max(env_x_min, min(blit_x, env_x_max - d * 2))
            clamped_blit_y = max(env_y_min, min(blit_y, env_y_max - d * 2))

            #the area on the detection_surface that corresponds to the clamped blit
            area_x = clamped_blit_x - blit_x
            area_y = clamped_blit_y - blit_y
            area_w = min(d * 2 - area_x, env_x_max - clamped_blit_x)
            area_h = min(d * 2 - area_y, env_y_max - clamped_blit_y)

            if area_w > 0 and area_h > 0:
                screen.blit(detection_surface, (clamped_blit_x, clamped_blit_y),
                            area=pygame.Rect(area_x, area_y, area_w, area_h))

        pygame.draw.circle(screen, self.robot_colour,
                           (self.position_x, self.position_y), self.RADIUS)
