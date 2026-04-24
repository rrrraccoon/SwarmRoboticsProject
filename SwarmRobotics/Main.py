import sequential_dispersion
import dispersion
import exploration
from Transport import Transport
import transportation

import pygame
import pygame.freetype
import pygame_gui

from Robot import Robot
from Survivor import Survivor
from Obstacles import Obstacles

#setup pygame modules
pygame.init()
CLOCK = pygame.Clock()
#width and height of display
screen_width = 900
screen_height = 640

#initialise pygame_gui ui manager
MANAGER = pygame_gui.UIManager((screen_width, screen_height))

#set the screen with caption
screen = pygame.display.set_mode((screen_width, screen_height))
#if obstacles need to be dealt with
obstacles_made = False

def main():

    pygame.display.set_caption('Swarm Robotics: Search and Rescue Simulation')

    # make screen bg grey
    interface_colour = pygame.Color(60, 61, 67)
    screen.fill(interface_colour)

    screen.fill(interface_colour, (0, 0, 220, screen.get_height()))

    #create a white rect which will be the environment for the swarm
    screen.fill((255,255,255), (220, 20, 660, 600))

    #create font object for text
    font = pygame.font.Font('fonts/FiraCode-Regular.ttf', 15)

    #display text
    behaviour_text = font.render('BEHAVIOURS:', True, (255,255,255))
    screen.blit(behaviour_text, (20,20))

    #dispersion_text = font.render('Dispersion:', True, (255, 255, 255))
    #screen.blit(dispersion_text, (30, 80))

    size_text = font.render('Swarm Size:', True, (255, 255, 255))
    screen.blit(size_text, (30, 180))

    survivor_text = font.render('Survivor Count:', True, (255, 255, 255))
    screen.blit(survivor_text, (30, 260))

    #exploration_text = font.render('Exploration:', True, (255, 255, 255))
    #screen.blit(exploration_text, (30, 100))

    #min and max labels for slider
    min_label = font.render('0', True, (255, 255, 255))
    max_label = font.render('30', True, (255, 255, 255))
    screen.blit(min_label, (20, 235))  #under left end of slider
    screen.blit(max_label, (180, 235))  #under right end of slider

    #button next to dispersion
    #screen.fill((255, 255, 255), (140, 84, 14, 14))

    #button next to exploration
    #screen.fill((255, 255, 255), (140, 104, 14, 14))

    # button for displaying swarm
    screen.fill((217, 217, 217), (15, 570, 185, 40))
    #display swarm text
    display_swarm_text = font.render('Display/Reset Swarm', True, (0, 0, 0))
    screen.blit(display_swarm_text, (20, 580))

    #input box next to swarm size
    text_input = pygame_gui.elements.UITextEntryLine(
        relative_rect=pygame.Rect((140, 180), (30, 20)),
        initial_text="5",
        manager=MANAGER,
        object_id="textentry")

    #input box next to survivor count
    survivor_text_input = pygame_gui.elements.UITextEntryLine(
        relative_rect=pygame.Rect((170, 260), (30, 20)),
        initial_text="2",
        manager=MANAGER,
        object_id="survivortextentry")


    #slider to change swarm size
    swarm_slider = pygame_gui.elements.UIHorizontalSlider(
        relative_rect=pygame.Rect((15, 205), (185, 30)),
        start_value=5,
        value_range=(0, 30),
        manager=MANAGER)

    #dispersion button
    disperse_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((15, 40), (185, 30)),
        text='Dispersion: OFF',
        manager=MANAGER
    )

    #exploration button
    exploration_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((15, 80), (185, 30)),
        text='Exploration: OFF',
        manager=MANAGER
    )

    #transportation button
    transportation_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((15, 120), (185, 30)),
        text='Transportation: OFF',
        manager=MANAGER
    )

    #toggle static obstacles button
    obstacles_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((25, 290), (165, 30)),
        text='Obstacles: OFF',
        manager=MANAGER
    )

    #grey box behind key section
    screen.fill((117, 117, 117), (10, 330, 200, 220))


    #key for behaviour states/robot/survivor colours
    key_text = font.render('KEY\n'
                           'Survivor:\n\n'
                           'Dispersing:\n'
                           'Pre-dispersion\npositions:\n\n'
                           'Exploring:\n'
                           'Survivor Found:\n\n'
                           'Transporting:\n',
                           True, (255, 255, 255))
    screen.blit(key_text, (20, 330))

    #coloured circles in key
    #survivor
    pygame.draw.circle(screen, pygame.Color(0, 0, 255),
                       (115, 360), 6)
    #dispersing
    pygame.draw.circle(screen, pygame.Color(252, 137, 5),
                       (130, 400), 6)
    #pre-dispersion positions
    pygame.draw.circle(screen, pygame.Color(208, 222, 224),
                       (120, 440), 6)
    #exploring
    pygame.draw.circle(screen, pygame.Color(255, 0, 0),
                       (120, 480), 6)
    #survivor found
    pygame.draw.circle(screen, pygame.Color(134, 2, 250),
                       (165, 500), 6)
    #transportation
    pygame.draw.circle(screen, pygame.Color(0, 255, 0),
                       (150, 540), 6)

    # safe zone left side of environment
    SAFE_ZONE = pygame.Rect(220, 20, 100, 600)
    drawSafeZone()


    #applies changes to display
    pygame.display.flip()

    #initial variables when loading up simulation
    size = 5
    survivor_count = 2
    swarm = None
    survivor = None
    #transportation subswarm
    subswarm = []
    #initialise pheromone map
    pheromone_map = Transport()
    #store prev behaviour
    previous_behaviour = ''
    #use the global variable within main method
    global obstacles_made
    obstacles = None

    #main loop to run pygame display until the program is quit
    running = True
    while running:
        #60fps
        UI_REFRESH_RATE = CLOCK.tick(60)/1000

        for event in pygame.event.get():
            #if the program is quit
            if event.type == pygame.QUIT:
                running = False


            if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                if event.ui_element == swarm_slider:
                    size = int(swarm_slider.get_current_value())
                    #set the text box value as the same
                    text_input.set_text(str(size))

            #check if text entry value has been changed
            if event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
                if event.ui_object_id == "textentry":
                    #size = int(event.text)
                    #set the slider value as the same
                    try:
                        entered_size = int(event.text)
                        #clamp to slider range
                        size = max(0, min(30, entered_size))
                        swarm_slider.set_current_value(size)
                        text_input.set_text(str(size))
                    except ValueError:
                        #print("invalid value")
                        pass
                elif event.ui_object_id == "survivortextentry":
                    try:
                        entered_count = int(event.text)
                        #clamp
                        survivor_count = max(0, min(10, entered_count))
                        survivor_text_input.set_text(str(survivor_count))
                    except ValueError:
                        #print("invalid value")
                        pass

            #chek if user clicks on display swarm
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse = pygame.mouse.get_pos()
                #check if its clicked within the area of the button
                if 15 <= mouse[0] <= 200 and 570 <= mouse[1] <= 610:
                    swarm, subswarm = create_swarm(size)
                    survivor = createSurvivors(survivor_count)
                    display_swarm(swarm, survivor, obstacles)
                    pheromone_map = Transport()

                    #prev stored behaviour resets
                    previous_behaviour = ''

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == disperse_button:
                    if disperse_button.text == 'Dispersion: OFF':

                        if swarm is not None and len(swarm) > 0 and previous_behaviour != 'disperse':
                            disperse_button.set_text('Dispersion: ON')

                            #update the text in the dispersion button before dispersion begins
                            MANAGER.update(0)
                            MANAGER.draw_ui(screen)
                            pygame.display.update()

                            dispersion.disperse_positions(swarm, updateDispersedSwarm, survivor, obstacles_made)
                            previous_behaviour = 'disperse'
                            #after dispersion is done, resets to being off
                            disperse_button.set_text('Dispersion: OFF')
                    else:
                        disperse_button.set_text('Dispersion: OFF')

                if event.ui_element == exploration_button:
                    #print('clicked')
                    if exploration_button.text == 'Exploration: OFF':

                        if swarm is not None and len(swarm) > 0 and previous_behaviour != 'explore':
                            exploration_button.set_text('Exploration: ON')

                            MANAGER.update(0)
                            MANAGER.draw_ui(screen)
                            pygame.display.update()

                            #pso_search(swarm, survivor)
                            exploration.pso_search(swarm,
                                                   survivor,
                                                   updatePSOSwarm,
                                                   subswarm,
                                                   pheromone_map,
                                                   obstacles)

                            previous_behaviour = 'explore'
                            #resets to being off
                            exploration_button.set_text('Exploration: OFF')
                    else:
                        exploration_button.set_text('Exploration: OFF')

                if event.ui_element == transportation_button:
                    if transportation_button.text == 'Transportation: OFF':
                        if swarm and previous_behaviour == 'explore':

                            if len(subswarm) == 0:
                                print('No robots ready for transportation, run exploration first')
                            else:
                                transportation_button.set_text('Transportation: ON')
                                MANAGER.update(0)
                                MANAGER.draw_ui(screen)
                                pygame.display.update()

                                #run ACO transport for all robots in the subswarm
                                transportation.transport_subswarm(
                                    subswarm, pheromone_map,
                                    swarm, survivor,
                                    updatePSOSwarm,
                                    obstacles
                                )

                                previous_behaviour = 'transport'
                                transportation_button.set_text('Transportation: OFF')
                        else:
                            print('Run exploration first before transporting')
                    else:
                        transportation_button.set_text('Transportation: OFF')

                if event.ui_element == obstacles_button:
                    #print('clicked')
                    if obstacles_button.text == 'Obstacles: OFF':
                        if previous_behaviour == '':

                            obstacles_button.set_text('Obstacles: ON')
                            obstacles_made = True
                            obstacles = Obstacles(1)
                            obstacles.display_obstacles(screen)

                            #update the text
                            MANAGER.update(0)
                            MANAGER.draw_ui(screen)
                            pygame.display.update()


                    else:
                        obstacles_button.set_text('Obstacles: OFF')
                        obstacles.remove_obstacles(screen)
                        obstacles_made = False
                        MANAGER.update(0)
                        MANAGER.draw_ui(screen)
                        pygame.display.update()

            #pass current event into manager to process (if not quitting)
            MANAGER.process_events(event)

        #update manager, to update every ui element in manager
        MANAGER.update(UI_REFRESH_RATE)

        MANAGER.draw_ui(screen)

        #update display
        pygame.display.update()

    pygame.quit()

