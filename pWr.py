import os
import numpy as np
import math
import keyboard as kb

class camC:
    pos = np.array([1.0,-0.5,-5.0])
    vRot = 0
    hRot = 0
    vSin = 0
    vCos = 1
    hSin = 0
    hCos = 1
    nearZ = 35

class surface:
    data = np.array([])
    width, heigth = 0,0

## Globalni promenne
gPoints = []
gLines = []
gCam = camC()
gScreen = surface()
gScreen.width = 70
gScreen.heigth = 40
gScreen.data = np.array([0 for i in range(gScreen.heigth * gScreen.width)])
##

def loadObj(path, points, lines): ## nacete wavefront .obj soubor
    points[:] = []
    lines[:] = []
    objFile = open(path, "r")
    ## pokusim se to nejak popsat strukturu .obj souboru
    for textLine in objFile: # .obj soubory jsou rozdelene radkama
        tlData = textLine.split(" ")
        if textLine[0] == "v": # pokud radek zacina n "v" tak to znaci Vertex neboli Bod a nasleduji tri cisla ktera rikaji jeho pozici v prostoru
            points.append(np.array([float(tlData[1]),float(tlData[2]),float(tlData[3])]))
        if textLine[0] == "f": # pokud radek zacina na "f" cili Face znaci Stenu, a nasleduji obvykle 3 nebo i vice indexy bodu ktere stenu tvori, (tento program pocita jen se trema)
            lines.append((int(tlData[1].split("/")[0]) - 1, int(tlData[2].split("/")[0]) - 1)) # tento program ale neumi kreslit steny a misto toho nakresli 3 cary
            lines.append((int(tlData[2].split("/")[0]) - 1, int(tlData[3].split("/")[0]) - 1))
            lines.append((int(tlData[3].split("/")[0]) - 1, int(tlData[1].split("/")[0]) - 1))
        if textLine[0] == "l":
            lines.append((int(tlData[1]) - 1, int(tlData[2]) - 1))
    
def hRotated( v, sine, cosine): ## Vraci vektor v otoceny kolem svisle osy o uhel predpocitany do sine a cosine
    nV = v.copy()
    nV[0] = cosine * v[0] - sine * v[2]
    nV[2] = sine * v[0] + cosine * v[2]
    return nV

def vRotated( v, sine, cosine):## Vraci vektor v otoceny kolem horizontalni osy o uhel predpocitany do sine a cosine
    nV = v.copy()
    nV[2] = cosine * v[2] - sine * v[1]
    nV[1] = sine * v[2] + cosine * v[1]
    return nV

def drawScreen(screen):
    os.system('cls' if os.name == 'nt' else 'clear')
    for c in range(screen.heigth * screen.width):
        "██"
        print("##",end="") if screen.data[c] == 1 else print("  ",end="")
        if (c+1)%screen.width == 0:
            print("X")

def put(pos, val, screen): ## nastavi v bod na pozici pos v poli screen na hodnotu val, pritom overi ze je bod opravdu v poli
    if pos[0] >= screen.width or pos[0] < 0:
        return
    if pos[1] >= screen.heigth or pos[1] < 0:
        return
    screen.data[pos[1] * screen.width + pos[0]] = val

def project(origin, cam):## prepocita kde by se mel vektor origin nachazed na obrazovce kamery cam
    nOrigin = origin - cam.pos # protoze zbytek funkce predpoklada ze kamera je v pocatku tak musime vektor posunout
	
    nOrigin = hRotated(nOrigin, cam.hSin, cam.hCos) # pak otocit 
    nOrigin = vRotated(nOrigin, cam.vSin, cam.vCos)

    ## cim je neco dal tim mensi to musi na obrazovce vypadat
    ## proto delime souradnice x a y souradnici z
    scale = nOrigin[2] / cam.nearZ
    nOrigin[0] = nOrigin[0] / scale
    nOrigin[1] = nOrigin[1] / scale 
    return nOrigin

def clear(screen):
    screen.data[:] = np.zeros(screen.width * screen.heigth)

