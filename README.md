# Fence Defense
**Team:** Joseph Ouyang, Caleb Ouyang, Parker Merritt, Rachael Chung

---

Fence Defense is a real-time tower defense game where players protect CMU's iconic Fence from waves of zombies using their phone flashlight and strategically placed structures. Built in 48 hours for Hack112, the game combines computer vision, a resource economy, and wave-based progression across 5 days and 15 waves.

---

## Table of Contents
- [Gameplay Overview](#gameplay-overview)
- [Controls](#controls)
- [Structures](#structures)
- [Wave and Level System](#wave-and-level-system)
- [Computer Vision Setup](#computer-vision-setup)
- [Getting Started](#getting-started)
- [Tech Stack](#tech-stack)
- [Repository Structure](#repository-structure)

---

## Gameplay Overview

Zombies spawn on the left side of the screen and march toward the Fence on the right. The Fence has an HP bar and the game ends when it reaches zero.

Players defend using two tools: their phone flashlight, detected by a computer vision system, and purchasable structures placed on the battlefield. Each zombie kill earns 10 Flex Dollars, which fund the structures needed to survive later waves.

### Win and Loss Conditions

| Condition | Trigger |
|---|---|
| Win | Survive all 3 waves across all 5 days |
| Loss | Fence HP reaches 0 |

---

## Controls

### Flashlight Combat
Point your phone flashlight at the camera. The CV system detects the light source and projects a cursor onto the screen. Holding the cursor over a zombie deals continuous damage until it dies.

### Buying and Placing Structures
The shop UI appears in the top-left corner of the game screen.

1. Click a structure slot to select it
2. Click anywhere on the battlefield to place it, if you have enough Flex Dollars
3. A red flash on the slot indicates insufficient funds

### Keyboard

| Key | Action |
|---|---|
| None required | All primary actions are mouse and flashlight driven |

---

## Structures

| Structure | Cost | Function |
|---|---|---|
| Turret | 100 Flex Dollars | Automatically fires bullets at zombies in the same row |
| Healing Station | 150 Flex Dollars | Pulses healing to nearby turrets within a set radius |
| Drone | 50 Flex Dollars | Patrols and attacks zombies autonomously |

All structures have HP and can be destroyed by zombies. Zombies will stop and attack any structure blocking their row before continuing toward the Fence.

### Special Enemy Types

| Enemy | Behavior |
|---|---|
| Standard Zombie | Walks toward the Fence at normal speed |
| Fast Zombie | Moves faster and appears at higher wave counts |

---

## Wave and Level System

The game is structured as 5 Days, each containing 3 Waves. Zombie spawn rate and difficulty scale with both the current wave and the current day.

```
Day 1 → Wave 1, Wave 2, Wave 3
Day 2 → Wave 1, Wave 2, Wave 3
...
Day 5 → Wave 1, Wave 2, Wave 3  → Victory
```

A new wave begins automatically once all zombies from the previous wave are cleared. A 20-second countdown between waves gives players time to place structures before the next spawn begins.

---

## Computer Vision Setup

The flashlight mechanic requires two processes running simultaneously: a CV sender that reads the camera and streams cursor coordinates, and the main game that receives them over a local UDP socket.

The CV sender detects the brightest light source in the camera feed and maps its coordinates to the game screen. Smoothing is applied to reduce jitter.

**Run in two separate terminal windows:**

```bash
# Terminal 1: start the CV sender
python3 cv_sender.py

# Terminal 2: start the game
python3 final_product.py
```

A functioning camera is required. The flashlight from a phone works best in a moderately dim environment.

---

## Getting Started

**Requirements:**

- Python 3.12 or later
- `cmu_graphics` package
- `opencv-python` package

```bash
pip install opencv-python
```

**Steps:**

1. Clone the repository and open the project folder
2. Run `cv_sender.py` in one terminal
3. Run `final_product.py` in a second terminal
4. Point your phone flashlight at the camera to begin

The game opens on a main menu with a history screen showcasing real events at the CMU Fence before starting.

---

## Tech Stack

| Tool | Use |
|---|---|
| Python 3.12+ | Primary language |
| cmu_graphics | Rendering and event handling via the 15-112 graphics framework |
| opencv-python | Computer vision for flashlight detection |
| socket (stdlib) | UDP communication between CV sender and game process |

---

## Repository Structure

```
fence-defense/
├── final_product.py     # main game
├── python_files/        # supporting modules including cv_sender
├── images/              # all game sprites and UI assets
├── sounds/              # music and sound effects
├── .vscode/             # editor config
├── .gitignore
└── README.md
```

---

*Built at Hack112, Carnegie Mellon University.
