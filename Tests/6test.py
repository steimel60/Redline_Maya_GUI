import maya.cmds as cmds

filename='C:\\Users\\DylanSteimel\\Desktop\\anotherone.xyz'
stepSize=100

f = open(filename, 'r')
full = [line.rstrip().split(' ') for line in f.readlines()[::stepSize]]
particleList, colorList = [(float(pos[0]), float(pos[1]), float(pos[2])) for pos in full], [(float(color[3])/255, float(color[4])/255, float(color[5])/255) for color in full]
xmin, ymin, zmin = min([float(x[0]) for x in full]), min([float(y[1]) for y in full]), min([float(z[2]) for z in full])
xVert, yVert, zVert = [particle for particle in particleList if particle[0]==xmin], [particle for particle in particleList if particle[1]==ymin], [particle for particle in particleList if particle[2]==zmin]
xmax, ymax, zmax = max([float(x[0]) for x in full]), max([float(y[1]) for y in full]), max([float(z[2]) for z in full])
f.close()

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def Left_index(points):
    '''
    Finding the left most point
    '''
    minn = 0
    for i in range(1,len(points)):
        if points[i].x < points[minn].x:
            minn = i
        elif points[i].x == points[minn].x:
            if points[i].y > points[minn].y:
                minn = i
    return minn

def orientation(p, q, r):
    '''
    To find orientation of ordered triplet (p, q, r).
    The function returns following values
    0 --> p, q and r are colinear
    1 --> Clockwise
    2 --> Counterclockwise
    '''
    val = (q.y - p.y) * (r.x - q.x) - \
          (q.x - p.x) * (r.y - q.y)

    if val == 0:
        return 0
    elif val > 0:
        return 1
    else:
        return 2

def convexHull(points, n):

    # There must be at least 3 points
    if n < 3:
        return

    # Find the leftmost point
    l = Left_index(points)

    hull = []

    '''
    Start from leftmost point, keep moving counterclockwise
    until reach the start point again. This loop runs O(h)
    times where h is number of points in result or output.
    '''
    p = l
    q = 0
    while(True):

        # Add current point to result
        hull.append(p)

        '''
        Search for a point 'q' such that orientation(p, q,
        x) is counterclockwise for all points 'x'. The idea
        is to keep track of last visited most counterclock-
        wise point in q. If any point 'i' is more counterclock-
        wise than q, then update q.
        '''
        q = (p + 1) % n

        for i in range(n):

            # If i is more counterclockwise
            # than current q, then update q
            if(orientation(points[p],
                           points[i], points[q]) == 2):
                q = i

        '''
        Now q is the most counterclockwise with respect to p
        Set p as q for next iteration, so that q is added to
        result 'hull'
        '''
        p = q

        # While we don't come to first point
        if(p == l):
            break

    # Print Result
    return hull
    #for each in hull:
        #print(points[each].x, points[each].y)





sliceCount = 250
zRange = zmax-zmin
zStep = zRange/sliceCount
yRange = ymax-ymin
yStep = yRange/sliceCount
xRange = xmax-xmin
xStep = xRange/sliceCount


for i in range(0,sliceCount):
    z = zmin + i*zStep
    err = .01
    Set = [(particle[0], particle[1]) for particle in particleList if abs(particle[2]-z)<err]
    points = [Point(particle[0], particle[1]) for particle in Set]
    hull = convexHull(points, len(points))
    if hull != None:
        curvePoints = [(Set[value][0],Set[value][1],z) for value in hull]
        curvePoints.append(curvePoints[0])
        newCurve = cmds.curve(p=curvePoints)
        curves.append(newCurve)
        print('Slice ' + str(i) + ' of ' + str(sliceCount))



#for i in range(0,sliceCount):
#    y = ymin + i*yStep
#    err = .01
#    Set = [(particle[0], particle[2]) for particle in particleList if abs(particle[1]-y)<err]
#    points = [Point(point[0], point[1]) for point in Set]
#    hull = convexHull(points, len(points))
#    if hull != None:
#        curvePoints = [(Set[value][0],y,Set[value][1]) for value in hull]
#        curvePoints.append(curvePoints[0])
#        cmds.curve(p=curvePoints)
#        print('Slice ' + str(i) + ' of ' + str(sliceCount))

#for i in range(0,sliceCount):
#    x = xmin + i*xStep
#    err = .01
#    Set = [(particle[1], particle[2]) for particle in particleList if abs(particle[0]-x)<err]
#    points = [Point(point[0], point[1]) for point in Set]
#    hull = convexHull(points, len(points))
#    if hull != None:
#        curvePoints = [(x,Set[value][0],Set[value][1]) for value in hull]
#        curvePoints.append(curvePoints[0])
#        cmds.curve(p=curvePoints)
