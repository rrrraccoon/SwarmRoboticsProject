# Swarm-Robotics-Individual-Project

An interactive Search and Rescue Swarm Robotics 2D simulation. The aim of this simulation is to allow users to understand how swarm robotics behaviours function and interact.

It demonstrates three main behaviours:
### Dispersion:
Robots spread out across the evironment to increase coverage. Grey circles represent the pre-dispersion positions of robots for comparison.

### Exploration:
Robots search for survivors, approaching a survivor that is within their range. Each robot has a visible detection radar. Can be paused and resumed.

### Transportation:
Robots that have detected and successfully approached a survivor during the exploration phase carry them within a subswarm to the safe zone. Their pathing is seen in orange. Can be paused and resumed.

## Running the Simulation:
The simulation is written in python, and requires pygame and pygame_gui to be installed:
```
pip install pygame pygame_gui
```

**Run the program through the Main.py file**


## Core project files:
**Main.py:** Handles executing the program and displaying the UI.
**Robot.py:** Robot class - Robot state, position and velocity update handling, detection radius display.
**Survivor.py:** Survivor class - Survivor state and position.
**Obstacles.py:** Obstacles class - Handles displaying obstacles and detecting collisions .
**dispersion.py:** Dispersion behaviour - Implementation using a Modified Gradient Descent algorithm.
**ExplorationACO.py:** Exploration behaviour class - Implemented using Particle Swarm Optimisation (PSO).
**TransportationACO.py:** Transportation behaviour class - Implemented using Ant Colony Optimisation (ACO).
**Pheromones.py:** Pheromone class - Handles depositing, evaporating and displaying ACO pheromones during transportation. Pheromones are shown as orange within the simulation.

## Using the simulation:
**Swarm size slider/input:** Set the number of robots in the swarm (0-30).
**Survivor count input:** Set the number of survivors appearing in the environment.
**Obstacles dropdown menu:** Choose between displaying no obstacles or two obstacle configurations.
**Key:** Colour-coded key to identify each robot and survivor state.
**Display/Reset Swarm button:** Initialises the swarm and survivors in random positions in the enviroment. Clicking this again resets the swarm with any updated parameters.
**Survivors transported counter:** Tracks the number of survivors that have been successfully transported.
**Dispersion/Exploration/Transportation behaviour buttons:** Toggle enabling/disabling behaviours.

Exploration and transportation can be toggled on to run concurrently.
Enabling dispersion during exploration briefly pauses exploration, disperses the swarm, then automatically resumes. This can be done to help robots that become stuck due to PSO convergence.
The user can hover over behaviour buttons for a short description of what it does.