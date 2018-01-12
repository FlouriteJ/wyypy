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

def getComment2(idSong):
	global lock,fileComment,threads,hashCommentvisited,success,fail
	url = "http://music.163.com/weapi/v1/resource/comments/R_SO_4_"+ idSong +"/?csrf_token=" 
	params = b'O5/yxckUkfK03FP34r7bgJVnmX5k2/G/l+JCIrgOQwyl+J53UnkgD1kh9z4b6IVTfsjcxGSpGImwZD9kofBZOZTdVyWchjIZes8sb6tnAWuqdC4/j7mOH13VQxx3TDUy'
	encSecKey = '257348aecb5e556c066de214e531faadd1c55d814f9be95fd06d6bff9f4c7a41f831f6394d5a3fd2e3881736d94a02ca919d952872e7d0a50ebfa1769a7a62d512f5f1ca21aec60bc3819a9c3ffca5eca9a0dba6d6f7249b06f5965ecfff3695b54e1c28f3f624750ed39e7de08fc8493242e26dbc4484a01c76f739e135637c'
	data = { "params": params, "encSecKey": encSecKey }
	try:
		response = requests.post(url, headers=headers, data=data,timeout = 2)
		json_text = response.text 
		json_dict = json.loads(json_text) 
		total = json_dict['total']
		content_list = []
		likedCount_list = []
		userId_list = []
		nickname_list = []
		for item in json_dict['hotComments']: 
			content_list.append(re.sub('\n','|&|',item['content']))
			likedCount_list.append(str(item['likedCount']))
			userId_list.append(str(item['user']['userId']))
			nickname_list.append(item['user']['nickname'])
			
		t ='|&&&|'.join([idSong,str(total),'|&&|'.join(content_list),'|&&|'.join(likedCount_list),'|&&|'.join(userId_list),'|&&|'.join(nickname_list)])
		if lock.acquire():
			success+=1
			fileComment.write(t.encode('utf-8'))
			fileComment.write('\n'.encode('utf-8'))
			threads-=1
			hashCommentvisited[idSong] = True
			lock.release()
	except:
		if lock.acquire():
			fail+=1
			threads-=1
			lock.release()	
	
#Initialization
if os.path.exists('Comment2_visit.db'):
	hashCommentvisited = pickle.load(open('Comment2_visit.db','rb'))
else:
	hashCommentvisited = {}
	
print('visited: ', len(hashCommentvisited))

f = open('song.db','r')
fileComment = open('Comment2_details.db','ab')
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
	if hashCommentvisited.get(id,False)==False:
		if lock.acquire():
			threads+=1
			lock.release()
		time.sleep(0.005 + 0.02 *(1-beta))
		threading.Thread(target=getComment2,args=(id,)).start()
		count+=1
		if count%100==0:
			if time.time()-last < alpha:
				time.sleep(alpha-(time.time()-last))
			try:
				beta = float(success)/(success+fail+1)
				print("threads= ",threads,'\t',len(hashCommentvisited),'\t','time= %.2f'%(time.time()-last),'%.2f%%'%(beta*100))
				success = 0
				fail = 0
			except:
				pass
			last = time.time()
		if count>=3000:
			pickle.dump(hashCommentvisited,open('Comment2_visit.db','wb'))
			print('-'*10+'pickled'+'-'*10)
			count-=3000
while True:
	time.sleep(0.5)
	if lock.acquire():
		if not threads:
			lock.release()
			break
		else:
			lock.release()
f.close()
fileComment.close()