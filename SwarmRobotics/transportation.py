#transportation.py
import pygame
import math
import random

#safe zone centre target for robots to move toward
SAFE_ZONE_X = 270  #centre of safe zone
SAFE_ZONE_Y = 310
SAFE_ZONE_RECT = pygame.Rect(220, 20, 100, 600)


def aco_transport(robot, survivor, pheromone_map, obstacles):
    rx = robot.get_position_x()
    ry = robot.get_position_y()

    alpha = 1.0
    beta = 4.0

    probabilities = []
    candidates = []

    # to avoid robot moving too fast/teleporting
    move_speed = 0.1

    #if reached safe zone
    if SAFE_ZONE_RECT.collidepoint(rx, ry):
        return True

    cell_size = pheromone_map.cell_size
    #get current cell
    current_cell_x = int(rx // cell_size)
    current_cell_y = int(ry // cell_size)

    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue

            #get neighbouring cell
            next_cell_x = current_cell_x + dx
            next_cell_y = current_cell_y + dy

            x_position = (next_cell_x + 0.5) * cell_size
            y_position = (next_cell_y + 0.5) * cell_size

            #skips adding a candidate if its out of bounds of environment
            if not (robot.ENVIRONMENT_X_MIN + robot.RADIUS <= x_position <= robot.ENVIRONMENT_X_MAX - robot.RADIUS):
                continue
            if not (robot.ENVIRONMENT_Y_MIN + robot.RADIUS <= y_position <= robot.ENVIRONMENT_Y_MAX - robot.RADIUS):
                continue

            #euclidean distance to safe zone
            distance_to_safezone = math.sqrt((x_position - SAFE_ZONE_X) ** 2 + (y_position - SAFE_ZONE_Y) ** 2)

            distance_before = math.sqrt((rx - SAFE_ZONE_X) ** 2 + (ry - SAFE_ZONE_Y) ** 2)
            distance_after = math.sqrt((x_position - SAFE_ZONE_X) ** 2 + (y_position - SAFE_ZONE_Y) ** 2)

            #if positive change in distance, better
            d = distance_before - distance_after
            if d > 0:
                #+1 for better heuristic
                improvement = (1 + d) ** beta
            else:
                #if going away from safe zone
                improvement = 0.01

            #pheromone
            pheromone = pheromone_map.get(x_position, y_position) ** alpha

            if obstacles.collision_robot(x_position, y_position, 15):
                pheromone *= 0.5

            p = improvement * pheromone

            if obstacles.collision_robot(x_position, y_position, 10):
                p *= 0.2

            candidates.append((x_position, y_position))
            probabilities.append(p)

    #if theres no valid candidates
    if not candidates:
        print("no candidates")
        return False

    #make sum of probabilities = 1 (done implicitly in random.choices with weights) then choose the next position
    #[0] to get the single value from the list returned by it
    next_position = random.choices(range(len(candidates)), weights=probabilities, k=1)[0]
    x_position, y_position = candidates[next_position]

    new_x = rx + (x_position - rx) * move_speed
    new_y = ry + (y_position - ry) * move_speed

    #if the new positions still collide
    if obstacles.collision_robot(new_x, new_y, robot.RADIUS):

        #test every other candidate, if one doesnt collide then break loop and use that for position
        for i in range(len(candidates)):
            x_position, y_position = candidates[i]
            new_x = rx + (x_position - rx) * move_speed
            new_y = ry + (y_position - ry) * move_speed

            if not obstacles.collision_robot(new_x, new_y, robot.RADIUS):
                print("new candidate found")
                break

        #if loop completes and final candidate still collides, reject movement
        if obstacles.collision_robot(new_x, new_y, robot.RADIUS):
            return False

    robot.set_position_x(new_x)
    robot.set_position_y(new_y)

    #keep survivor next to robot
    survivor.set_position_x(new_x - 10)
    survivor.set_position_y(new_y - 10)

    distance_before = math.sqrt((rx - SAFE_ZONE_X) ** 2 + (ry - SAFE_ZONE_Y) ** 2)
    distance_after = math.sqrt((x_position - SAFE_ZONE_X) ** 2 + (y_position - SAFE_ZONE_Y) ** 2)

    #put down pheromone (more if closer to safe zone)
    if (distance_after < distance_before):
        deposit_amount = 0.5
    else:
        deposit_amount = 0.05

    pheromone_map.deposit(x_position, y_position, deposit_amount)

    return False


def transport_subswarm(transport_queue, pheromone_map, swarm, survivors, updatePSOSwarm, obstacles):
    finished = []
    active = list(transport_queue)
    clock = pygame.time.Clock()

    while active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return finished

        for robot in active[:]:
            survivor = robot.get_assigned_survivor()
            reached = aco_transport(robot, survivor, pheromone_map, obstacles)

            if reached:
                print("Robot delivered survivor to safe zone")
                survivor.set_colour(pygame.Color(0, 0, 200))
                survivor.transported = True

                robot.set_colour(pygame.Color(255, 0, 0))
                robot.set_assigned_survivor(None)
                robot.stagnation_counter = 0
                robot.last_position = None
                robot.personal_best = robot.get_position()[:]
                #add the robot back into the main swarm
                swarm.append(robot)

                finished.append((robot, survivor))
                active.remove(robot)


        updatePSOSwarm(swarm, survivors, active, pheromone_map, obstacles)
        pheromone_map.evaporate()

        pygame.display.update()
        #controls transport speed (fix speed being too fast)
        clock.tick(30)

    return finished