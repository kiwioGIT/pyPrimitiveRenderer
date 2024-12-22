def drawLine(p1,p2, val,screen): ## jednoduchy algorytmus na kresleni car
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]

    if abs(dx) > abs(dy): # tady se to musi rozdelit na dve strany protoze vzdycky musim postupovat podle toho co je delsi bud dx nebo dy
        slope = dy / dx # sklon cary
        for i in range(0,int(dx),int(math.copysign(1,dx))):
            put((int(p1[0] + i), int( p1[1] + i * slope)), val, screen)
    else:
        slope = dx / dy # sklon cary ale naopak
        for i in range(0,int(dy),int(math.copysign(1,dy))):
            put((int(p1[0] + i * slope), int( p1[1] + i)), val, screen)