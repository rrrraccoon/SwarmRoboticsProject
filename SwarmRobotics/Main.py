import dispersion
from Pheromones import Pheromones

import pygame
import pygame.freetype
import pygame_gui

from Robot import Robot
from Survivor import Survivor
from Obstacles import Obstacles
from ExplorationPSO import ExplorationPSO
from TransportationACO import TransportationACO

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

# make screen bg grey
interface_colour = pygame.Color(60, 61, 67)

#create font object for text
font = pygame.font.Font('fonts/FiraCode-Regular.ttf', 15)

def main():

    pygame.display.set_caption('Swarm Robotics: Search and Rescue Simulation')

    screen.fill(interface_colour)

    screen.fill(interface_colour, (0, 0, 220, screen.get_height()))

    #create a white rect which will be the environment for the swarm
    screen.fill((255,255,255), (220, 20, 660, 600))

    # button for displaying swarm
    display_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((15, 570, 185, 40)),
        text='Display/Reset Swarm',
        manager=MANAGER,
        tool_tip_text='Swarm displays'
    )

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
        manager=MANAGER,
        tool_tip_text='Spreads robots across the environment to maximise area coverage'
    )

    #exploration button
    exploration_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((15, 80), (185, 30)),
        text='Exploration: OFF',
        manager=MANAGER,
        tool_tip_text='Main swarm looks for survivors, and moves towards them once detected'
    )

    #transportation button
    transportation_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((15, 120), (185, 30)),
        text='Transportation: OFF',
        manager=MANAGER,
        tool_tip_text='Robots that have found a survivor move in a subswarm to transport them to the safe zone'
    )

    #obstacle choices dropdown
    obstacles_dropdown = pygame_gui.elements.UIDropDownMenu(
        options_list=['No Obstacles', 'Obstacles 1', 'Obstacles 2'],
        starting_option='No Obstacles',
        relative_rect=pygame.Rect((25, 290), (165, 30)),
        manager=MANAGER
    )
    draw_sidebar()

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
    pheromone_map = Pheromones()
    #use the global variables within main method
    global obstacles, obstacles_made, exploration, transportation

    transportation = TransportationACO()
    transporting = False
    exploring = False
    obstacles = None

    #main loop to run pygame display until the program is quit
    running = True
    while running:
        #60fps
        UI_REFRESH_RATE = CLOCK.tick(60)/1000

        for event in pygame.event.get():
            # pass current event into manager to process
            MANAGER.process_events(event)

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
                    #set the slider value as the same
                    try:
                        entered_size = int(event.text)
                        #clamp to slider range
                        size = max(0, min(30, entered_size))
                        swarm_slider.set_current_value(size)
                        text_input.set_text(str(size))
                    except ValueError:
                        pass
                elif event.ui_object_id == "survivortextentry":
                    try:
                        entered_count = int(event.text)
                        #clamp
                        survivor_count = max(0, min(10, entered_count))
                        survivor_text_input.set_text(str(survivor_count))
                    except ValueError:
                        pass

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                #check if user clicks on display swarm
                if event.ui_element == display_button:
                    swarm, subswarm = create_swarm(size)
                    survivor = createSurvivors(survivor_count)
                    display_swarm(swarm, survivor, obstacles)
                    pheromone_map = Pheromones()
                    transportation = TransportationACO()

                if event.ui_element == disperse_button:
                    if disperse_button.text == 'Dispersion: OFF':

                        if swarm is not None and len(swarm) > 0:
                            disperse_button.set_text('Dispersion: ON')

                            #update the text in the dispersion button before dispersion begins
                            MANAGER.update(0)
                            MANAGER.draw_ui(screen)
                            pygame.display.update()

                            #if it was exploring then pause it so the swarm disperses
                            was_exploring = exploring
                            if was_exploring:
                                exploring = False

                            dispersion.disperse_positions(swarm, updateDispersedSwarm, survivor, obstacles, subswarm, pheromone_map)

                            #continue exploring after if it was before
                            if was_exploring:
                                exploring = True

                            #after dispersion is done, resets to being off
                            disperse_button.set_text('Dispersion: OFF')
                    else:
                        disperse_button.set_text('Dispersion: OFF')

                if event.ui_element == exploration_button:
                    if exploration_button.text == 'Exploration: OFF' and exploring == False:
                        if swarm:
                            exploration_button.set_text('Exploration: ON')
                            MANAGER.update(0)
                            MANAGER.draw_ui(screen)
                            pygame.display.update()

                            exploration = ExplorationPSO(swarm, survivor, obstacles)
                            exploring = True
                        else:
                            print("A swarm must be created before exploration!")
                    else:
                        exploring = False
                        exploration_button.set_text('Exploration: OFF')


                if event.ui_element == transportation_button:
                    if transportation_button.text == 'Transportation: OFF' and transporting == False:
                        #can toggle during exploration
                        #and if exploration is paused but theres a subswarm, can still toggle
                        if exploring or subswarm:
                            transportation_button.set_text('Transportation: ON')
                            MANAGER.update(0)
                            MANAGER.draw_ui(screen)
                            pygame.display.update()

                            transporting = True
                        else:
                            print("No robots ready for transportation!")
                    else:
                        transporting = False
                        transportation_button.set_text('Transportation: OFF')

            if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                if event.ui_element == obstacles_dropdown:
                    #remove any obstacles (would also apply to No Obstacles option)
                    if obstacles_made:
                        obstacles.remove_obstacles(screen)
                        obstacles_made = False

                    if event.text == 'Obstacles 1':
                        obstacles_made = True
                        #pass in as option 1
                        obstacles = Obstacles(1)
                        obstacles.display_obstacles(screen)

                    elif event.text == 'Obstacles 2':
                        obstacles_made = True
                        #pass in as option 2
                        obstacles = Obstacles(2)
                        obstacles.display_obstacles(screen)


        #check if any behaviours are active
        if exploring and swarm is not None:
            explore_done = exploration.pso_search(swarm, survivor, updatePSOSwarm, subswarm, pheromone_map, obstacles)
            if explore_done:
                exploring = False
                exploration_button.set_text('Exploration: OFF')

        if transporting and subswarm is not None:
            transport_done = transportation.transport_subswarm(subswarm, pheromone_map,swarm, survivor, updatePSOSwarm, obstacles)
            if transport_done and not exploring:
                transporting = False
                transportation_button.set_text('Transportation: OFF')

        #update manager, to update every ui element in manager
        MANAGER.update(UI_REFRESH_RATE)
        draw_sidebar()

        #area for text of amount of survivors transported
        screen.fill(interface_colour, (220, 622, 660, 20))
        transported_count = transportation.survivors_transported if isinstance(transportation, TransportationACO) else 0
        survivor_count_display = len(survivor) if survivor else 0
        survivors_text = font.render(
            'Survivors transported: ' + str(transported_count) + '/' + str(survivor_count_display),
            True, (255, 255, 255)
        )
        screen.blit(survivors_text, (230, 620))

        MANAGER.draw_ui(screen)
        #update display
        pygame.display.update()

    pygame.quit()

