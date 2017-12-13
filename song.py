import requests
import re
from bs4 import BeautifulSoup
import json
import time
import threading

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
	global fileSong,lock,threads
	urlSong = 'http://music.163.com/song?id='
	r = requests.get(urlSong + idSong,headers = headers)
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
		try:
			print("threads= ",threads,'\t',idSong)
		except:
			pass
		lock.release()
	
f = open('song','r')
fileSong = open('song_details','wb')
line = f.readline()
maxThreads = 100
threads = 0
lock = threading.Lock()

while line:
	id = line.strip('\n')
	time.sleep(0.005)
	if lock.acquire():
		if threads<maxThreads:
			threading.Thread(target=getSong2,args=(id,)).start()
			threads+=1
		lock.release()
	line = f.readline()
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