import numpy as np
import cv2
import csv
import re

'''

this program is to calculate the feature vector of a picture,
how to use:
cd = ColorDescriptor((4,6,3))
features = cd.getHistogram

'''
class ColorDescriptor:
    def __init__(self,bins):
        self.bins = bins

    def histagram(self,img,mask):
        hist = cv2.calcHist([img],[0,1,2],mask,self.bins,[0,180,0,256,0,256])
        hist = cv2.normalize(hist).flatten()
        return hist
    
    #divide a picture into 5 parts
    def getHistogram(self,img):
        image = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
        features = []
        (h,w) = img.shape[:2]
        (cx,cy) = (int(w/2),int(h/2))
        
        #devide pic into 4 parts
        segments = [(0,cx,0,cy),(cx,w,0,cy),(cx,w,cy,h),(0,cx,cy,h)]

        #constructs a ellipcal mask on behalf of the central part of picture
        (ex,ey) = (int(w*0.75)/2,int(h*0.75)/2)
        ellipmask = np.zeros(img.shape[:2],dtype = "uint8")
        cv2.ellipse(ellipmask,(cx,cy),(ex,ey),0,0,360,255,-1)

        #get histagram from these parts
        for (lx,rx,ly,ry) in segments:
            cornermask = np.zeros(img.shape[:2], dtype = "uint8")
            cv2.rectangle(cornermask,(lx,ly),(rx,ry),255,-1)
            cornermask = cv2.subtract(cornermask,ellipmask)

            hist = self.histagram(img,cornermask)
            features.extend(hist)

        hist = self.histagram(img,ellipmask)
        features.extend(hist)

        return features

