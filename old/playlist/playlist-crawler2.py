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
	global lock,filePlaylist,threads,hashPlaylistvisited,success,fail
	try:
		urlPlaylist = "http://music.163.com/api/playlist/detail?id=%s&upd"%(idPlaylist)
		r = requests.get(urlPlaylist,headers = headers,timeout = 2)
		text = r.text
		json_dict = json.loads(text) 	
		title = json_dict['result']['name']
		author = json_dict['result']['creator']['nickname']
		tags_list = json_dict['result']['tags']
		description = json_dict['result']['description']
		image = json_dict['result']['coverImgUrl']
		songs_list = []
		tracks = json_dict['result']['tracks']
		for track in tracks:
			songs_list.append(str(track['id']))

		shareCount = str(json_dict['result']['shareCount'])
		playCount = str(json_dict['result']['playCount'])
		subscribedCount = str(json_dict['result']['subscribedCount'])
		commentCount = str(json_dict['result']['commentCount'])
			
		t = ','.join([idPlaylist,title,author,image,'|'.join(tags_list),'|'.join(songs_list),shareCount,playCount,subscribedCount,commentCount])
		
		if lock.acquire():
			if len(songs_list)>=1:
				filePlaylist.write(t.encode('utf-8'))
				filePlaylist.write('\n'.encode('utf-8'))
				hashPlaylistvisited[idPlaylist] = True
				success+=1
			else:
				fail+=1
			threads-=1
			lock.release()
	except:
		if lock.acquire():
			threads-=1
			fail+=1
			lock.release()
	
#Initialization
if os.path.exists('playlist_visit2.db'):
	hashPlaylistvisited = pickle.load(open('playlist_visit2.db','rb'))
else:
	hashPlaylistvisited = {}
	
print('visited: ', len(hashPlaylistvisited))

f = open('playlist.db','r')
filePlaylist = open('playlist_details2.db','ab')
maxThreads = 500
threads = 0
lock = threading.Lock()
count = 1
last = time.time()
alpha = 1
success = 0
fail = 0
beta = 1
for line in f:
	id = line.strip('\n')
	while threads>=maxThreads:
		time.sleep(0.01)
	if hashPlaylistvisited.get(id,False)==False:
		if lock.acquire():
			threads+=1
			lock.release()
		time.sleep(0.007 + 0.03*(1-beta))
		threading.Thread(target=getPlaylist2,args=(id,)).start()
		count+=1
		if count%100==0:
			if time.time()-last < alpha:
				time.sleep(alpha-(time.time()-last))
			try:
				beta = float(success)/(success+fail+1)
				print("threads= ",threads,'\t',len(hashPlaylistvisited),'\t','time= %.2f'%(time.time()-last),'%.2f%%'%(beta*100))
			except:
				pass
			last = time.time()
		if count>=5000:
			pickle.dump(hashPlaylistvisited,open('playlist_visit2.db','wb'))
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