def drawSafeZone():
    font = pygame.font.Font('fonts/FiraCode-Regular.ttf', 15)
    # draw safe zone in environment
    screen.fill((198, 255, 160), (220, 20, 100, 600))  # light green
    safe_zone_text = font.render('SAFE\nZONE', True, (0, 0, 0))
    screen.blit(safe_zone_text, (245, 300))

def display_swarm(swarm, survivor, obstacles):
    #reset environment by overlaying it
    screen.fill((255, 255, 255), (220, 20, 660, 600))
    drawSafeZone()

    if obstacles_made:
        obstacles.display_obstacles(screen)

    #create robot objects in swarm population
    for r in swarm:
        #print(robot.return_position())
        #print('robot added')
        r.display_robot(screen)
        pygame.display.update()

    displaySurvivors(survivor)
    pygame.display.update()


def create_swarm(swarmSize):
    # initialise swarm
    swarm = []
    subswarm = []

    # create robot objects in swarm population
    for i in range(swarmSize):
        robot = Robot(swarmSize)
        # print(robot.return_position())
        swarm.append(robot)
        # print('robot added')

    return swarm, subswarm

def updateSwarm(swarm, survivor, obstacles):
    # reset environment by overlaying it
    screen.fill((255, 255, 255), (220, 20, 660, 600))
    drawSafeZone()

    if obstacles_made:
        obstacles.display_obstacles(screen)

    for r in swarm:
        r.display_robot(screen)

    displaySurvivors(survivor)
    pygame.display.update()

