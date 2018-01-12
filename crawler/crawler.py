import os
import requests
import re
import time
import threading
import random
import pickle
import json

from pynm import *
	
def refresh():
	fileList = ['song','url','playlist','visit']
	for file in fileList:
		if os.path.exists(file):
			os.remove(file)
		
def getLinks(text):
	global maxUrl,urlSet
	if len(urlSet)>maxUrl:
		alpha = 0
	else:
		alpha = 1.0 - (float(len(urlSet))/maxUrl)**2
	Random = random.random()
	if Random > alpha:
		return
	urlset = set()
	for x in detectPlaylist(text):
		urlset.add('http://music.163.com/playlist?id=' + x)
	for x in detectSong(text):
		urlset.add('http://music.163.com/song?id=' + x)
	for x in detectUser(text):
		urlset.add('http://music.163.com/user/home?id=' + x)
		#TODO: fans & followings
	for x in detectAbum(text):
		urlset.add('http://music.163.com/album?id=' + x)		
	return list(urlset)	
	
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
	
def deal(curPage):
	global lock,Page,urlSet,hashPlaylist,hashSong,threads,songs,error503,success,fail
	try:
		r = requests.get(curPage,headers = headers,timeout=1)
	except Exception as e:
		if lock.acquire():
			threads-=1
			fail+=1
			lock.release()			
		return
	text = r.text
	if Find('(503 Service)( Temporarily Unavailable)',text):
		error503 = True
	dpl = detectPlaylist(text)
	ds = detectSong(text)
	links = getLinks(text)
	if lock.acquire():
		for x in dpl:
			if(hashPlaylist.get(x,False)==False):
				hashPlaylist[x] = True
				filePlaylist.write(x+'\n')
		
		for x in ds:
			if(hashSong.get(x,False)==False):
				hashSong[x] = True
				fileSong.write(x+'\n')
				songs+=1
		if links:
			union_bfs(urlSet,links)
		Page+=1
		threads-=1
		success+=1
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

# Initialization
# refresh()
Page = 0
maxThreads = 500
hashVisited = {}
hashPlaylist = {}
hashSong = {}
threads = 0
lock = threading.Lock()
songs = 0
maxUrl = 200000
printTime = 0
timeLast = time.time()
success = 0
fail = 0

if os.path.exists('playlist.db'):
	filePlaylist = open("playlist.db",'r')
	for line in filePlaylist:
		hashPlaylist[line.strip('\n')] = True
	filePlaylist.close()

if os.path.exists('song.db'):
	fileSong = open("song.db",'r')
	for line in fileSong:
		hashSong[line.strip('\n')] = True	
	fileSong.close()
	
if os.path.exists('url.db'):
	urlSet = pickle.load(open('url.db','rb'))
else:
	urlSet = ["http://music.163.com/discover/playlist"]

if os.path.exists('visit.db'):
	hashVisited = pickle.load(open('visit.db','rb'))
	
print('playlist: ', len(hashPlaylist))
print('song: ', len(hashSong))
print('url: ', len(urlSet))
print('visited: ', len(hashVisited))
filePlaylist = open("playlist.db",'a')
fileSong = open("song.db",'a')

error503 = False
while (getUrlset() or getThreads()):
	if error503:
		print(503)
		time.sleep(30)
		error503 = False
		break
	time.sleep(0.001)
	if lock.acquire():
		if threads<maxThreads and urlSet:
			curPage = urlSet.pop()
			flag = True
			if hashVisited.get(curPage,False)==True:
				while hashVisited.get(curPage,False)==True:
					if not urlSet:
						flag = False
						break
					curPage = urlSet.pop()
			if not flag:
				lock.release()
				time.sleep(0.01)
				continue
			hashVisited[curPage]=True
			threads+=1
			if printTime %100 == 0:
				# if time.time() - timeLast<1:
					# time.sleep(1.0-(time.time() - timeLast))
				try:

					print("Urls: ",len(urlSet),"\t","Threads: ",threads,"\t","Pages: ",Page,'\t','Time: %.2f'%(time.time() - timeLast),'\t','Songs: ',songs,'\t','quality: %.2f'%(float(success)*100/(success+fail+1)))
					timeLast = time.time()
					success = 0
					fail = 0
				except:
					pass
			if printTime %10000 == 0:
				printTime-=10000
				pickle.dump(urlSet,open('url.db','wb'))
				pickle.dump(hashVisited,open('visit.db','wb'))
				print('-'*10+'pickled'+'-'*10)
			printTime+=1	
		
			threading.Thread(target=deal,args=(curPage,)).start()
		lock.release()
		
		
while True:
	time.sleep(0.5)
	if lock.acquire():	
		print("Urls: ",len(urlSet),"\t","Threads: ",threads,"\t","Pages: ",Page,'\t','Time: %.2f'%(time.time() - timeLast),'\t','Songs: ',songs)
		if not threads:
			lock.release()
			break
		else:
			lock.release()
			
filePlaylist.close()
fileSong.close()