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

def getAlbum2(idAlbum = "37115236"):
	global fileAlbum,lock,threads,fail,success,hashAlbumvisited
	try:
		urlAlbum = 'http://music.163.com/album?id='
		r = requests.get(urlAlbum + idAlbum,headers = headers)
		text = r.text
		date = Find(r'(?:"pubDate": ")(.+)(?:T)',text)
		description = Find(r'(?:"description": ")(.+)(?:")',text)
		# description = re.sub('\n',"|&|",description)

		t = ','.join([idAlbum,date,description])
		
		if lock.acquire():
			fileAlbum.write(t.encode('utf-8'))
			fileAlbum.write('|newline|'.encode('utf-8'))
			threads-=1
			hashAlbumvisited[idAlbum] = True
			success+=1
			lock.release()
	except:
		if lock.acquire():
			threads-=1
			fail+=1
			lock.release()

#Initialization
if os.path.exists('album_visit2.db'):
	hashAlbumvisited = pickle.load(open('album_visit2.db','rb'))
else:
	hashAlbumvisited = {}

print('visited: ', len(hashAlbumvisited))

f = open('album.db','r')
fileAlbum = open('album_details2.db','ab')
maxThreads = 500
threads = 0
lock = threading.Lock()
count = 1
last = time.time()
alpha = 1.5
beta = 1
success = 0
fail = 0
for line in f:
	id = line.strip('\n')
	while threads>=maxThreads:
		time.sleep(0.01)
	if hashAlbumvisited.get(id,False)==False:
		if lock.acquire():
			threads+=1
			lock.release()
		time.sleep(0.005 + 0.05*(1-beta))
		threading.Thread(target=getAlbum2,args=(id,)).start()
		count+=1
		if count%100==0:
			if time.time()-last < alpha:
				time.sleep(alpha-(time.time()-last))
			try:
				beta = float(success)/(success+fail+1)
				print("threads= ",threads,'\t',len(hashAlbumvisited),'\t','time= %.2f'%(time.time()-last),'\t%.2f%%'%(beta*100))
				success = 0
				fail = 0
			except:
				pass
			last = time.time()
		if count>=2000:
			pickle.dump(hashAlbumvisited,open('album_visit2.db','wb'))
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
fileAlbum.close()
