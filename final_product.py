from cmu_graphics import *
import socket
import random
import math

############################################################
# NETWORK SETUP — receives flashlight coords from OpenCV
############################################################
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("127.0.0.1", 5005))
sock.setblocking(False)

############################################################
# SCREEN SIZE
############################################################
SCREEN_W = 1512
SCREEN_H = 1000

############################################################
# BASE HP
############################################################
BASE_MAX_HP = 25

############################################################
# UTILS
############################################################
def clamp(val, lo, hi):
    return max(lo, min(hi, val))

def drawImageFit(imgPath, cx, cy, maxW, maxH):
    # Load image metadata
    w, h = getImageSize(imgPath)   # cmu_graphics built-in

    scale = min(maxW / w, maxH / h)
    newW = w * scale
    newH = h * scale

    drawImage(imgPath, cx, cy, align='center', width=newW, height=newH)


############################################################
# BACKGROUND FUNCTIONS
############################################################
def generateGrass(app):
    density = 0.1
    for row in range(app.tilesHigh):
        for col in range(app.tilesWide):
            if random.random() < density:
                cx = col * app.tileW + app.tileW/2 + random.randint(-40, 40)
                cy = row * app.tileH + app.tileH/2 + random.randint(-30, 30)
                scale = random.uniform(0.4, 1.0)
                app.grassSprites.append({'x': cx, 'y': cy, 'scale': scale})

def generateFlowers(app):
    density = 0.15
    for row in range(app.tilesHigh):
        for col in range(app.tilesWide):
            if random.random() < density:
                cx = col * app.tileW + app.tileW/2 + random.randint(-40, 40)
                cy = row * app.tileH + app.tileH/2 +random.randint(-30, 30)
                scale = random.uniform(0.3, 0.8)
                app.flowers.append(Flower(cx, cy, scale))


def drawTiles(app):
    for row in range(app.tilesHigh):
        for col in range(app.tilesWide):
            x = col * app.tileW
            y = row * app.tileH
            drawImage(
                "images/grassTile.png",
                x, y,
                align='top-left',
                width=app.tileW,
                height=app.tileH
            )


def drawGrass(app):
    for blade in app.grassSprites:
        drawImage(
            "images/grass.png",
            blade['x'], blade['y'],
            align='center',
            width=50 * blade['scale'],
            height=50 * blade['scale']
        )

def drawFlowers(app):
    for flower in app.flowers:
        drawImage(flower.image, flower.x, flower.y, 
                align='center', width = 30*flower.scale,
                height=30*flower.scale)


def drawFence(app):
    for (x, y1, y2, thickness) in app.fencePlanks:
        drawRect(x - thickness/2, y1,
                 thickness, y2 - y1,
                 fill=rgb(38, 85, 255),
                 border=rgb(47, 47, 252))

    for (x, y, r) in app.fencePosts:
        drawCircle(x, y, r,
                   fill=rgb(75, 127, 252),
                   border=rgb(37, 79, 179))
        
def drawGameText(text, x, y, size=20, color='white', align='center'):
    drawLabel(text, x+1, y+1, size=size, bold=True, fill='black', align=align)
    drawLabel(text, x, y, size=size, bold=True, fill=color, align=align)


############################################################
# ZOMBIE CLASS — WALK, ATTACK, HP, FLASHLIGHT DAMAGE
############################################################
class Zombie:
    def __init__(self, app, wave):
        # position + collision radius
        self.x = -200
        self.y = random.randint(100, 750)
        self.r = 30

        # movement speed based on wave
        self.speed = random.uniform(4.0, 6.0) + 0.35 * (wave - 1)

        # walking animation frames (zom0, zom1, zom2)
        self.images = app.zombieFrames1
        self.frame = 0
        self.animDelay = 5
        self.animTimer = 0

        # ----- ATTACKING STATE -----
        self.attacking = False              # zombie stops moving at fence
        self.attackTimer = 0                # deal damage every 30 frames
        self.attackAnimTimer = 0            # animation timer
        self.attackAnimDelay = 10           # switch zom3 ↔ zom4 every 10 frames
        self.attackAnimFrame = 0            # 0 or 1 (index into attackFrames)
        self.attackFrames1 = app.attackFrames1  # zom3, zom4

        # ----- FLASHLIGHT DAMAGE -----
        self.requiredTime = 30      # 1 second at 30 FPS
        self.timeOnCursor = 0       # accumulates flashlight damage

    ########################################################
    # MOVE + WALK OR ATTACK ANIMATION
    ########################################################
    def update(self):
        # If zombie is attacking the fence, it does NOT move.
        if self.attacking:
            # attack animation
            self.attackAnimTimer += 1
            if self.attackAnimTimer >= self.attackAnimDelay:
                self.attackAnimFrame = (self.attackAnimFrame + 1) % 2
                self.attackAnimTimer = 0
            return

        # walking movement
        self.x += self.speed

        # walking animation
        self.animTimer += 1
        if self.animTimer >= self.animDelay:
            self.frame = (self.frame + 1) % len(self.images)
            self.animTimer = 0

    ########################################################
    # CURSOR HIT DETECTION
    ########################################################
    def hit(self, cx, cy):
        return math.dist((self.x, self.y), (cx, cy)) < self.r

    ########################################################
    # FLASHLIGHT DAMAGE
    ########################################################
    def applyFlashlightDamage(self):
        self.timeOnCursor += 1

    def isDead(self):
        return self.timeOnCursor >= self.requiredTime

    ########################################################
    # DRAW ZOMBIE + HEALTH BAR
    ########################################################
    def draw(self):
        if self.attacking:
            # attack animation (zom3, zom4)
            drawImage(self.attackFrames1[self.attackAnimFrame],
                      self.x, self.y, align='center')
        else:
            # normal walking animation (zom0–zom2)
            drawImage(self.images[self.frame],
                      self.x, self.y, align='center')

        # ----- NEW HEALTH BAR (FULL GREEN → RED AS DAMAGE) -----

        barWidth = 40
        hpPercent = clamp(1 - (self.timeOnCursor / self.requiredTime), 0, 1)
        greenWidth = barWidth * hpPercent
        redWidth = barWidth - greenWidth

        # green — remaining HP
        if greenWidth > 0:
            drawRect(self.x - barWidth/2,
                    self.y - 40,
                    greenWidth,
                    6,
                    fill='lime')

        # red — missing HP
        if redWidth > 0:
            drawRect(self.x - barWidth/2 + greenWidth,
                    self.y - 40,
                    redWidth,
                    6,
                    fill='red')
            

