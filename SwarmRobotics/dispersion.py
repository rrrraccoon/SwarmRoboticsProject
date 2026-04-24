import math

import pygame
import copy


def disperse_positions(swarm, updateDispersedSwarm, survivor, obstacles):

    max_iterations = 1000
    disperse_colour = pygame.Color(252, 137, 5)

    #if a swarm wasnt created
    if len(swarm) == 0:
        return

    n = len(swarm)
    RSS_threshold = (n - 1) * (1 / 150)

    #adjust learning rate based on size so it isnt too fast
    if n <= 3:
        learning_rate = 150
    elif n <= 5:
        learning_rate = 100
    elif n <= 8:
        learning_rate = 75
    else:
        learning_rate = 60

    #indices of robots that have become anchors
        #may change to use list comprehension
    settled = set()

    #display transparent circles in original positions
    original_swarm = copy.deepcopy(swarm)
    for r in original_swarm:
        r.set_colour(pygame.Color(208, 222, 224))
        #r.display_robot(screen)

    #while dispersing, set the colour of robots to blue
    for r in swarm:
        r.set_colour(disperse_colour)


    for iteration in range(max_iterations):

        if len(settled) == len(swarm):
            break  #all robots have settled

        #get new positions for all robots simultaneously
        #using the CURRENT positions of all of them
        #stored in dictionary
        new_positions = {}


        #for each robot in the swarm
        #enumerate to get both current index i and robot object r of swarm
        for i, r in enumerate(swarm):

            #if the current indexed robot is already settled/anchored
            #go to next iteration
            if i in settled:
                continue

            x = r.get_position_x()
            y = r.get_position_y()

            #using every other robot as anchor which instead now acts as repulsing
            #excluding current robot
            others = [other for j, other in enumerate(swarm) if j != i]

            #if there are no other robots (e.g. only 1 robot in swarm)
            if len(others) == 0:
                continue

            #make a check if its currently past rss threshold
            #would then make it settled and go to next iteration
            current_rss = calculateTotalRSS(x, y, others, obstacles)
            if current_rss <= RSS_threshold:
                settled.add(i)
                continue

            #calculating new x position using x gradient
            #gradient using original rss
            x_gradient = calculateGradientX(x, y, current_rss, others, obstacles)
            new_x = x - (learning_rate * x_gradient)
            #get the new rss using the new x position
            x_new_rss = calculateTotalRSS(new_x, y, others, obstacles)


            if not (r.ENVIRONMENT_X_MIN + r.RADIUS <= new_x <= r.ENVIRONMENT_X_MAX - r.RADIUS) or x_new_rss >= current_rss:
                new_x = x  #reject move by reassigning original position

            #y position (using updated x for gradient and rss)
            y_rss = calculateTotalRSS(new_x, y, others, obstacles)
            y_gradient = calculateGradientY(new_x, y, y_rss, others, obstacles)
            new_y = y - (learning_rate * y_gradient)
            y_new_rss = calculateTotalRSS(new_x, new_y, others, obstacles)


            if not (r.ENVIRONMENT_Y_MIN + r.RADIUS <= new_y <= r.ENVIRONMENT_Y_MAX - r.RADIUS) or y_new_rss >= y_rss:
                new_y = y  #reject move by reverting to original y

            #update new positions into robot's index
            new_positions[i] = (new_x, new_y)

        #after 1 iteration of whole swarm, apply all new positions
        #concurrent update
        for i, (new_x, new_y) in new_positions.items():
            swarm[i].set_position_x(new_x)
            swarm[i].set_position_y(new_y)


        #check RSS for each non-settled robot using updated positions
        for i, r in enumerate(swarm):
            if i in settled:
                continue
            others = [other for j, other in enumerate(swarm) if j != i]
            if len(others) == 0:
                continue
            current_rss = calculateTotalRSS(r.get_position_x(), r.get_position_y(), others, obstacles)
            #make settled
            if current_rss <= RSS_threshold:
                settled.add(i)

        updateDispersedSwarm(swarm, original_swarm, survivor, obstacles)

    #after dispersion, reset colour
    for r in swarm:
        r.set_colour(pygame.Color(255, 0, 0))
    updateDispersedSwarm(swarm, original_swarm, survivor, obstacles)


def calculateGradientX(x_position, y_position, current_RSS, anchors, obstacles):
    step = 4
    next_position = x_position + step

    RSS_next = calculateTotalRSS(next_position, y_position, anchors, obstacles)

    gradient = (RSS_next - current_RSS)/(next_position - x_position)
    return gradient

def calculateGradientY(x_position, y_position, current_RSS, anchors, obstacles):
    step = 4
    next_position = y_position + step

    RSS_next = calculateTotalRSS(x_position, next_position, anchors, obstacles)

    gradient = (RSS_next - current_RSS)/(next_position - y_position)
    return gradient

#with 1 anchor
def calculateRSS(x_position, y_position, anchor):
    ax = anchor.get_position_x()
    ay = anchor.get_position_y()

    distance = abs(math.sqrt((x_position - ax) ** 2 + (y_position - ay) ** 2))
    #epsilon to prevent current division by 0 error if robots overlap exactly
    epsilon = 1e-6
    distance = max(distance, epsilon)

    rss = 1/distance
    return rss

#passes values into calculateRSS for each anchor then adds
def calculateTotalRSS(x_position, y_position, anchors, obstacles):
    total = 0
    for a in anchors:
            total += calculateRSS(x_position, y_position, a)

    if obstacles:
        total += calculateTotalObstacleRSS(x_position, y_position, obstacles)

    return total

def calculateTotalObstacleRSS(x_position, y_position, obstacles):
    total = 0
    for obstacle in obstacles.get_obstacles():
        #get the x and y bounds of the obstacle
        closest_x = max(obstacle.left, min(x_position, obstacle.right))
        closest_y = max(obstacle.top, min(y_position, obstacle.bottom))

        #get distance from center of obstacle to robot
        distance = math.sqrt((x_position - closest_x) ** 2 + (y_position - closest_y) ** 2)
        epsilon = 1e-6
        distance = max(distance, epsilon)

        #adding this rss to total rss
        total += 1/distance
    return total