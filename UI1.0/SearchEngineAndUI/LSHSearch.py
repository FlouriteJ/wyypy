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
    return featuresvector

def lshTOfind(path):
    lsh = LSHash(10,360)
    f = open('finalindex.csv')
    index = csv.reader(f)
    features = []
    count = 0
    for r in index:
        features = [float(i) for i in r[1:]]
        lsh.index(features[:360],features[360])
        count += 1
    try:
        f_v = getfeatures(path)
        #print f_v
        ans = lsh.query(f_v[:360],15)
        if ans != []:
            res = []
            for i in ans:
                res.append(str(int(i[0][1]/10000)))
            return res
        #searchid(int(ans[0][0][360]/10000))
    except:
        return []

if __name__=="__main__":
       
    path = "195286.jpg"
    ans = lshTOfind(path)
    print ans