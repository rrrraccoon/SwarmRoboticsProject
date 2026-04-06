#transportation.py
import pygame
import math
import random

#safe zone centre target for robots to move toward
SAFE_ZONE_X = 270  #centre of safe zone
SAFE_ZONE_Y = 310
SAFE_ZONE_RECT = pygame.Rect(220, 20, 100, 600)


def aco_transport(robot, survivor, pheromone_map):
    rx, ry = robot.get_position()

    if SAFE_ZONE_RECT.collidepoint(rx, ry):
        return True

    step_size = 1.0
    candidates = []

    #check possible positions all around robot
    for angle in range(0, 360, 20):
        #diff angled possible positions around robot
        rad = math.radians(angle)
        nx = rx + math.cos(rad) * step_size
        ny = ry + math.sin(rad) * step_size

        #continue if in bounds
        if not (robot.ENVIRONMENT_X_MIN + robot.RADIUS <= nx <= robot.ENVIRONMENT_X_MAX - robot.RADIUS):
            continue
        if not (robot.ENVIRONMENT_Y_MIN + robot.RADIUS <= ny <= robot.ENVIRONMENT_Y_MAX - robot.RADIUS):
            continue

        candidates.append((nx, ny))

    if not candidates:
        return False

    scores = []

    for nx, ny in candidates:
        #improves moving left toward safe zone
        improvement = rx - nx

        pheromone = pheromone_map.get(nx, ny)

        score = (1.0 + 3.0 * max(improvement, 0)) * (1.0 + 0.2 * pheromone)

        if improvement < 0:
            score *= 0.1  #if moving away

        scores.append(score)

    chosen_idx = random.choices(range(len(candidates)), weights=scores, k=1)[0]
    nx, ny = candidates[chosen_idx]

    robot.set_position_x(nx)
    robot.set_position_y(ny)

    pheromone_map.deposit(nx, ny, 0.1)

    # keep survivor attached to robot
    survivor.set_position_x(nx-10)
    survivor.set_position_y(ny-10)

    return False


def transport_subswarm(transport_queue, pheromone_map, swarm, survivors, updatePSOSwarm):
    finished = []
    active = list(transport_queue)
    clock = pygame.time.Clock()

    while active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return finished

        for robot in active[:]:
            survivor = robot.get_assigned_survivor()
            reached = aco_transport(robot, survivor, pheromone_map)

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


        updatePSOSwarm(swarm, survivors, active, pheromone_map)
        pheromone_map.evaporate()

        pygame.display.update()
        #controls transport speed (fix speed being too fast)
        clock.tick(30)

    return finished