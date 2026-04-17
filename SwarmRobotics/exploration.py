import pygame
import math
import random

def pso_search(swarm, survivors, updatePSOSwarm, subswarm, pheromone_map, obstacles_made):

    #max iterations
    maxsteps = 500
    step = 0
    #robots detection radius
    detection_radius = 50
    #environment grid cell size
    cell_size = 40
    #initialise explored (passed into robot class method)
    #stores all explored 'cells' by their centre x and y coords
    explored = set()

    #return only unfound survivors each time this is called
    def unfound():
        return [s for s in survivors if not s.found]

    #initial global best is the first robot's personal best
        #maybe change to use a local best instead of a global best?
    global_best = swarm[0].personal_best.copy()

    #while max iterations havent been reached and there are still survivors remaining to be found
    while step < maxsteps and len(unfound()) > 0:

        #for each unfound survivor, check if any robots are in range of it
        for s in unfound():
            #check if the survivor doesnt already have a robot that is assigned (found) to it
            if s.assigned_robot is not None:
                continue

            #find robots that are within detection range of it (according to pso eval)
            robots_in_range = [
                r for r in swarm
                if r.get_assigned_survivor() is None
                and pso_evaluation(r.get_position(), s.get_position()) < detection_radius
            ]

            #if there have been robots found within range of it choose a random one to assign to i
            if robots_in_range:
                chosen = random.choice(robots_in_range)
                chosen.set_assigned_survivor(s)
                s.assigned_robot = chosen
                print('Robot assigned to survivor at ' + str(s.get_position()))

        #for each robot during pso search
        for r in swarm:

            #robot assigned to a survivor moves towards it
            if r.get_assigned_survivor() is not None:
                s = r.get_assigned_survivor()
                #get distance between robot and survivor
                dist = pso_evaluation(r.get_position(), s.get_position())

                #shorten distance between them (-1 to make them a bit closer)
                if dist > r.RADIUS*2 - 1:
                    #survivor x y coords
                    sx, sy = s.get_position()
                    #robot x y coords
                    rx, ry = r.get_position()
                    #reduce the distance between them
                    step_size = 5
                    dx = (sx - rx) / dist * step_size
                    dy = (sy - ry) / dist * step_size
                    r.set_position_x(rx + dx)
                    r.set_position_y(ry + dy)
                else:
                    #reached survivor
                    s.mark_found()
                    r.set_colour(pygame.Color(134, 2, 250))
                    print('Survivor found at ' + str(s.get_position()))

                    #put robot and its survivor into subswarm
                    subswarm.append(r)
                    #temporarily remove the robot from the main swarm
                    swarm.remove(r)

                updatePSOSwarm(swarm, survivors, subswarm, pheromone_map)
                continue

            #unassigned robots continue PSO exploration
            for s in unfound():
                #update gb
                if pso_evaluation(r.personal_best, s.get_position()) < pso_evaluation(
                        global_best, s.get_position()):
                    global_best = r.personal_best.copy()

            #get the currently explored area to deter away from it
            bias_x, bias_y = r.get_exploration_bias(explored, cell_size)

            #break loop if all survivors found
            remaining = unfound()
            if not remaining:
                break

            #update current robots velocity
            r.update_velocity(
                global_best, step, maxsteps, pso_evaluation,
                min(remaining, key=lambda s: pso_evaluation(
                    r.get_position(), s.get_position())).get_position(),
                bias_x, bias_y
            )

            #update position
            position = r.update_position()

            #update personal best against all unfound survivors
            for s in unfound():
                if pso_evaluation(position, s.get_position()) < pso_evaluation(
                        r.personal_best, s.get_position()):
                    r.personal_best = position.copy()
                    #check if its also a new global best
                    if pso_evaluation(r.personal_best, s.get_position()) < pso_evaluation(
                            global_best, s.get_position()):
                        global_best = r.personal_best.copy()

            updatePSOSwarm(swarm, survivors, subswarm, pheromone_map)

        step += 1

    if len(unfound()) == 0:
        print('All survivors found!')

#based on distance between a given robot and survivor position
def pso_evaluation(position, survivor_position):
    x = position[0] - survivor_position[0]
    y = position[1] - survivor_position[1]
    return math.sqrt((x ** 2) + (y ** 2))