def drawLine(p1,p2,screen): ## jednoduchy algorytmus na kresleni car
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]

    if abs(dx) > abs(dy): # tady se to musi rozdelit na dve strany protoze vzdycky musim postupovat podle toho co je delsi bud dx nebo dy
        slope = dy / dx # sklon cary
        for i in range(0,int(dx),int(math.copysign(1,dx))):
            put((int(p1[0] + i), int( p1[1] + i * slope)), 1, screen)
    else:
        slope = dx / dy # sklon cary ale naopak
        for i in range(0,int(dy),int(math.copysign(1,dy))):
            put((int(p1[0] + i * slope), int( p1[1] + i)), 1, screen)

def drawHzLine(p1, p2, screen):
    if p1[0] < p2[0]:
        for i in range(p2[0] - p1[0]):
            put(p1 + np.array([i,0,0]), 1, screen)
    else:
        for i in range(p2[0] - p1[0]):
            put(p1 + np.array([i,0,0]), 1, screen)

def fillFlatTriangle(v1, v2, v3, screen): ## assumes vertix order
    slope1 = (v2[0] - v1[0]) / (v2[1] - v1[1])
    slope2 = (v3[0] - v1[0]) / (v3[1] - v1[1])

    x1 = v1[0]
    x2 = v1[0]
    for yLine in range(v1[1], v2[1] + 1):
        drawHzLine(np.array([int(x1), yLine,0]), np.array([int(x2), yLine,0]), screen)
        x1 += slope1
        x2 += slope2

def fillReverseFlatTriangle(v1, v2, v3, screen): ## assumes vertix order
    slope1 = (v3[0] - v1[0]) / (v3[1] - v1[1])
    slope2 = (v3[0] - v2[0]) / (v3[1] - v2[1])

    x1 = v3[0]
    x2 = v3[0]
    for yLine in range(v3[1], v1[1], -1):
        drawHzLine(np.array([int(x1), yLine,0]), np.array([int(x2), yLine,0]), screen)
        x1 -= slope1
        x2 -= slope2



def fillTriangle(p1, p2, p3, value, sceen):
    pass



def drawLines(points, lines, screen): ## Vykresli vsecky cary
    projectedPoints = [project(point,gCam) for point in points]
    for line in lines:
        if projectedPoints[line[0]][2] < 0 or projectedPoints[line[1]][2] < 0:
            continue
        drawLine(projectedPoints[line[0]] + [screen.width // 2, screen.heigth // 2 , 0], projectedPoints[line[1]] + [screen.width // 2, screen.heigth // 2 , 0], screen)



fillFlatTriangle(np.array([10,5,0]),np.array([0, 15,0]),np.array([20,15,0]),gScreen)
drawScreen(gScreen)

"""
while True: ## hlavni smycka
    clear(gScreen)
    drawLines(gPoints, gLines, gScreen)
    drawScreen(gScreen)
    if kb.is_pressed("escape"):
        inp = input(">>")
        if inp == "q" or inp == "quit":
            break
        if inp[:4] == "load":
            ln = inp.split()
            try:
                loadObj(ln[1], gPoints, gLines)
            except:
                print("something went wrong")
        if inp[:4] == "setw":
            ln = inp.split()
            try:
                gScreen.width = int(ln[1])
                gScreen.heigth = int(ln[2])
                gCam.nearZ = int(ln[1]) // 2
                gScreen.data = []
            except:
                print("no")
    moveVec = np.array([0.0,0.0,0.0])
    if kb.is_pressed("a"):
        moveVec[2] += 0.1
    if kb.is_pressed("d"):
        moveVec[2] -= 0.1
    if kb.is_pressed("w"):
        moveVec[0] += 0.1
    if kb.is_pressed("s"):
        moveVec[0] -= 0.1
    if kb.is_pressed("space"):
        moveVec[1] -= 0.1
    if kb.is_pressed("shift"):
        moveVec[1] += 0.1
    if kb.is_pressed("left"):
        gCam.hRot -= 0.05
    if kb.is_pressed("right"):
        gCam.hRot += 0.05
    if kb.is_pressed("up"):
        gCam.vRot += 0.05
    if kb.is_pressed("down"):
        gCam.vRot -= 0.05
    
    gCam.hSin = math.sin(gCam.hRot)
    gCam.hCos = math.cos(gCam.hRot)

    gCam.vSin = math.sin(gCam.vRot)
    gCam.vCos = math.cos(gCam.vRot)
    
    moveVec = hRotated(moveVec,gCam.hCos,gCam.hSin)
    gCam.pos = gCam.pos + moveVec
"""