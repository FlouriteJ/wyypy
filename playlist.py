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
"User-Agent":"New"}

def Find(pat,text):
	match = re.search(pat,text)
	if match == None:
		return ''
	#print(match.group(1))
	return match.group(1)

def getPlaylist2(idPlaylist):
	global lock,filePlaylist,threads,hashPlaylistvisited
	urlPlaylist = "http://music.163.com/api/playlist/detail?id=%s&upd"%(idPlaylist)
	try:
		r = requests.get(urlPlaylist,headers = headers,timeout=1)
	except:
		if lock.acquire():
			threads-=1
			lock.release()
			return
	text = r.text
	
	text = r.text
	json_dict = json.loads(text) 
	title = json_dict['result']['name']
	#梦里走了许多路，醒来也要走下去
	
	
	author = json_dict['result']['creator']['nickname']
	#给我一颗糖好吗
	
	# patKeywords =  r'(?:<meta name="keywords" content=")(.+?)(?:" />)'
	# keywords = Find(patKeywords,text)
	# #梦里走了许多路，醒来也要走下去，给我一颗糖好吗，华语，流行，校园
	
	tags_list = json_dict['result']['tags']
	#['华语', '流行', '校园']
	
	description = json_dict['result']['description']
	#梦里走了许多路，醒来还是在床上？……
	
	image = json_dict['result']['coverImgUrl']
	#http://p1.music.126.net/vIw7wO2mPkJunPOSUODyCg==/109951163081338075.jpg
	
	
	songs_list = []
	tracks = json_dict['result']['tracks']
	for track in tracks:
		songs_list.append(str(track['id']))
		
	t = ','.join([idPlaylist,title,author,image,'|'.join(tags_list),'|'.join(songs_list)])
	
	if lock.acquire():
		filePlaylist.write(t.encode('utf-8'))
		filePlaylist.write('\n'.encode('utf-8'))
		threads-=1
		hashPlaylistvisited[idPlaylist] = True
		lock.release()
	
#Initialization
if os.path.exists('playlist_visit.db'):
	hashPlaylistvisited = pickle.load(open('playlist_visit.db','rb'))
else:
	hashPlaylistvisited = {}
	
print('visited: ', len(hashPlaylistvisited))

f = open('playlist.db','r')
filePlaylist = open('playlist_details.db','ab')
maxThreads = 500
threads = 0
lock = threading.Lock()
count = 1
last = time.time()
alpha = 0.5
for line in f:
	id = line.strip('\n')
	if threads<maxThreads:
		if hashPlaylistvisited.get(id,False)==False:
			if lock.acquire():
				threads+=1
				lock.release()
			time.sleep(0.003)
			threading.Thread(target=getPlaylist2,args=(id,)).start()
			count+=1
			if count%100==0:
				if time.time()-last < alpha:
					time.sleep(alpha-(time.time()-last))
				try:
					print("threads= ",threads,'\t',len(hashPlaylistvisited),'\t','time= %.2f'%(time.time()-last))
				except:
					pass
				last = time.time()
			if count>=5000:
				pickle.dump(hashPlaylistvisited,open('playlist_visit.db','wb'))
				print('-'*10+'pickled'+'-'*10)
				count-=5000
while True:
	time.sleep(0.5)
	if lock.acquire():
		if not threads:
			lock.release()
			break
		else:
			lock.release()
f.close()
filePlaylist.close()