import requests
import re
from bs4 import BeautifulSoup
import json
import time
import threading
import os
import pickle

headers = {
"Host":"music.163.com",
"Referer":"http://music.163.com/",
"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36"}

def Find(pat,text):
	match = re.search(pat,text)
	if match == None:
		return ''
	#print(match.group(1))
	return match.group(1)


def getSong2(idSong = "246316"):
	global fileSong,lock,threads,hashSongvisited
	urlSong = 'http://music.163.com/song?id='
	try:
		r = requests.get(urlSong + idSong,headers = headers,timeout = 1)
	except:
		if lock.acquire():
			threads-=1
			lock.release()
			return
	text = r.text
			
	patTitle = r'(?:data-res-name=")(.+?)(?:")'
	title = Find(patTitle,text)
	#飞

	patAuthor = r'(?:data-res-author=")(.+?)(?:")'
	author = Find(patAuthor,text)	
	#洪辰
	
	patAlbum = r'(?:class="s-fc7">)(.*?)(?:</a>)'
	album = Find(patAlbum,text)
	#72小姐
	
	patImage = r'(?:class="j-img" data-src=")(.*?jpg)(?:">)'
	image = Find(patImage,text)
	#http://p1.music.126.net/Y0MWOGVy-xhVRyhT_LnSVQ==/109951163077105754.jpg
	
	t = ','.join([idSong,title,author,album,image])
	
	if lock.acquire():
		fileSong.write(t.encode('utf-8'))
		fileSong.write('\n'.encode('utf-8'))
		threads-=1
		hashSongvisited[idSong] = True
		lock.release()

#Initialization
if os.path.exists('song_visit.db'):
	hashSongvisited = pickle.load(open('song_visit.db','rb'))
else:
	hashSongvisited = {}
	
print('visited: ', len(hashSongvisited))

f = open('song.db','r')
fileSong = open('song_details.db','ab')
maxThreads = 500
threads = 0
lock = threading.Lock()
count = 1
last = time.time()
alpha = 0.8
for line in f:
	id = line.strip('\n')
	if threads<maxThreads:
		if hashSongvisited.get(id,False)==False:
			if lock.acquire():
				threads+=1
				lock.release()
			time.sleep(0.005)
			threading.Thread(target=getSong2,args=(id,)).start()
			count+=1
			if count%100==0:
				if time.time()-last < alpha:
					time.sleep(alpha-(time.time()-last))
				try:
					print("threads= ",threads,'\t',len(hashSongvisited),'\t','time= %.2f'%(time.time()-last))
				except:
					pass
				last = time.time()
			if count>=2000:
				pickle.dump(hashSongvisited,open('song_visit.db','wb'))
				print('-'*10+'pickled'+'-'*10)
				count-=2000
while True:
	time.sleep(0.5)
	if lock.acquire():
		if not threads:
			lock.release()
			break
		else:
			lock.release()
f.close()
fileSong.close()