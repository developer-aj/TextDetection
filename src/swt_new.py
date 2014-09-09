"""
    swt Preforms stoke width transform on input image
    A novel image operator that seeks to find the value of stroke width
    for each image pixel.  It's use is meant for the task of text
    detection in natural images.

    im = RGB input image of size m x n x 3
    searchDirection = gradient direction is either 1 to detect dark text on light
    background or -1 to detect light text on dark background.

    swtMap = resulting mapping of stroke withs for image pixels
"""

from numpy import *
import numpy
import math
import cv2
import cv2.cv as cv
from decimal import *

def swt(name, searchDirection):

    src = cv2.imread(name)
    
    # gray image
    imgray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    cv2.imwrite("gray.jpg", imgray)
    #cv2.imshow("gray", imgray)

    # detecting MSER regions
    vis = src.copy()
    mser = cv2.MSER()
    regions = mser.detect(imgray, None)
    hulls = [cv2.convexHull(p.reshape(-1, 1, 2)) for p in regions]
    cv2.polylines(vis, hulls, 1, (0, 255, 0))
    #print regions
    cv2.imwrite("mser.jpg", vis)

    # initialize
    edgePointRows = []
    edgePointCols = []
    height = size(imgray, 0)
    width = size(imgray, 1)
    pixels = height*width

    # Find edges using canny edge detector
    edgeMap = cv2.Canny(imgray, 320, 160)
    cv2.imwrite("canny.jpg", edgeMap)

    vis = cv2.cvtColor(vis, cv2.COLOR_BGR2GRAY)
    final = vis & edgeMap
    cv2.imwrite("fin.jpg", final)

    # Get all edge pixel positions
    for row in range(height):
        for col in range(width):
            if(edgeMap[row][col] > 0):
                edgePointRows.append(row)
                edgePointCols.append(col)

    # Find horizontal & vertical gradients
    dx = cv2.Sobel(imgray, cv2.CV_8U, 1, 0, ksize = 5)
    dy = cv2.Sobel(imgray, cv2.CV_8U, 0, 1, ksize = 5)

    """(minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(dx)
    ret,dx = cv2.threshold(dx, 255.0/(maxVal - minVal), -minVal * 255.0/(maxVal - minVal), cv2.THRESH_BINARY)
    (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(dy)
    ret,dy = cv2.threshold(dy, 255.0/(maxVal - minVal), -minVal * 255.0/(maxVal - minVal), cv2.THRESH_BINARY)
"""
    cv2.imwrite("gradx.jpg", dx)
    cv2.imwrite("grady.jpg", dy)
    
    # initializing matrix of gradient direction
    theta = array(random.randint(255, 256, pixels)).reshape(height, width)

    # calculating theta
    for row in range(height):
        for col in range(width):
            if(edgeMap[row][col] > 0):
                theta[row][col] = math.atan2(dy[row][col], dx[row][col])
    cv2.imwrite("theta.jpg", theta)

    # initializing stroke width array with infinity
    swtMap = array(random.randint(255.0, 256.0, pixels)).reshape(height, width)

    # Set the maximum stroke width. this number is variable for now but must be
    # made to be more dynamic in the future
    maxStrokeWidth = 350

    # Initialize container for all stroke points found
    strokePointsX = zeros(size(edgePointCols))
    strokePointsY = zeros(size(strokePointsX))
    sizeOfStrokePoints = 0
    #print len(strokePointsX), len(strokePointsY)
    
    # Iterate through all edge points and compute stoke widths
    for i in range(size(edgePointRows)):
        step = 1
        initialX = edgePointRows[i]
        initialY = edgePointCols[i]
        isStroke = 0
        initialTheta = theta[initialX][initialY]
        sizeOfRay = 0
        pointOfRayX = array(random.randint(0, 1, maxStrokeWidth))
        pointOfRayY = array(random.randint(0, 1, maxStrokeWidth))

        # record first point of the ray
        pointOfRayX[sizeOfRay] = initialX
        pointOfRayY[sizeOfRay] = initialY

        # increase the size of the ray
        sizeOfRay += 1

        # follow the ray
        while step < maxStrokeWidth:
            nextX = numpy.round(initialX + cos(initialTheta) * searchDirection * step)
            nextY = numpy.round(initialY + sin(initialTheta) * searchDirection * step)

            step += 1
            
            # Break loop if out of bounds.  For some reason this is really slow.
            if (nextX < 0 or nextY < 0 or nextX >= height or nextY >= width):
                break

            # record next point of the ray
            pointOfRayX[sizeOfRay] = nextX
            pointOfRayY[sizeOfRay] = nextY

            # increase size of the ray
            sizeOfRay += 1

            # another edge pixel has been found
            if edgeMap[nextX][nextY]:
                oppositeTheta = theta[nextX][nextY]

                # gradient direction roughly opposite
                if (oppositeTheta >= (-initialTheta - pi/6) or oppositeTheta <= (-initialTheta + pi/6)) :
                    isStroke = 1
                    strokePointsX[sizeOfStrokePoints] = initialX
                    strokePointsY[sizeOfStrokePoints] = initialY
                    sizeOfStrokePoints += 1
                    #print "."

                break
            
        # edge pixel is part of stroke
        if isStroke :

            # calculate stroke width
            strokeWidth = math.sqrt((nextX - initialX)**2 + (nextY - initialY)**2)

            # iterate all ray points and populate with minimum stroke width
            for j in range(sizeOfRay):
                swtMap[pointOfRayX[j]][pointOfRayY[j]] = min(swtMap[pointOfRayX[j]][pointOfRayY[j]], strokeWidth)
    
    # writing images
    cv2.imwrite("swt_pass1.jpg", swtMap)

    # Iterate through all stoke points for a refinement pass.
    # Refer to figure 4b in the paper.
    for i in range(sizeOfStrokePoints):
        step = 1
        initialX = strokePointsX[i]
        initialY = strokePointsY[i]
        initialTheta = theta[initialX][initialY]
        sizeOfRay = 0
        pointOfRayX = array(random.randint(0, 1, maxStrokeWidth))
        pointOfRayY = array(random.randint(0, 1, maxStrokeWidth))
        swtValues = array(random.randint(0, 1, maxStrokeWidth))
        sizeOfSWTValues = 0

        # record first point of the ray
        pointOfRayX[sizeOfRay] = initialX
        pointOfRayY[sizeOfRay] = initialY

        # increase the size of the ray
        sizeOfRay += 1

        # record the swt value of the first stroke point
        swtValues[sizeOfSWTValues] = swtMap[initialX][initialY]
        sizeOfSWTValues += 1

        
        # follow the ray
        while step < maxStrokeWidth:
            nextX = round(initialX + cos(initialTheta) * searchDirection * step)
            nextY = round(initialY + sin(initialTheta) * searchDirection * step)

            step += 1

            # record next point of the ray
            pointOfRayX[sizeOfRay] = nextX
            pointOfRayY[sizeOfRay] = nextY

            # increase size of the ray
            sizeOfRay += 1

            # record the swt value of next stroke point
            swtValues[sizeOfSWTValues] = swtMap[nextX][nextY]
            sizeOfSWTValues += 1

            # another edge pixel has been found
            if edgeMap[nextX][nextY]:
                break

        # calculate stroke width as the median value of all swtValues seen
        strokeWidth = median(swtValues[0:sizeOfSWTValues])

        # Iterate all ray points and populate with the minimum stroke width
        for j in range(sizeOfRay):
            swtMap[pointOfRayX[j]][pointOfRayY[j]] = min(swtMap[pointOfRayX[j]][pointOfRayY[j]], strokeWidth)

    cv2.imwrite("swt_pass2.jpg", swtMap)
    print sizeOfStrokePoints

swt("lena.jpg", -1)
