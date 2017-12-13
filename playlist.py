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

def getPlaylist2(idPlaylist):
	global lock,filePlaylist,threads
	urlPlaylist = "http://music.163.com/playlist?id="
	r = requests.get(urlPlaylist + idPlaylist,headers = headers)
	text = r.text
	
	patTitle = r'(?:data-res-name=")(.+?)(?:")'
	title = Find(patTitle,text)
	#梦里走了许多路，醒来也要走下去
	title = re.sub(',','，',title)

	patAuthor = r'(?:data-res-author=")(.+?)(?:")'
	author = Find(patAuthor,text)	
	#给我一颗糖好吗
	
	# patDescription = r'(?:<meta name="description" content=")(.*?)(?:" />)'
	# description = Find(patDescription,text)
	# #梦里走了许多路，醒来还是在床上？……
	# description = re.sub('\n','',description)
	
	patImage = r'(?:"images": \[")(.*?)(?:"\])'
	image = Find(patImage,text)
	#http://p1.music.126.net/vIw7wO2mPkJunPOSUODyCg==/109951163081338075.jpg
	
	tags_list = re.findall('(?:<a class="u-tag" .+?<i>)(.+?)(?:</i></a>)',text)
	#['华语', '流行', '校园']
	
	songs_list = re.findall('(?:<li><a href="/song\?id=)(.+?)(?:">)',text)
	#['246316', '394722', '472435973', '27588743', '436355876', '205549', '519250024', '25641032', '186103', '26562231', '406072138', '168091', '29713016', '29583952', '29328047', '27630567', '156016', '340395', '31445772', '5245936', '205978', '400162138', '381825', '518895142', '167975', '426026314', '504215085', '191240', '350815', '139357', '350749', '25657589', '30569534', '443292570', '472462728', '5254338', '484057003', '176675', '472442212', '191278', '29418039', '167880', '25713024', '240175', '350803', '191285', '29418037', '25706282', '5251354', '444548903', '22853023', '28798772', '28029031', '4874158', '27984963', '28160015', '436699254', '422463501', '420125810', '355992']
	
	t = ','.join([idPlaylist,title,author,image,'|'.join(tags_list),'|'.join(songs_list)])
	
	if lock.acquire():
		filePlaylist.write(t.encode('utf-8'))
		filePlaylist.write('\n'.encode('utf-8'))
		threads-=1
		try:
			print("threads= ",threads,'\t',idPlaylist)
		except:
			pass
		lock.release()
	
f = open('playlist','r')
filePlaylist = open('playlist_details','wb')
line = f.readline()
maxThreads = 100
threads = 0
lock = threading.Lock()

while line:
	id = line.strip('\n')
	time.sleep(0.005)
	if lock.acquire():
		if threads<maxThreads:
			threading.Thread(target=getPlaylist2,args=(id,)).start()
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
filePlaylist.close()