class ZombieFast:
    def __init__(self, app, wave):
        # position + collision radius
        self.x = -200
        self.y = random.randint(100, 750)
        self.r = 30

        # movement speed based on wave
        self.speed = random.uniform(4.0, 6.0) + 0.35 * (wave - 1) +2

        # walking animation frames (zom0, zom1, zom2)
        self.images = app.zombieFrames2
        self.frame = 0
        self.animDelay = 5
        self.animTimer = 0

        # ----- ATTACKING STATE -----
        self.attacking = False              # zombie stops moving at fence
        self.attackTimer = 0                # deal damage every 30 frames
        self.attackAnimTimer = 0            # animation timer
        self.attackAnimDelay = 10           # switch zom3 ↔ zom4 every 10 frames
        self.attackAnimFrame = 0            # 0 or 1 (index into attackFrames)
        self.attackFrames2 = app.attackFrames2  # zom3, zom4

        # ----- FLASHLIGHT DAMAGE -----
        self.requiredTime = 30      # 1 second at 30 FPS
        self.timeOnCursor = 0       # accumulates flashlight damage

    ########################################################
    # MOVE + WALK OR ATTACK ANIMATION
    ########################################################
    def update(self):
        # If zombie is attacking the fence, it does NOT move.
        if self.attacking:
            # attack animation
            self.attackAnimTimer += 1
            if self.attackAnimTimer >= self.attackAnimDelay:
                self.attackAnimFrame = (self.attackAnimFrame + 1) % 2
                self.attackAnimTimer = 0
            return

        # walking movement
        self.x += self.speed

        # walking animation
        self.animTimer += 1
        if self.animTimer >= self.animDelay:
            self.frame = (self.frame + 1) % len(self.images)
            self.animTimer = 0

    ########################################################
    # CURSOR HIT DETECTION
    ########################################################
    def hit(self, cx, cy):
        return math.dist((self.x, self.y), (cx, cy)) < self.r

    ########################################################
    # FLASHLIGHT DAMAGE
    ########################################################
    def applyFlashlightDamage(self):
        self.timeOnCursor += 1

    def isDead(self):
        return self.timeOnCursor >= self.requiredTime

    ########################################################
    # DRAW ZOMBIE + HEALTH BAR
    ########################################################
    def draw(self):
        if self.attacking:
            # attack animation (zom3, zom4)
            drawImage(self.attackFrames2[self.attackAnimFrame],
                      self.x, self.y, align='center')
        else:
            # normal walking animation (zom0–zom2)
            drawImage(self.images[self.frame],
                      self.x, self.y, align='center')

        # ----- NEW HEALTH BAR (FULL GREEN → RED AS DAMAGE) -----

        barWidth = 40
        hpPercent = clamp(1 - (self.timeOnCursor / self.requiredTime), 0, 1)
        greenWidth = barWidth * hpPercent
        redWidth = barWidth - greenWidth

        # green — remaining HP
        if greenWidth > 0:
            drawRect(self.x - barWidth/2,
                    self.y - 40,
                    greenWidth,
                    6,
                    fill='lime')

        # red — missing HP
        if redWidth > 0:
            drawRect(self.x - barWidth/2 + greenWidth,
                    self.y - 40,
                    redWidth,
                    6,
                    fill='red')
            

class HealthStation:
    sound = Sound('sounds/place2.mp3')
    def __init__(self, x, y):
        self.image = "images/healthStation.png"
        self.x = x 
        self.y = y
        self.health = 5
        self.pulse = 5

class Bullet:
    def __init__(self, x, y):
        self.image = "images/bullet.png"
        self.x = x
        self.y = y
        self.dx = -4

class Flower:
    flowerImages = ['images/flower1.png', 'images/flower2.png', 'images/flower3.png', 'images/flower4.png']
    def __init__(self, x, y, scale):
        self.image= Flower.flowerImages[randrange(0, 4)]
        self.x=x
        self.y=y
        self.scale=scale

def distance(x1, y1, x2, y2):
    return ((x2 - x1)**2 + (y2 - y1)**2)**0.5

class Turret:
    sound = Sound('sounds/place1.mp3')
    def __init__(self, x, y):
        self.image = "images/turret.png"
        self.x = x
        self.y = y
        self.health = 5        # turrets now have 5 HP
        self.steps = 0

