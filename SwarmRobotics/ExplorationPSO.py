import pygame
import random
import math
class ExplorationPSO:

    MAX_STEPS = 1000

    def __init__(self, swarm, survivors, obstacles):
        #the current step of this instance of exploration
        self.step = 0
        # robots detection radius
        self.detection_radius = 50
        # environment grid cell size
        self.cell_size = 40
        # initialise explored (passed into robot class method)
        # stores all explored 'cells' by their centre x and y coords
        self.explored = set()

        # initial global best is the first robot's personal best
        self.global_best = swarm[0].personal_best.copy()

        self.done = False

    def pso_search(self, swarm, survivors, updatePSOSwarm, subswarm, pheromone_map, obstacles):
        #when exploration steps are all done, return true
        if self.done:
            return True

        # return only unfound survivors each time this is called
        #def unfound():
        unfound = [s for s in survivors if not s.found]

        if self.step >= self.MAX_STEPS or len(unfound) == 0:
            print('All survivors found!')
            self.done = True
            return True

        # for each unfound survivor, check if any robots are in range of it
        for s in unfound:
            # check if the survivor doesnt already have a robot that is assigned (found) to it
            if s.assigned_robot is not None:
                continue

            # find robots that are within detection range of it (according to pso eval)
            robots_in_range = [
                r for r in swarm
                if r.get_assigned_survivor() is None
                   and self.pso_evaluation(r.get_position(), s.get_position()) <= self.detection_radius
            ]

            # if there have been robots found within range of it choose a random one to assign to i
            if robots_in_range:
                chosen = random.choice(robots_in_range)
                chosen.set_assigned_survivor(s)
                s.assigned_robot = chosen
                print('Robot assigned to survivor at ' + str(s.get_position()))

        # for each robot during pso search
        for r in swarm:

            # robot assigned to a survivor moves towards it
            if r.get_assigned_survivor() is not None:
                s = r.get_assigned_survivor()
                # get distance between robot and survivor
                dist = self.pso_evaluation(r.get_position(), s.get_position())

                # shorten distance between them (-1 to make them a bit closer)
                if dist > r.RADIUS * 2 - 1:
                    # survivor x y coords
                    sx, sy = s.get_position()
                    # robot x y coords
                    rx, ry = r.get_position()
                    # reduce the distance between them
                    step_size = 5
                    dx = (sx - rx) / dist * step_size
                    dy = (sy - ry) / dist * step_size
                    r.set_position_x(rx + dx)
                    r.set_position_y(ry + dy)
                else:
                    # reached survivor
                    s.mark_found()
                    r.set_colour(pygame.Color(134, 2, 250))
                    print('Survivor found at ' + str(s.get_position()))

                    # put robot and its survivor into subswarm
                    subswarm.append(r)
                    # temporarily remove the robot from the main swarm
                    swarm.remove(r)

                    unfound = [s for s in survivors if not s.found]

                #updatePSOSwarm(swarm, survivors, subswarm, pheromone_map, obstacles)
                continue

            #if no survivors left
            if not unfound:
                break

            #if unassigned continue PSO exploration
            #for every unfound survivor, check and update gb/pb
            for s in unfound:
                # update gb
                if self.pso_evaluation(r.personal_best, s.get_position()) < self.pso_evaluation(
                        self.global_best, s.get_position()):
                    self.global_best = r.personal_best.copy()

            # get the currently explored area to deter away from it
            bias_x, bias_y = r.get_exploration_bias(self.explored, self.cell_size)

            # update current robots velocity
            r.update_velocity(
                self.global_best,
                self.step,
                self.MAX_STEPS,
                self.pso_evaluation,
                min(unfound, key=lambda s: self.pso_evaluation(
                    r.get_position(), s.get_position())).get_position(),
                bias_x, bias_y
            )

            old_position = r.position.copy()
            # update position
            position = r.update_position()

            #handle obstacle collision
            if obstacles:

                if obstacles.collision_robot(position[0], position[1], r.RADIUS + 1):
                    r.position = old_position.copy()
                    r.personal_best = r.position.copy()
                    r.velocity[0] *= -1
                    r.velocity[1] *= -1

                    print("obstacle avoided")
                    continue

            # update personal best against all unfound survivors
            for s in unfound:

                if self.pso_evaluation(position, s.get_position()) < self.pso_evaluation(
                        r.personal_best, s.get_position()):
                    r.personal_best = position.copy()
                    # check if its also a new global best
                    if self.pso_evaluation(r.personal_best, s.get_position()) < self.pso_evaluation(
                            self.global_best, s.get_position()):
                        self.global_best = r.personal_best.copy()

            #updatePSOSwarm(swarm, survivors, subswarm, pheromone_map, obstacles)

        self.step += 1
        updatePSOSwarm(swarm, survivors, subswarm, pheromone_map, obstacles)

        #if len(unfound()) == 0:
        #    print('All survivors found!')

        return False


    # based on distance between a given robot and survivor position
    def pso_evaluation(self, position, survivor_position):
        x = position[0] - survivor_position[0]
        y = position[1] - survivor_position[1]
        dist = math.sqrt((x ** 2) + (y ** 2))

        return dist