def draw_sidebar():
    #fill sidebar background section
    screen.fill(interface_colour, (0, 0, 220, screen_height))

    #display text
    behaviour_text = font.render('BEHAVIOURS:', True, (255, 255, 255))
    screen.blit(behaviour_text, (20, 20))

    size_text = font.render('Swarm Size:', True, (255, 255, 255))
    screen.blit(size_text, (30, 180))

    survivor_text = font.render('Survivor Count:', True, (255, 255, 255))
    screen.blit(survivor_text, (30, 260))

    #min and max labels for slider
    min_label = font.render('0', True, (255, 255, 255))
    max_label = font.render('30', True, (255, 255, 255))
    screen.blit(min_label, (20, 235))
    screen.blit(max_label, (180, 235))

    # grey box behind key section
    screen.fill((117, 117, 117), (10, 330, 200, 220))

    # key for behaviour states/robot/survivor colours
    key_text = font.render('KEY\n'
                           'Survivor:\n\n'
                           'Dispersing:\n'
                           'Pre-dispersion\npositions:\n\n'
                           'Exploring:\n\n'
                           'Transporting/\nSurvivor Found:\n\n',
                           True, (255, 255, 255))
    screen.blit(key_text, (20, 330))

    # coloured circles in key
    # survivor
    pygame.draw.circle(screen, pygame.Color(0, 0, 255),
                       (115, 360), 6)
    # dispersing
    pygame.draw.circle(screen, pygame.Color(252, 137, 5),
                       (130, 400), 6)
    # pre-dispersion positions
    pygame.draw.circle(screen, pygame.Color(208, 222, 224),
                       (120, 440), 6)
    # exploring
    pygame.draw.circle(screen, pygame.Color(255, 0, 0),
                       (120, 480), 6)
    # survivor found
    pygame.draw.circle(screen, pygame.Color(134, 2, 250),
                       (165, 540), 6)

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
        if obstacles:
            #try different positions until it doesnt collide
            while obstacles.collision_robot(robot.get_position_x(), robot.get_position_y(), robot.RADIUS):
                robot = Robot(swarmSize)

        swarm.append(robot)


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
def updateDispersedSwarm(swarm, original_swarm, survivor, obstacles, subswarm, pheromone_map):
    # reset environment by overlaying it
    screen.fill((255, 255, 255), (220, 20, 660, 600))
    drawSafeZone()
    if obstacles_made:
        obstacles.display_obstacles(screen)

    for r in original_swarm:
        r.display_robot(screen)

    for r in swarm:
        r.display_robot(screen)

    if subswarm:
        pheromone_map.draw(screen)
        for r in subswarm:
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
    for i in range(amount):
        s = Survivor()

        if obstacles:
            while obstacles.collision_robot(s.get_position_x(), s.get_position_y(), 10):
                s = Survivor()
        survivors.append(s)

    return survivors

def displaySurvivors(survivors):
    for s in survivors:
        s.display_survivor(screen)
    pygame.display.update()

main()