class Drone:
    sound = Sound('sounds/drone.mp3')
    def __init__(self, targetX, targetY):
        self.image = 'images/drone.png'
        self.x = targetX
        self.y = 900
        self.targetX = targetX
        self.targetY = targetY
        self.width = 80
        self.height = 80
        self.dropping = 5
        self.dy = -5

class ExplodingDrone:
    sound = Sound('sounds/explosion.mp3')
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.r = 5
        self.dr = 2
        self.maxR = 25

# class Spark:
#     def __init__(self, x, y):
#         # random short-lived spark effect
#         self.x = x
#         self.y = y
#         self.radius = random.randint(4, 7)
#         self.opacity = 100
#         self.dx = random.uniform(-1, 1)
#         self.dy = random.uniform(-1, 1)
#         self.decay = random.uniform(3, 6)

def healNearbyTurrets(app):
    HEAL_RATE = 0.025         # heals 0.5 HP per tick (slow, balanced)
    HEAL_RADIUS = app.tileW * 1.1   # heal within *one tile*

    for station in app.healthStations:
        healed_any = False

        for turret in app.turrets:
            dist = distance(turret.x, turret.y, station.x, station.y)

            # Turret inside healing radius
            if dist <= HEAL_RADIUS:
                healed_any = True
                turret.health = min(app.maxTurretHealth,
                                    turret.health + HEAL_RATE)

        # --------------------------
        # Healing pulse animation
        # --------------------------
        if healed_any:
            # pulse grows faster when actively healing
            station.pulse += app.healPulseSpeed
        else:
            # idle slow pulsing
            station.pulse += 0.5

        # wrap around
        if station.pulse >= app.healPulseMax:
            station.pulse = app.healPulseMin
# def updateSparks(app):
#     toRemove = []
#     for i, s in enumerate(app.sparks):
#         s.x += s.dx
#         s.y += s.dy
#         s.opacity -= s.decay
#         s.radius *= 0.85
#         if s.opacity <= 0 or s.radius <= 0.5:
#             toRemove.append(i)
#     for i in reversed(toRemove):
#         app.sparks.pop(i)

def doExplosions(app):
    toPop = []
    for i in range(len(app.explodingDrones)):
        explosion = app.explodingDrones[i]
        explosion.r+=explosion.dr
        if explosion.r >= 40:
            toPop.append(i)
    for i in reversed(toPop):
        app.explodingDrones.pop(i)

def moveDrones(app):
    toPop=[]
    for i in range(len(app.drones)):
        drone=app.drones[i]
        drone.y += drone.dy
        if drone.y<=drone.targetY:
            drone.y = drone.targetY
            drone.width-=drone.dropping
            drone.height-=drone.dropping
            if drone.width<=10:
                toPop.append(i)
                app.explodingDrones.append(ExplodingDrone(drone.x, drone.y))
    for i in reversed(toPop):
        ExplodingDrone.sound.play()
        app.drones.pop(i)

def addBullets(app):
    for turret in app.turrets:
        turret.steps+=1
        if turret.steps==60:
            app.bullets.append(Bullet(turret.x-35, turret.y))
            #addSpark(app, turret.x-35, turret.y)
            turret.steps=0


def moveBullets(app):
    i=0
    toPop=[]
    for i in range(len(app.bullets)):
        bullet = app.bullets[i]
        bullet.x += bullet.dx
        if bullet.x < 0:
            toPop.append(i)
    for i in reversed(toPop):
        app.bullets.pop(i)

def gameScreen_onMousePress(app, x, y):

    # If flashing red, ignore
    if app.errorTimer > 0:
        return

    clickedSlot = None

    # Check if clicking inside top-center seed bank
    for i, (x1, y1, x2, y2) in enumerate(app.rects):
        if x1 <= x <= x2 and y <= app.headerHeight:
            clickedSlot = i
            break

    # Clicked on a slot
    if clickedSlot is not None:
        cost = app.costs[clickedSlot]

        if app.sun < cost:
            app.errorSlot = clickedSlot
            app.errorTimer = 120
            app.selected = None
        else:
            app.selected = clickedSlot
        return

    # Clicked on field → place selected item
    if y > app.headerHeight and app.selected is not None:

        cost = app.costs[app.selected]

        if app.sun >= cost:

            row, col = getCell(app, x, y)
            if row is not None:
                cy = row * app.tileH + app.tileH / 2
                cx = col * app.tileW + app.tileW / 2

                if isLegalPlacement(app, cx, cy):

                    if app.selected == 0:
                        app.turrets.append(Turret(cx, cy))
                        app.bullets.append(Bullet(cx-35, cy))
                        #addSpark(app, cx-35, cy)
                        Turret.sound.play()

                    elif app.selected == 1:
                        app.healthStations.append(HealthStation(cx, cy))
                        HealthStation.sound.play()

                    elif app.selected == 2:
                        app.drones.append(Drone(x, y))
                        Drone.sound.play()

                    # slot 2 → reserved for future

                    app.sun -= cost

        app.selected = None

def isLegalPlacement(app, cx, cy):
    for turret in app.turrets:
        if (turret.x==cx and turret.y==cy):
            return False
    for healthStation in app.healthStations:
        if (healthStation.x==cx and healthStation.y==cy):
            return False
    return True

