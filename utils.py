import cv2
import numpy as np
import math

def drawAngle(elbow,shoulder,image,hand,transp):
    angle_mask = np.zeros_like(image)

    Xe,Ye = elbow
    Xs,Ys = shoulder

    radius = int(((Xs-Xe)**2 + (Ys-Ye)**2)**0.5)
    slope = (Ye-Ys)/(Xe-Xs)

    if hand == 'left':

        angle = 90 - math.atan(slope) * 180 / math.pi
        angle = 0 if angle>165 and Ye>Ys else angle
        color = getColor(angle)
        cv2.ellipse(angle_mask,
                    shoulder,
                    (radius,radius),
                    90-angle,
                    0,
                    angle,
                    color,
                    -1)

    else:
        angle = math.atan(slope) * 180 / math.pi +  90
        angle = 0 if angle>165 and Ye>Ys else angle
        color = getColor(angle)
        cv2.ellipse(angle_mask,
                    shoulder,
                    (radius,radius),
                    90,
                    0,
                    angle,
                    color,
                    -1)
    
    drawTransparent(angle_mask,radius,image,transp,shoulder,hand)
    return angle

def getColor(angle):
    # in a standard BGR representation, we start with a fully red color
    color = [0,0,255]

    factor = int(angle*255/90)
    if factor > 255:
        factor = 255
    
    # this gives value to color green and removes it from red
    color[1] += factor
    color[2] -= factor

    return color

def denormalizePoint(point,height,width):
    x = int(point.x * width)
    y = int(point.y * height)
    return (x,y)
    
def drawTransparent(angle_mask,radius,frame, transp, shoulder, hand='left'):
    # Make the image of protractor fit to size
    transp = cv2.resize(transp,(radius,2*radius))
    height,width = transp.shape[:2]

    # Get an origin point for the protractor img
    if hand == 'left':
        origin_x, origin_y = shoulder[0], int(shoulder[1]-height/2)
    else:
        origin_x, origin_y = shoulder[0]-width, int(shoulder[1]-height/2)


    transp_mask = transp[:,:,3]
    transp = cv2.cvtColor(transp,cv2.COLOR_BGRA2BGR)
    locs = np.where(transp_mask != 0)

    transp_mask = np.zeros_like(angle_mask)
    transp_mask[locs[0]+origin_y, locs[1]+origin_x] = transp[locs[0], locs[1]]

    ultimate_mask = cv2.bitwise_and(angle_mask,transp_mask)
    frame = cv2.addWeighted(frame,1,ultimate_mask,1,1,frame)
