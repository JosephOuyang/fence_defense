from cmu_graphics import *
import random
import math

class Grass:
    def __init__(self, x, y, scale):
        self.image= "images/grass.png"
        self.x=x
        self.y=y
        self.scale=scale

class HealthStation:
    def __init__(self, x, y):
        self.image = "images/healthStation.png"
        self.x = x 
        self.y = y
        self.health = 20
        self.pulse = 5

class Bullet:
    def __init__(self, x, y):
        self.image = "images/bullet.png"
        self.x = x
        self.y = y
        self.dx = -4

def distance(x1, y1, x2, y2):
    return ((x2 - x1)**2 + (y2 - y1)**2)**0.5

class Turret:
    def __init__(self, x, y):
        self.image = "images/turret.png"
        self.x = x
        self.y = y
        self.health = 100
        self.steps = 0

def onAppStart(app):
    app.width = 1550
    app.height = 1000
    app.tilesWide = 20
    app.tilesHigh = 10
    app.tileW = app.width / app.tilesWide
    app.tileH = app.height / app.tilesHigh
    app.steps = 0
    app.baseColor = rgb(40, 150, 40)
    app.lightColor = rgb(50, 170, 50)
    app.stepsPerSecond = 100
    app.bullets = []
    app.turrets = []
    app.healthStations = []
    app.numCoins = 0
    app.grassSprites = []
    generateGrass(app)
    app.isTurrets = True
    app.healRadius = 100
    app.healRadius = 60
    app.healAmount = 0.2
    app.maxTurretHealth = 5
    
    # animation pulses
    app.healPulse = 5
    app.healPulseSpeed = 4
    app.healPulseMax = 25
    app.healPulseMin = 5

    app.fencePosts = []
    app.fencePlanks = []
    numPosts = 6
    postRadius = 15
    plankThickness = 10
    fenceX = app.width-150                  # distance from left edge
    fenceHeight = 650             # total span of fence
    fenceTop = 100
    spacing = fenceHeight / (numPosts - 1)

    # Generate vertical fence posts
    for i in range(numPosts):
        y = fenceTop + i * spacing
        app.fencePosts.append((fenceX, y, postRadius))

    # Generate planks between posts
    for i in range(numPosts - 1):
        y1 = fenceTop + i * spacing
        y2 = fenceTop + (i + 1) * spacing
        app.fencePlanks.append((fenceX, y1, y2, plankThickness))

def generateGrass(app):
    density = 0.10
    for row in range(app.tilesHigh):
        for col in range(app.tilesWide):
            if random.random() < density:
                cx = col * app.tileW + app.tileW/2 + random.randint(-40, 40)
                cy = row * app.tileH + app.tileH/2 +random.randint(-30, 30)
                scale = random.uniform(0.4, 1.0)
                app.grassSprites.append(Grass(cx, cy, scale))

def onStep(app):
    app.steps+=1
    addBullets(app)
    moveBullets(app)
    healNearbyTurrets(app)

def healNearbyTurrets(app):
    for turret in app.turrets:
        for station in app.healthStations:
            dist = distance(turret.x, turret.y, station.x, station.y)
            station.pulse -= 1
            station.pulse = max(app.healPulseMin, min(app.healPulseMax, station.pulse))
            # If turret is within healing radius
            if dist <= app.healRadius:
                turret.health = min(100,turret.health + 3)
                station.pulse+=app.healPulseSpeed
                station.pulse = min(app.healPulseMax, station.pulse)

def addBullets(app):
    for turret in app.turrets:
        turret.steps+=1
        if turret.steps==60:
            app.bullets.append(Bullet(turret.x-35, turret.y))
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

def onMousePress(app, x, y):
    row, col = getCell(app, x, y)
    if row!=None:
        cy = (1 + row) * app.tileH #+ (app.tileW /2)
        cx = (1 + col) * app.tileW #+ (app.tileH /2)
        if isLegalPlacement(app, cx, cy):
            if app.isTurrets:
                app.turrets.append(Turret(cx, cy))
                app.bullets.append(Bullet(x-35, cy))
            else: 
                app.healthStations.append(HealthStation(cx, cy))

def isLegalPlacement(app, cx, cy):
    for turret in app.turrets:
        if (turret.x==cx and turret.y==cy):
            return False
    for healthStation in app.healthStations:
        if (healthStation.x==cx and healthStation.y==cy):
            return False
    return True

def drawTiles(app):
    for row in range(app.tilesHigh):
        for col in range(app.tilesWide):
            x = col * app.tileW
            y = row * app.tileH
            drawImage(
                "images/grassTile.png",
                x, y,
                align='center',
                width=80,
                height=100
                        )

def getCell(app, x, y):
    row = math.floor(y / app.tileH)
    col = math.floor(x / app.tileW)
    if (0 <= row < app.tilesHigh) and (0 <= col < app.tilesWide):
        return (row, col)
    else:
        return None, None

def onKeyPress(app, key):
    if key=='1':
        app.isTurrets = not app.isTurrets

def drawGrass(app):
    for blade in app.grassSprites:
        drawImage(blade.image, blade.x, blade.y, 
                align='center', width = 50*blade.scale,
                height=50*blade.scale)
            # "grass.png",
            # blade['x'],
            # blade['y'],
            # align='center',
            # width=50 * blade['scale'],
            # height=50 * blade['scale']

def drawFence(app):
    for (x, y1, y2, thickness) in app.fencePlanks:
        drawRect(x - thickness/2, y1,
                 thickness,
                 y2 - y1,
                 fill=rgb(38, 85, 255),
                 border=rgb(47, 47, 252))
    for (x, y, r) in app.fencePosts:
        drawCircle(x, y, r,
                   fill=rgb(75, 127, 252),
                   border=rgb(37, 79, 179))

def drawTurrets(app):
    for turret in app.turrets:
        drawImage(turret.image, turret.x, turret.y, 
                    align ='center', width=90, height=70)

def drawBullets(app):
    for bullet in app.bullets:
        drawImage(bullet.image, bullet.x, bullet.y, 
                    align ='center', width=30, height=15)

def drawHealthStations(app):
    for healthStation in app.healthStations:
        drawImage(healthStation.image, healthStation.x, healthStation.y, 
                    align ='center', width=90, height=70)
    
def drawHealingAnimations(app):
    for station in app.healthStations:
        # alpha fades with pulse
        opacity = int(80 * (station.pulse/ app.healPulseMax))
        print(opacity)
        # outer healing ring
        drawCircle(station.x, station.y,
                   station.pulse,
                   fill=None,
                   border='lightGreen',
                   borderWidth=3,
                   opacity=opacity)

def redrawAll(app):
    drawTiles(app)
    drawGrass(app)
    drawFence(app)
    drawHealthStations(app)
    drawHealingAnimations(app)
    drawTurrets(app)
    drawBullets(app)

def main():
    runApp()

main()