def getCell(app, x, y):
    row = math.floor(y / app.tileH)
    col = math.floor(x / app.tileW)
    if (0 <= row < app.tilesHigh) and (0 <= col < app.tilesWide):
        return (row, col)
    else:
        return None, None
    
def drawTurrets(app):
    for turret in app.turrets:
        drawImage(turret.image, turret.x, turret.y,
                  align='center', width=90, height=70)

        maxHP = app.maxTurretHealth
        hp = turret.health

        barWidth = 50
        barHeight = 6

        greenWidth = barWidth * (hp / maxHP)
        redWidth = barWidth - greenWidth

        # Draw GREEN (only if >0)
        if greenWidth > 0:
            drawRect(
                turret.x - barWidth/2,
                turret.y - 55,
                max(1, greenWidth),   # <-- ensures positive width
                barHeight,
                fill='lime'
            )

        # Draw RED (only if >0)
        if redWidth > 0:
            drawRect(
                turret.x - barWidth/2 + greenWidth,
                turret.y - 55,
                max(1, redWidth),      # <-- ensures positive width
                barHeight,
                fill='red'
            )

def drawBullets(app):
    for bullet in app.bullets:
        drawImage(bullet.image, bullet.x, bullet.y, 
                    align ='center', width=30, height=15)
        
def bulletHitsZombie(bullet, zombie):
    return distance(bullet.x, bullet.y, zombie.x, zombie.y) < zombie.r

def drawHealthStations(app):
    for station in app.healthStations:
        drawImage(station.image, station.x, station.y,
                  align='center', width=90, height=70)

        maxHP = app.maxTurretHealth
        hp = station.health

        barWidth = 50
        barHeight = 6

        greenWidth = barWidth * (hp / maxHP)
        redWidth = barWidth - greenWidth

        if greenWidth > 0:
            drawRect(
                station.x - barWidth/2,
                station.y - 55,
                max(1, greenWidth),
                barHeight,
                fill='lime'
            )

        if redWidth > 0:
            drawRect(
                station.x - barWidth/2 + greenWidth,
                station.y - 55,
                max(1, redWidth),
                barHeight,
                fill='red'
            )
        
def drawHealingAnimations(app):
    for station in app.healthStations:
        opacity = int(60 * (1 - (station.pulse / app.healPulseMax)))

        drawCircle(station.x, station.y,
                   station.pulse,
                   fill=None,
                   border='lightGreen',
                   borderWidth=3,
                   opacity=opacity)
    
def drawHealthStationsBar(app):
    for station in app.healthStations:
        # Draw station sprite
        drawImage(station.image, station.x, station.y, 
                  align='center', width=90, height=70)

        # ----- HEALTH BAR -----
        maxHP = 5
        hp = station.health
        barWidth = 50
        barHeight = 6

        greenWidth = barWidth * (hp / maxHP)
        redWidth   = barWidth - greenWidth

        # green HP
        if greenWidth > 0:
            drawRect(station.x - barWidth/2,
                     station.y - 55,
                     greenWidth,
                     barHeight,
                     fill='lime')

        # red missing HP
        if redWidth > 0:
            drawRect(station.x - barWidth/2 + greenWidth,
                     station.y - 55,
                     redWidth,
                     barHeight,
                     fill='red')
        
def drawDrones(app):
    for drone in app.drones:
        drawImage(drone.image, drone.x, drone.y, 
                    align ='center', width=drone.width, height=drone.height)

def drawExplodingDrones(app):
    for explosion in app.explodingDrones:
        drawCircle(explosion.x, explosion.y,
                    explosion.r, fill=gradient('yellow', 'orange', 'red'),
                    opacity = 50)
        
def explosionHitsZombies(app):
    """Kill zombies that are inside any explosion radius."""
    for explosion in app.explodingDrones:
        for z in app.zombies[:]:
            d = distance(explosion.x, explosion.y, z.x, z.y)
            if d <= explosion.r:
                # Zombie dies instantly
                app.zombies.remove(z)
                app.score += 1
                app.effects.append(Explosion(z.x, z.y))

# def drawSparks(app):
#     for s in app.sparks:
#         drawCircle(s.x, s.y, s.radius,
#                    fill=rgb(255, 230, 120),   # warm flash color
#                    border=None,
#                    opacity=int(max(0, s.opacity)))


############################################################
# EXPLOSION EFFECT
############################################################
class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10
        self.maxRadius = 42
        self.life = 0

    def step(self):
        self.life += 1
        self.radius += 4

    def done(self):
        return self.radius >= self.maxRadius

    def draw(self):
        opacity = clamp(100 - self.life * 7, 0, 100)
        drawCircle(self.x, self.y, self.radius,
                   fill=None,
                   border='yellow',
                   borderWidth=4,
                   opacity=opacity)


