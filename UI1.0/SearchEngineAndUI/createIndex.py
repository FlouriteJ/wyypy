import glob
from ColorDescriptor import ColorDescriptor
import argparse
import cv2

'''

this program is to create the index file for an image dataset

'''
ap = argparse.ArgumentParser()
ap.add_argument("-d","--dataset",required = True)
ap.add_argument("-i","--index",required = True)
args = vars(ap.parse_args())
cd = ColorDescriptor((4,6,3))

output = open(args["index"],"w")
count = 0
for imgpath in glob.glob(args["dataset"]+"/*.jpg"):
    try:
        imgid = imgpath[imgpath.rfind("/")+1:]
        img = cv2.imread(imgpath)
        mark = float(imgid.split('.')[0])
        features = cd.getHistogram(img)
        features.append(mark/10000)
        features = [str(f*100000000) for f in features]
        output.write("%s,%s\n" % (imgid, ",".join(features)))
    except:
        pass
output.close()