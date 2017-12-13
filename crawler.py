import sys,io

import requests
import re
import time
import threading

headers = {
"Host":"music.163.com",
"Referer":"http://music.163.com/",
"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36"}


def getLinks(text): #From Index&Search
	urlset = set()
	for x in detectPlaylist(text):
		urlset.add('http://music.163.com/playlist?id=' + x)
	for x in detectSong(text):
		urlset.add('http://music.163.com/song?id=' + x)
	for x in detectUser(text):
		urlset.add('http://music.163.com/user/home?id=' + x)
		#TODO: fans & followings
	# for x in detectAbum(text):
		# urlset.add('http://music.163.com/album?id=' + x)		
	return list(urlset)
	
def detectPlaylist(text):
	playList = re.findall(r"(?:/playlist\?id=)(\d+)",text)
	# print("playList Len= ",end = '')
	# print(len(playList))
	return playList

def detectSong(text):
	songList = re.findall(r"(?:/song\?id=)(\d+)",text)
	# print("songList Len= ",end = '')
	# print(len(songList))
	return songList
	
def detectUser(text):
	userList = re.findall(r"(?:/user/home\?id=)(\d+)",text)
	# print("userList Len= ",end = '')
	# print(len(userList))
	return userList

def detectAbum(text):
	albumList = re.findall(r"(?:/album\?id=)(\d+)",text)
	# print("albumList Len= ",end = '')
	# print(len(albumList))
	return albumList
	
def union_bfs(a,b):
	# l = []
	# for e in b:
		# if e not in a and e not in l:
			# l.append(e)
	# a.reverse()
	# a.extend(l)
	# a.reverse()
	
	a.reverse()
	a.extend(b)
	a.reverse()
	
filePlaylist = open("playlist",'a')
fileSong = open("song",'a')

maxPage = 30000000
maxThreads = 500
urlSet = ["http://music.163.com/discover/playlist"]
hashVisited = {}
hashPlaylist = {}
hashSonglist = {}
threads = 0
lock = threading.Lock()

def deal(curPage):
	global lock,maxPage,urlSet,hashPlaylist,hashSonglist,threads
	try:
		r = requests.get(curPage,headers = headers,timeout=1)
	except:
		if lock.acquire():
			threads-=1
			lock.release()			
		return
	text = r.text
	dpl = detectPlaylist(text)
	ds = detectSong(text)
	if len(urlSet)<2000000:
		links = getLinks(text)
	else:
		links = []
	if lock.acquire():
		for x in dpl:
			if(hashPlaylist.get(x,False)==False):
				hashPlaylist[x] = True
				filePlaylist.write(x+'\n')
		
		for x in ds:
			if(hashSonglist.get(x,False)==False):
				hashSonglist[x] = True
				fileSong.write(x+'\n')
		# print("linksNum: ",end = '')
		# print(len(links))
		if links:
			union_bfs(urlSet,links)
		maxPage-=1
		threads-=1
		lock.release()

def getThreads():
	global lock,threads
	if lock.acquire():
		x = threads
		lock.release()
	return x
	
def getUrlset():
	global lock,urlSet
	if lock.acquire():
		x = len(urlSet)
		lock.release()
	return x	

while maxPage>0 and (getUrlset() or getThreads()):
	time.sleep(0.001)
	if lock.acquire():
		if threads<maxThreads and urlSet:
			curPage = urlSet.pop()
			if hashVisited.get(curPage,False)==True:
				curPage = urlSet.pop()
				while hashVisited.get(curPage,False)==True:
					curPage = urlSet.pop()
			hashVisited[curPage]=True
			threads+=1
			try:
				print("curUrls: ",len(urlSet),"\t","curThreads: ",threads,"\t","curPages: ",maxPage)
			except:
				pass
			threading.Thread(target=deal,args=(curPage,)).start()
		lock.release()
		
		
while True:
	time.sleep(0.5)
	if lock.acquire():	
		print("Url: ",len(urlSet),"\t","Threads: ",threads,"\t","Pages: ",maxPage)
		if not threads:
			lock.release()
			break
		else:
			lock.release()
			
filePlaylist.close()
fileSong.close()