############################################################
# GAME SETUP / RESET
############################################################
def resetGame(app):
    # -------------------------------------
    # CORE GAME STATE RESET
    # -------------------------------------
    app.cursor = (SCREEN_W//2, SCREEN_H//2)
    app.zombies = []
    app.effects = []
    app.turrets = []
    app.bullets = []
    app.healthStations = []
    app.score = 0
    app.baseHP = BASE_MAX_HP
    app.wave = 1
    app.steps = 0
    app.gameOver = False
    app.gameWin = False

    app.flowers = []
    
    app.drones = []
    app.explodingDrones = []
    #app.sparks = []
    app.grassSprites = []
    generateGrass(app)
    generateFlowers(app)
    app.isTurrets= True
    app.isDrones = False
    app.isStations = False
    app.healRadius = 100
    app.healRadius = app.healRadius = int(app.tileW * 1.0)   # = exactly 1 tile radius
    app.healAmount = 0.2
    app.maxTurretHealth = 5

    # -------------------------------------
    # SEED BANK RESET (TOP-CENTER UI)
    # -------------------------------------
    app.sun = 670                     # <-- FIXED HERE
    app.numRects = 3
    app.headerHeight = 90

    # Shrink box width to prevent horizontal stretching
    fullWidth = app.width * 0.75
    rectWidth = (fullWidth / app.numRects) * 0.55

    # Center the seed bank
    app.headerLeft = (app.width - rectWidth * app.numRects) / 2

    # Costs for each slot
    app.costs = [100, 150, 50]        # turret, health, bullet (future)

    # Item icons
    itemsList = 'images'
    app.itemImages = [
        f'{itemsList}/turret.png',
        f'{itemsList}/healthStation.png',
        f'{itemsList}/drone.png'
    ]

    # Build the seed bank rectangles
    app.rects = []
    for i in range(app.numRects):
        x1 = app.headerLeft + i * rectWidth
        y1 = 0
        x2 = x1 + rectWidth
        y2 = app.headerHeight
        app.rects.append((x1, y1, x2, y2))

    # Selection states
    app.selected = None
    app.errorSlot = None
    app.errorTimer = 0

    # -------------------------------------
    # LOAD SPRITE ANIMATIONS
    # -------------------------------------
    base = 'images/'
    app.zombieFrames1 = [
        f'{base}/zom0.png',
        f'{base}/zom1.png',
        f'{base}/zom2.png'
    ]
    app.attackFrames1 = [
        f'{base}/zom3.png',
        f'{base}/zom4.png'
    ]

    app.zombieFrames2 = [
        f'{base}/zom5.png',
        f'{base}/zom6.png',
    ]

    app.attackFrames2 = [
        f'{base}/zom7.png',
        f'{base}/zom8.png'
    ]

    # ----- WAVE / LEVEL STATE -----
    app.level = 1
    app.waveInLevel = 1
    app.maxLevels = 5
    app.maxWavesPerLevel = 3

    app.waveActive = False
    app.waveActiveButZombies = False
    app.timeBetweenWaves = 180    # frames between waves
    app.timeUntilNextWave = 120   # countdown before next wave      # length of each wave in frames
    app.waveTimer = 600

def onAppStart(app):
    app.menuMusic = Sound("sounds/menuMusic.mp3")
    app.levelUp = Sound("sounds/levelUp.mp3")
    # -------------------------------------
    # GAMEPLAY CONSTANTS
    # -------------------------------------
    app.healRadius = 60
    app.healAmount = 0.2
    app.maxTurretHealth = 5
    
    # Healing animation pulses
    app.healPulse = 5
    app.healPulseSpeed = 4
    app.healPulseMax = 70
    app.healPulseMin = 5

    app.stepsPerSecond = 30

    # -------------------------------------
    # GRID / FIELD SETUP
    # -------------------------------------
    app.tilesWide = 20
    app.tilesHigh = 10
    app.tileW = SCREEN_W / app.tilesWide
    app.tileH = SCREEN_H / app.tilesHigh

    # Grass decoration
    app.grassSprites = []

    resetGame(app)

    generateGrass(app)

    # -------------------------------------
    # FENCE SETUP
    # -------------------------------------
    app.fencePosts = []
    app.fencePlanks = []

    numPosts = 6
    postRadius = 15
    plankThick = 12

    fenceX = SCREEN_W - 180
    fenceHeight = 650
    fenceTop = 100
    spacing = fenceHeight / (numPosts - 1)

    app.fenceX = fenceX
    app.fenceTop = fenceTop
    app.fenceBottom = fenceTop + fenceHeight
    app.fenceLeft = fenceX - 40
    app.fenceRight = fenceX + 40

    # Vertical posts
    for i in range(numPosts):
        y = fenceTop + i * spacing
        app.fencePosts.append((fenceX, y, postRadius))

    # Horizontal planks
    for i in range(numPosts - 1):
        y1 = fenceTop + i * spacing
        y2 = fenceTop + (i + 1) * spacing
        app.fencePlanks.append((fenceX, y1, y2, plankThick))

    # for main menu
    app.width = 1512
    app.height = 1000

    app.gameStartHover = False
    app.historyHover = False
    app.goBackHover = False

    app.startGame = False
    app.history =  False

    app.historyDict = {0: "images/whatthefence.png", 1: "images/1923.png", 2: "images/1989.png", 3: "images/2001.png",
                       4: "images/2011.png", 5: "images/2020.png", 6: "images/2025.png"}
    
    app.selectedTimeline = 0

############################################################
# SPARKS
############################################################

# def addSpark(app, x, y):
#     MAX_SPARKS = 200
#     if len(app.sparks) >= MAX_SPARKS:
#         return
#     # creates 3–6 sparks when turret fires
#     for i in range(random.randint(3, 6)):
#         app.sparks.append(Spark(x, y))

############################################################
# SOCKET CURSOR UPDATE
############################################################
def updateCursorFromSocket(app):
    try:
        while True:
            data, _ = sock.recvfrom(1024)
            rawX, rawY = map(int, data.decode().split(","))

            x = int(rawX * (SCREEN_W / 1920))
            y = int(rawY * (SCREEN_H / 1080))

            ox, oy = app.cursor
            alpha = 0.25
            sx = int(ox*(1-alpha) + x*alpha)
            sy = int(oy*(1-alpha) + y*alpha)

            app.cursor = (clamp(sx, 0, SCREEN_W),
                          clamp(sy, 0, SCREEN_H))

    except BlockingIOError:
        pass


############################################################
# GAME LOOP
############################################################
def gameScreen_onStep(app):
    nextWave(app)
    # Seed bank flashing logic (red slot timer)
    if app.errorTimer > 0:
        app.errorTimer -= 1
        if app.errorTimer == 0:
            app.errorSlot = None
    if not app.gameOver and not app.gameWin:
        updateCursorFromSocket(app)

    # turrets + bullets + healing
    addBullets(app)
    moveBullets(app)
    healNearbyTurrets(app)
    moveDrones(app)
    doExplosions(app)
    explosionHitsZombies(app)
    #updateSparks(app)

    # explosions
    for fx in app.effects:
        fx.step()
    app.effects = [fx for fx in app.effects if not fx.done()]

    if app.gameOver or app.gameWin:
        return

    app.steps += 1

    # waves


    # spawn zombies
    if app.waveTimer > 0: #STOP SPAWNING WHEN WAVE TIMER IS ZERO
        randChoice = random.randint(0, 5)
        spawnChance = 0.005 + (0.003 * (app.waveInLevel - 1)) * (app.level - 1)
        if random.random() < spawnChance:
            if randChoice == 5:
                app.zombies.append(ZombieFast(app, app.waveInLevel))
            else:
                app.zombies.append(Zombie(app, app.waveInLevel))

    cx, cy = app.cursor

    # ---- ZOMBIE LOOP ----
        # ---- ZOMBIE LOOP ----
    for z in app.zombies[:]:
        z.update()
        zombieDied = False

        # ----- FLASHLIGHT DAMAGE OVER TIME -----
        if z.hit(cx, cy):
            z.applyFlashlightDamage()
            if z.isDead():
                app.zombies.remove(z)
                app.score += 1
                app.effects.append(Explosion(z.x, z.y))
                zombieDied = True

        if zombieDied:
            app.sun += 10
            continue

        # ----- BULLET COLLISION -----
        for bullet in app.bullets[:]:
            if bulletHitsZombie(bullet, z):
                # remove 1/4 HP
                z.timeOnCursor += (z.requiredTime / 4)
                app.bullets.remove(bullet)

                if z.isDead():
                    app.zombies.remove(z)
                    app.score += 1
                    app.effects.append(Explosion(z.x, z.y))
                    zombieDied = True
                break  # stop checking other bullets for this zombie

        if zombieDied:
            app.sun += 10
            continue

        # -------------------------------------------------
        # ----- TURRET COLLISION & ATTACK (SAME ROW) -----
        # -------------------------------------------------
        turretTarget = None
        zombieRow = int(z.y // app.tileH)

        for turret in app.turrets:
            turretRow = int(turret.y // app.tileH)

            # turret must be in SAME ROW
            if turretRow != zombieRow:
                continue

            # ----- ZOMBIE MUST BE LEFT OF TURRET -----
            if not (z.x + z.r <= turret.x + 40):
                continue

            # ----- ZOMBIE HAS REACHED TURRET -----
            if z.x + z.r >= turret.x - 40:
                turretTarget = turret
                break

        if turretTarget is not None:
            z.attacking = True
            z.attackTimer += 1

            if z.attackTimer >= 30:
                turretTarget.health -= 1
                z.attackTimer = 0
                app.effects.append(Explosion(turretTarget.x, turretTarget.y))
                print(f"[DEBUG] Turret Hit! HP = {turretTarget.health}")

                if turretTarget.health <= 0:
                    app.turrets.remove(turretTarget)
                    z.attacking = False  # resume walking

            continue

        # -------------------------------------------------
        # ----- HEALTH STATION COLLISION & ATTACK -----
        # -------------------------------------------------
        stationTarget = None

        for station in app.healthStations:
            stationRow = int(station.y // app.tileH)

            if stationRow != zombieRow:
                continue

            # ZOMBIE MUST BE LEFT OF STATION
            if not (z.x + z.r <= station.x + 40):
                continue

            # ZOMBIE HAS REACHED STATION
            if z.x + z.r >= station.x - 40:
                stationTarget = station
                break

        if stationTarget is not None:
            z.attacking = True
            z.attackTimer += 1

            if z.attackTimer >= 30:
                stationTarget.health -= 1
                z.attackTimer = 0
                app.effects.append(Explosion(stationTarget.x, stationTarget.y))
                print(f"[DEBUG] Station Hit! HP = {stationTarget.health}")

                if stationTarget.health <= 0:
                    app.healthStations.remove(stationTarget)
                    z.attacking = False  # resume walking

            continue

        # -------------------------------------------------
        # ----- FENCE COLLISION & ATTACK -----
        # -------------------------------------------------
        if (app.fenceLeft <= z.x + z.r <= app.fenceRight and
            app.fenceTop <= z.y <= app.fenceBottom):

            # zombie attacks fence
            z.attacking = True

            # deal 1 damage every second
            z.attackTimer += 1
            if z.attackTimer >= 30:
                app.baseHP -= 1
                z.attackTimer = 0
                app.effects.append(Explosion(app.fenceX, z.y))
                print(f"[DEBUG] Fence ATTACK! BaseHP = {app.baseHP}")

                if app.baseHP <= 0:
                    app.gameOver = True
            continue
        ############################################################
        # WAVE ENGINE — CLEAN, CORRECT, NO LOOPING
        ############################################################

            # countdown timer
    if app.waveTimer > 0:
        app.waveTimer -= 1

            # spawn zombies while timer > 0
            
        # ----------------------
        # CHECK FOR WAVE END
        # ----------------------
        # Wave ends when timer is done AND all zombies are dead
        
def nextWave(app):    
    if app.waveTimer <= 0 and len(app.zombies) <= 0:

            # Move to next wave or level
        if app.waveInLevel < app.maxWavesPerLevel:
            app.waveInLevel += 1
        else:
            if app.level < app.maxLevels:
                app.level += 1
                app.levelUp.play()
                app.waveInLevel = 1
            else:
                # Player finished all levels
                app.gameWin = True
                print("YOU WIN!")

            # Start countdown to next wave
        app.waveTimer = 600



############################################################
# DRAW EVERYTHING
############################################################
def gameScreen_redrawAll(app):
    # BACKGROUND + FIELD ELEMENTS
    drawTiles(app)
    drawGrass(app)
    drawFence(app)
    drawHealthStations(app)
    drawHealthStationsBar(app)
    drawHealingAnimations(app)
    drawTurrets(app)
    drawFlowers(app)
    drawBullets(app)
    drawDrones(app)
    drawExplodingDrones(app)
    #drawSparks(app)


    # ============================================================
    # SEED BANK UI (TOP-CENTER)
    # ============================================================
    leftPanelX = app.headerLeft - 80

    # Sun counter box
    drawRect(leftPanelX, 0, 80, app.headerHeight,
             fill='khaki', border='gold', borderWidth=4)

    drawGameText(str(app.sun),
                 leftPanelX + 40,
                 app.headerHeight / 2 - 10,
                 size=28,
                 color='red')

    drawGameText("FLEX $",
                 leftPanelX + 40,
                 app.headerHeight / 2 + 18,
                 size=15,
                 color='red')

    # Seed bank bar (corrected width)
    realWidth = app.rects[-1][2] - app.rects[0][0]
    drawRect(app.headerLeft, 0, realWidth, app.headerHeight,
            fill='burlywood', border='sienna', borderWidth=4)

    # Slots
    for i in range(app.numRects):
        x1, y1, x2, y2 = app.rects[i]

        # Slot color logic
        if app.errorSlot == i:
            slotFill = 'red'
        elif app.selected == i:
            slotFill = 'gold'
        else:
            slotFill = 'tan'

        drawRect(x1, y1, x2 - x1, y2 - y1,
                 fill=slotFill, border='sienna', borderWidth=3)

        slotCenterX = (x1 + x2) / 2
        slotCenterY = app.headerHeight * 0.37

        # Limit icon by HEIGHT only (keeps aspect ratio automatically)
        # Icon fits inside the slot WITHOUT stretching
        iconMaxW = (x2 - x1) * 0.9   # 90% of slot width
        iconMaxH = app.headerHeight * 0.45

        drawImageFit(app.itemImages[i],
                    slotCenterX, slotCenterY,
                    iconMaxW, iconMaxH)

        # Cost text
        drawGameText(str(app.costs[i]),
                    slotCenterX,
                    app.headerHeight * 0.85,
                    size=20,
                    color='white')

    # ============================================================
    # BASE HP BAR
    # ============================================================
    drawRect(20, 50, 260, 25, fill='red')
    if app.baseHP > 0:
        hpRatio = app.baseHP / BASE_MAX_HP
        drawRect(20, 50, 260 * hpRatio, 25, fill='lime')
    drawLabel(f"Base HP: {app.baseHP}", 70, 30, size=20, fill='white')

    # ZOMBIES
    for z in app.zombies:
        z.draw()

    # EXPLOSIONS
    for fx in app.effects:
        fx.draw()

    # CROSSHAIR
    cx, cy = app.cursor
    drawCircle(cx, cy, 22, border='white', borderWidth=3)
    drawLine(cx - 30, cy, cx + 30, cy, fill='white')
    drawLine(cx, cy - 30, cx, cy + 30, fill='white')

    # HUD
    drawLabel(f"Day: {app.level}", 70, 90, size=28, fill='cyan')
    drawLabel(f"Wave: {app.waveInLevel}/{app.maxWavesPerLevel}", 70, 130, size=28, fill='cyan')

    secondsLeft = app.waveTimer // app.stepsPerSecond
    drawLabel(f"Time Left: {secondsLeft}s", 90, 170, size=24, fill='white')

    # Wave timer finished but zombies still remain
    if app.waveTimer <= 0 and len(app.zombies) > 0:
        drawLabel(f"Zombies Remaining: {len(app.zombies)}", 100, 190, size=24, fill='orange')

    if app.gameOver:
        drawRect(0, 0, SCREEN_W, SCREEN_H, fill='black', opacity=70)
        drawLabel("YOU LOSE!", SCREEN_W/2, SCREEN_H/2 - 60,
                  size=80, fill='red', bold=True)
        drawLabel(f"Final Score: {app.score}",
                  SCREEN_W/2, SCREEN_H/2,
                  size=40, fill='white')
        drawLabel("Press R to restart",
                  SCREEN_W/2, SCREEN_H/2 + 70,
                  size=28, fill='white')
        
    if app.gameWin:
        drawRect(0, 0, SCREEN_W, SCREEN_H, fill='black', opacity=70)
        drawLabel("CONGRATS!", SCREEN_W/2, SCREEN_H/2 - 60,
                  size=80, fill='lightGreen', bold=True)
        drawLabel("You defended the fence for 5 days", SCREEN_W/2, SCREEN_H/2,
                  size=40, fill='white', bold=True)
        drawLabel(f"Final Score: {app.score}",
                  SCREEN_W/2, SCREEN_H/2 + 50,
                  size=40, fill='white')
        drawLabel("Press R to play again!",
                  SCREEN_W/2, SCREEN_H/2 + 110,
                  size=28, fill='white')

### MENU SCREEN ###

def menuScreen_redrawAll(app):
    drawImage("images/hack112menuscreen.png", 0, 0)
    drawGameStart(app)
    drawHistoryButton(app)

def drawGameStart(app):
    blue = rgb(34, 110, 239)
    bolded = True if app.gameStartHover else False
    drawRect(569, 662, 186, 76, fill=blue, align='center')
    drawLabel('Start Game', 569, 662, size=20, bold=bolded, fill='white', font='monospace')

def drawHistoryButton(app):
    blue = rgb(34, 110, 239)
    bolded = True if app.historyHover else False
    drawRect(943, 662, 186, 76, fill=blue, align='center')
    drawLabel('Fence History', 943, 662, size=20, bold=bolded, fill='white', font='monospace')

### HISTORY ###

def history_redrawAll(app):
    drawHistory(app)

def drawHistory(app):
    pageSelect = app.selectedTimeline
    drawImage(app.historyDict[pageSelect], 0, 0)

    bolded = True if app.goBackHover else False
    drawLabel('<<< Back to Menu', 1398, 808, fill='white', bold=bolded, size=20, font='arial')

### MENU INTERACTION ###

def menuScreen_onMouseMove(app, mouseX, mouseY):
    thisRect = getRect(mouseX, mouseY)
    if thisRect == 'start':
        app.gameStartHover = True
        app.historyHover = False
    elif thisRect == 'history':
        app.gameStartHover = False
        app.historyHover = True
    else:
        app.gameStartHover = False
        app.historyHover = False

def menuScreen_onMousePress(app, mouseX, mouseY):
    thisRect = getRect(mouseX, mouseY)
    #buttonPress = Sound("buttonClick.mp3")
    if thisRect == 'start':
        setActiveScreen('howToPlay')
        #buttonPress.play(restart=False, loop=False)
    elif thisRect == 'history':
        setActiveScreen('history')
        #buttonPress.play(restart=False, loop=False)
    else:
        return
        
def getRect(mouseX, mouseY):
    #to be in start button
    if (477 <= mouseX <= 663) and (624 <= mouseY <= 700):
        return 'start'
    
    #to be in history
    if (850 <= mouseX <= 1036) and (624 <= mouseY <= 700):
        return 'history'
    
### HISTORY INTERACTION ####

def history_onMouseMove(app, mouseX, mouseY):
    if (1292 <= mouseX <= 1504) and (779 <= mouseY <= 825):
        app.goBackHover = True
    else:
        app.goBackHover = False

def history_onMousePress(app, mouseX, mouseY):
    pageSelect = selectPage(mouseX, mouseY)
    if pageSelect != None:
        app.selectedTimeline = pageSelect
    if (1292 <= mouseX <= 1504) and (779 <= mouseY <= 825):
        app.selectedTimeline = 0
        setActiveScreen('menuScreen')

def selectPage(mouseX, mouseY):
    width = 188
    if (52 <= mouseY <= 120):
        if (53 <= mouseX <= 53+width):
            return 1
        elif (297 <= mouseX <= 297+width):
            return 2
        elif (540 <= mouseX <= 540+width):
            return 3
        elif (784 <= mouseX <= 784+width):
            return 4
        elif (1027 <= mouseX <= 1027+width):
            return 5
        elif (1270 <= mouseX <= 1270+width):
            return 6
        
def howToPlay_redrawAll(app):
    drawImage('images/howToPlay.png', 0, 0)

### HOW-TO-PLAY INTERACTION ###

def howToPlay_onMousePress(app, mouseX, mouseY):
    if (535 <= mouseX <= 977) and (784 <= mouseY <= 900):
        resetGame(app)
        setActiveScreen('gameScreen')


def menuScreen_onScreenActivate(app):
    app.menuMusic.play(restart=True, loop=True)

def howToPlay_onScreenActivate(app):
    app.menuMusic.pause()

def history_onScreenActivate(app):
    app.menuMusic.pause()

############################################################
# KEY PRESS
############################################################
def gameScreen_onKeyPress(app, key):
    if key.lower() == 'r':
        if app.gameOver:
            resetGame(app)
        elif app.gameWin:
            setActiveScreen('menuScreen')

    ### FOR DEMO
    if key == 'w':
        app.gameWin = True

    if key == '5':
        app.level = 5


############################################################
# RUN APP
############################################################
runAppWithScreens(initialScreen='menuScreen', width=SCREEN_W, height=SCREEN_H)