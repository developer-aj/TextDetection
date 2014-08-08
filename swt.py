import cv2
import cv2.cv as cv
import numpy as np
import math
import cmath

def text(src):
    # gradient
    
    imgray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(imgray, 175, 320)
    imgaussian = cv2.GaussianBlur(imgray, (5, 5), 0)
    imgradx = cv2.Sobel(imgaussian, cv.CV_SCHARR, 1, 0, ksize = 5)
    imgrady = cv2.Sobel(imgaussian, cv.CV_SCHARR, 0, 1, ksize = 5)
    lines = cv2.HoughLines(edges,1,np.pi/180,200)
    imtemp = imgray
    print len(edges[0])
    #print len(imtemp[0])
    for i in range(0, len(imtemp)):
        for j in range(0, len(imtemp[0])):
            imtemp[i][j] = -1
    #swt(edges, imgradx, imgrady, False)
    
    #saving images
    cv2.imwrite("gray.jpg", imgray)
    cv2.imwrite("gradx.jpg", imgradx)
    cv2.imwrite("grady.jpg", imgrady)
    cv2.imwrite("gaussian.jpg", imgaussian)
    cv2.imwrite("canny.jpg", edges)
    #cv2.imwrite("line.jpg", lines)
    cv2.imwrite("swt.jpg", swt(edges, imgradx, imgrady, imtemp, False))

def swt(edge, gradx, grady, imtemp, dark_on_light):
    stroke = imtemp
    prec = 0.05
    for row in range(0, len(edge)):
        #print "row : ",row+1
        for col in range(0, len(edge[0])):
           # print "col : ",col+1
            if(edge[row][col]>0):
                #print "if(edge[row][col]>0) ----->"
                p = (col, row)
                points = [[col, row]]
                curx = float(col) + 0.5
                cury = float(row) + 0.5
                curpixx = col
                curpixy = row
                gx = float(gradx[row][col])
                gy = float(grady[row][col])

                # normalize gradient
                mag = float((gx**2 + gy**2)**0.5)
                #print mag
                #print grady[100]
                if(mag > 0):
                   # print "if(mag > 0)[1] ----->"
                    if(dark_on_light):
                        #print "if(dark_on_light) ---->"
                        gx = -gx/mag
                        gy = -gy/mag
                    else:
                        #print "else(dark_on_light) ----->"
                        gx = gx/mag
                        gy = gy/mag
                else:
                   # print "else(mag > 0)[1] ----->"
                    continue
                while(True):
                    #print "while(True) ---->"
                    curx += gx*prec
                    cury += gy*prec
                    if(int(math.floor(curx)) != curpixx or int(math.floor(cury)) != curpixy):
                       # print "if(int(math.floor(curx)) != curpixx or int(math.floor(cury)) != curpixy) ------>"
                        curpixx = int(math.floor(curx))
                        curpixy = int(math.floor(cury))

                        # check if pixel is outside boundary of image
                        
                        if(curpixx < 0 or curpixx >= len(edge)-1 or curpixy < 0 or curpixy>=len(edge[0])-1):
                          #  print "if(curpixx < 0 or curpixx >= 480 or curpixy < 0 or curpixy>=640) ---->"
                            break
                        q = (curpixx, curpixy)
                        if(edge[curpixx][curpixy] > 0):
                           # print "if(edge[curpixx][curpixy] > 0) ----->"
                            points.append([curpixx, curpixy])
                            gxt = float(gradx[curpixx][curpixy])
                            gyt = float(grady[curpixx][curpixy])
                            mag = float((gxt**2 + gyt**2)**0.5)
                            
                            if(mag > 0):
                               # print mag
                               # print "if(mag > 0)[2] ---->"
                                if(dark_on_light):
                                   # print "if(dark_on_light) ------>"
                                    gxt = -gxt/mag
                                    gyt = -gyt/mag
                                else:
                                  #  print "else(dark_on_light) ----->"
                                    gxt = gxt/mag
                                    gyt = gyt/mag
                               # print gxt, ", ", gyt
                            """else:
                                print "else(mag > 0)[2] ---->"
                                continue"""
                           # print math.acos(gx * ( gxt) + gy * ( gyt))
                            if(math.acos(gx * (-gxt) + gy * (-gyt)) < np.pi/2.0):
                                #print "if(math.acos(gx*gxt + gy*gyt) < math.pi/2.0) ---->"
                                length = (float(q[0] - p[0])**2 + float(q[1] - p[1])**2)**0.5
                               # print length
                                for m in points:
                                    if(stroke[m[0]][m[1]]<0):
                                        stroke[m[0]][m[1]] = length
                                    else:
                                        stroke[m[0]][m[1]] = min(length, stroke[m[0]][m[1]])
                                    # print stroke[m[0]][m[1]]
                        cv2.line(stroke, p, q,60,2)
                        break
    #print stroke[2]
    return stroke
        
text(cv2.imread("036.jpg"))
