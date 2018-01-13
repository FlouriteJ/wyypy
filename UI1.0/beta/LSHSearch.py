from lshash import LSHash
from ColorDescriptor import ColorDescriptor
import linecache
import csv
import cv2

'''

find the result of an image

'''

def getfeatures(path):
    cd = ColorDescriptor((4,6,3))
    img = cv2.imread(path)
    featuresvector = cd.getHistogram(img)
    featuresvector = [int(i*100000000) for i in featuresvector]
    featuresvector.append(2000)
    return featuresvector

def lshTOfind(path):
    lsh = LSHash(50,361)
    f = open('newindex.csv')
    index = csv.reader(f)
    features = []
    count = 0
    for r in index:
        features = [int(float(i)) for i in r[1:]]
        lsh.index(features)
        count += 1
    try:
        f_v = getfeatures(path)
        ans = lsh.query(f_v)
        if ans != []:
            return searchid(int(ans[0][0][360]/10000))
    except:
        return []

def searchid(n):
    line = linecache.getline('Filename-ID_index',n)
    return line.split('  ')[1]
    
if __name__=="__main__":
    path = "./sample.jpg"
    ans = lshTOfind(path)
    print ans
