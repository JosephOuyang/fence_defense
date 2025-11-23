# Base template for CMU Graphics animations
# Updated to use onAppStart and redrawAll, with grass details

from cmu_graphics import *
import random

print('h')

def onAppStart(app):
    app.width = 1550
    app.height = 1000
    app.tilesWide = 20
    app.tilesHigh = 10
    app.tileW = app.width / app.tilesWide
    app.tileH = app.height / app.tilesHigh

    app.baseColor = rgb(40, 150, 40)
    app.lightColor = rgb(50, 170, 50)

    app.grassSprites = []
    generateGrass(app)
    app.circleX = 200
    app.circleY = 200
    app.circleRadius = 40
    app.circleColor = 'red'
    app.stepsPerSecond = 30
    app.squareX = 100
    app.squareY = 200
    app.squareW = 60
    app.squareColor = 'blue'
    app.dx = 3
    app.dy = 2

    app.fencePosts = []
    app.fencePlanks = []
    numPosts = 6
    postRadius = 15
    plankThickness = 10
    fenceX = app.width-150                  # distance from left edge
    fenceHeight = 650             # total span of fence
    fenceTop = (app.height - fenceHeight) / 2
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
                app.grassSprites.append({
                    'x': cx,
                    'y': cy,
                    'scale': scale
                })

def onStep(app):
    app.circleX += app.dx
    app.circleY += app.dy
    if app.circleX < 0 or app.circleX > app.width:
        app.dx = -app.dx
    if app.circleY < 0 or app.circleY > app.height:
        app.dy = -app.dy

def onKeyPress(app, key):
    if key == 'up': app.squareY -= 10
    elif key == 'down': app.squareY += 10
    elif key == 'left': app.squareX -= 10
    elif key == 'right': app.squareX += 10

def onMousePress(app, x, y):
    app.circleX = x
    app.circleY = y

def drawTiles(app):
    for row in range(app.tilesHigh):
        for col in range(app.tilesWide):
            x = col * app.tileW
            y = row * app.tileH
            if (row + col) % 2 == 0:
                color = app.baseColor
            else:
                color = app.lightColor
            drawImage(
                "images/grassTile.png",
                x, y,
                align='center',
                width=80,
                height=100
                        )
            #drawRect(x, y, app.tileW, app.tileH, fill=color)

def drawGrass(app):
    for blade in app.grassSprites:
        drawImage(
            "images/grass.png",
            blade['x'],
            blade['y'],
            align='center',
            width=50 * blade['scale'],
            height=50 * blade['scale']
        )

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

def redrawAll(app):
    # Draw tiles
    drawTiles(app)
    drawGrass(app)
    drawFence(app)
    #drawCircle(app.circleX, app.circleY, app.circleRadius, fill=app.circleColor)
    drawRect(app.squareX, app.squareY, app.squareW, app.squareW, fill=app.squareColor)

def main():
    runApp()

main()