Fence Defense

Award Categories We Are Applying To

1. Social Good Category

Our game symbolizes the importance of protecting free speech and expression on campus.
By giving players direct control through computer vision and the phone flashlight mechanic, the game emphasizes that defending shared values—like open expression—requires active participation, not passive observation.
Players must manually shine their light to stop threats approaching the fence, reinforcing the idea that preserving free speech is a responsibility we all share.
This interactive design ties directly into the Social Good category by combining gameplay with a meaningful message about agency, community, and protecting expressive spaces.
2. General Category

Our project highlights several unique and innovative features:

Computer Vision Integration
Phone Flashlight Combat System
Damage & Health System (HP bars, healing, losing health)
Strategic Flex Dollar Economy
Earn 10 Flex Dollars per Zombie Kill
Placeable Defense Structures
Turrets, Healing Stations, and Drones
Destructible Fence and Destructible Structures
Wave-Based Level Progression
Increasing Enemy Difficulty
Multiplayer Mode (Cooperative Two-Role System)
How to Run the Program

To run Fence Defense, you will need:

Python 3.12 or higher
Any Python-capable IDE (VSCode, PyCharm, Thonny, etc.)
The cmu_graphics package
The opencv-python package
A device with a functioning camera for the CV flashlight mechanic
Steps to run:

Open the project folder in your IDE or terminal.
Run the main Python file for the game.
Ensure your camera is enabled so the computer vision system can detect your phone flashlight.
General Description

Fence Defense is a real-time defensive strategy game where the player must protect a fence from waves of zombies advancing from the left side of the screen. The fence has a health bar, and the game ends when its HP reaches zero.

Players must:

Use their phone flashlight + computer vision to manually kill zombies
Earn Flex Dollars and spend them on defenses
Place turrets, healing stations, and drones strategically
Survive waves of increasing difficulty within each level
Progress through and beat multiple levels, each containing its own set of increasingly challenging and complex waves
The core objective is simple: protect the fence at all costs.

Basic Controls

Flashlight Combat

Shine your phone flashlight at zombies.
The computer vision system detects the light and damages the zombies.
Buying & Placing Structures

Use the top-left UI to select:

Turrets
Healing Stations
Drones
Click an item to select it.

Click anywhere on the battlefield to place it (if you have enough Flex Dollars).

Gameplay Mechanics

You earn 10 Flex Dollars for each zombie you kill.
Turrets and drones automatically attack zombies.
Healing stations restore HP to nearby defenses.
The fence and all structures have HP and can be destroyed.

Important Commands (Joseph's Computer)

cd "/Users/josephouyang/Desktop/15-112 (F25)/hack112-group-16"
python3.13 cv_sender.py

cd "/Users/josephouyang/Desktop/15-112 (F25)/hack112-group-16"
python3.13 zombie_defense.py




