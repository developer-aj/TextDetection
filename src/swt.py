import cv2
import cv2.cv as cv
import numpy as np
import math

def text(src):
    
    imgray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(imgray, 175, 320)
    """edgepoints = []
    for row in range(0, len(edges)):
        for col in range(0, len(edges[0])):
            if(edges[row][col] > 0):
                edgepoints.append([col, row])
                print "[", row, ",", col, "]"
    print edgepoints"""
    imgaussian = cv2.GaussianBlur(imgray, (5, 5), 0)

    # gradient x and y
    imgradx = cv2.Sobel(imgaussian, cv.CV_SCHARR, 1, 0, ksize = 5)
    imgrady = cv2.Sobel(imgaussian, cv.CV_SCHARR, 0, 1, ksize = 5)

    # initializing stroke image
    stroke = imgray
    for i in range(0, len(stroke)):
        for j in range(0, len(stroke[0])):
            stroke[i][j] = -1
    """theta = imgray
    for i in range(len(edges)):
        for j in range(len(edges[0])):
            if(edges[i][j] == 1):
                theta[i][j] = math.atan2(imgrady[i][j], imgradx[i][j])"""
    # saving images
    #cv2.imwrite("theta.jpg", theta)
    #cv2.imwrite("gray.jpg", imgray)
    cv2.imwrite("gradx.jpg", imgradx)
    cv2.imwrite("grady.jpg", imgrady)
    cv2.imwrite("gaussian.jpg", imgaussian)
    cv2.imwrite("canny.jpg", edges)
    cv2.imwrite("swt.jpg", swt(edges, imgradx, imgrady, stroke, True))

def swt(edge, gradx, grady, imtemp, dark_on_light):
    stroke = imtemp
    ray = []
    prec = 0.05
    for row in range(0, len(edge)):
        for col in range(0, len(edge[0])):
            if(edge[row][col]>0):
                k = 1
                #759546
                points = []
                p = (col, row)
                ray.append(col)
                ray.append(row)
                points.append(p)
                
                curx = float(col) + 0.5
                cury = float(row) + 0.5
                curpixx = col
                curpixy = row
                
                gx = float(gradx[row][col])
                gy = float(grady[row][col])

                # normalize gradient
                if(gx != 0 and gy != 0):
                    mag = float((gx**2 + gy**2)**0.5)

                    if(dark_on_light):
                        gx = -gx/mag
                        gy = -gy/mag
                    else:
                        gx = gx/mag
                        gy = gy/mag
                else:
                    continue
                    
                while(True):
                    curx += gx*prec
                    cury += gy*prec
                    if((int(math.floor(curx)) != curpixx) or (int(math.floor(cury)) != curpixy)):
                        curpixx = int(math.floor(curx))
                        curpixy = int(math.floor(cury))

                        # check if pixel is outside boundary of image
                        
                        if(curpixx <= 0 or curpixx >= len(edge) or curpixy <= 0 or curpixy >= len(edge[0])):
                            break
                        ray.append(curpixx)
                        ray.append(curpixy)
                        q = (curpixx, curpixy)
                        k += 1
                        points.append(q)
                        
                        if(edge[curpixx][curpixy] > 0):
                            
                            gxt = float(gradx[curpixx][curpixy])
                            gyt = float(grady[curpixx][curpixy])
                            
                            if(gxt != 0 and gyt != 0):
                                mag = float((gxt**2 + gyt**2)**0.5)
                                if(dark_on_light):
                                    gxt = -gxt/mag
                                    gyt = -gyt/mag
                                else:
                                    gxt = gxt/mag
                                    gyt = gyt/mag
                            else:
                                continue
                            if(math.acos(gx * (gxt) + gy * (gyt)) < np.pi/2.0):
                                length = float((float(q[0] - p[0])**2 + float(q[1] - p[1])**2)**0.5)
                                for m in points:
                                    if(stroke[m[0]][m[1]]<0):
                                        stroke[m[0]][m[1]] = length
                                    else:
                                        stroke[m[0]][m[1]] = min(length, stroke[m[0]][m[1]])

                        #cv2.line(stroke, p, q,60,2)
                        #ray.append(points)
                        break
    #print ray   
    return stroke
        
text(cv2.imread("036.jpg"))
