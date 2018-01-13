import urllib2
import urlparse
import urllib
import os, sys
import threading

'''

this program is to download the image from Netease music website
'''

def dl(dir,ID,url):
    filename = ID
    path = dir + '/' + filename + ".jpg"
    try:
        data = urllib.urlopen(url).read()
        f = file(path,"wb")
        f.write(data)
        f.close()
    except:
        pass

def run_thread(dir,playlistImage):
    for line in playlistImage.readlines():
        ID,url = line.split(',')
        ID = ID.split('=')[1]
        lock.acquire()
        try:
            dl(dir,ID,url)
        finally:
            lock.release()

f = open("playlist_img_url2","r")
dir = "/media/hduser/TOSHIBA EXT/NeteaseImage2"
try:
    if not os.path.exists(dir):
        os.mkdir(dir)
except:
    pass
lock = threading.Lock()
t = threading.Thread(target = run_thread, args = (dir,f))
t.start()
t.join()
f.close()