#to have the original swarm positions be displayed as well
def updateDispersedSwarm(swarm, original_swarm, survivor, obstacles):
    # reset environment by overlaying it
    screen.fill((255, 255, 255), (220, 20, 660, 600))
    drawSafeZone()
    if obstacles_made:
        obstacles.display_obstacles(screen)

    for r in original_swarm:
        r.display_robot(screen)

    for r in swarm:
        r.display_robot(screen)

    displaySurvivors(survivor)
    pygame.display.update()

#pso robots have their detection radius visible
def updatePSOSwarm(swarm, survivor, subswarm, pheromone_map, obstacles):
    # reset environment by overlaying it
    screen.fill((255, 255, 255), (220, 20, 660, 600))
    drawSafeZone()

    if obstacles_made:
        obstacles.display_obstacles(screen)

    for r in swarm:
        r.display_pso_robot(screen)

    #subswarm display
    if subswarm:
        pheromone_map.draw(screen)
        for r in subswarm:
            r.display_robot(screen)


    displaySurvivors(survivor)
    pygame.display.update()

def createSurvivors(amount):
    survivors = []
    for _ in range(amount):
        survivors.append(Survivor())

    return survivors

def displaySurvivors(survivors):
    for s in survivors:
        s.display_survivor(screen)
    pygame.display.update()

main()

