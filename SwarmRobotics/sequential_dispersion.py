import math
import pygame

def disperse_positions(swarm, updateSwarm, survivor):
    learning_rate = 50
    max_iterations = 600

    anchors = []
    #indices of robots that have become anchors
    settled = set()

    anchor_colour = pygame.Color(0, 0, 255)
    RSS_threshold = 0.02

    #for each robot in the swarm
    for r in swarm:

        #first robot becomes initial anchor
        if len(anchors) == 0:
            #put in anchors array
            anchors.append(r)
            print("first anchor robot: " + str(swarm.index(r)))

        else:
            #moving until max iterations
            iterations = 0

            while iterations < max_iterations:
                print(iterations)


                x_position = r.get_position_x()
                y_position = r.get_position_y()

                #calculate current RSS at x using sum of anchor's rss
                x_RSS = calculateTotalRSS(x_position, y_position, anchors)

                #calculate x gradient
                x_gradient = calculateGradientX(x_position, y_position, x_RSS, anchors)

                #calculate new position
                new_x_position = x_position - (learning_rate * x_gradient)

                print(x_position)
                print(new_x_position)
                print(" .")

                #store new rss
                x_new_rss = calculateTotalRSS(new_x_position, y_position, anchors)

                if x_new_rss <= RSS_threshold:
                    print("reached threshold in x")
                    break

                #evaluate calculated position
                #check if its within bounds and if the new position is better
                if (r.ENVIRONMENT_X_MIN+r.RADIUS <= new_x_position <= r.ENVIRONMENT_X_MAX-r.RADIUS) and (x_new_rss < x_RSS):

                    r.set_position_x(new_x_position)
                    x_position = new_x_position
                    print("new x")
                    print(x_new_rss)
                    updateSwarm(swarm, survivor)

                #y pos now done after it has moved in x direction
                #calculate RSS
                #calculate current RSS at y using sum of anchor's rss
                y_RSS = calculateTotalRSS(x_position, y_position, anchors)

                #calculate y gradient
                y_gradient = calculateGradientY(x_position, y_position, y_RSS, anchors)

                #calculate new position
                new_y_position = y_position - (learning_rate * y_gradient)

                print(y_position)
                print(new_y_position)
                print(" .")

                #store new rss
                y_new_rss = calculateTotalRSS(x_position, new_y_position, anchors)

                if y_new_rss <= RSS_threshold:
                    print("reached threshold in y")
                    break

                # evaluate calculated position
                # check if its within bounds and if the new position is better
                if (r.ENVIRONMENT_Y_MIN + r.RADIUS <= new_y_position <= r.ENVIRONMENT_Y_MAX - r.RADIUS) and (y_new_rss < y_RSS):
                    r.set_position_y(new_y_position)
                    y_position = new_y_position
                    print("new y")
                    updateSwarm(swarm, survivor)

                iterations += 1

                updateSwarm(swarm, survivor)
            #make current robot the anchor
            anchors.append(r)

        #change colour of anchors
        r.set_colour(anchor_colour)
        updateSwarm(swarm, survivor)


def calculateGradientX(x_position, y_position, current_RSS, anchors):
    step = 4
    next_position = x_position + step

    RSS_next = calculateTotalRSS(next_position, y_position, anchors)

    gradient = (RSS_next - current_RSS)/(next_position - x_position)
    return gradient

def calculateGradientY(x_position, y_position, current_RSS, anchors):
    step = 4
    next_position = y_position + step

    RSS_next = calculateTotalRSS(x_position, next_position, anchors)

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
def calculateTotalRSS(x_position, y_position, anchors):
    total = 0
    for a in anchors:
            total += calculateRSS(x_position, y_position, a)

    return total
