# import sys,io
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='gb18030')
import requests
import re

headers = {
"Host":"music.163.com",
"Referer":"http://music.163.com/",
"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36"}

def Find(pat,text):
	match = re.search(pat,text,flags=re.DOTALL)
	if match == None:
		return ''
	return match.group(1)

def gethttpLinks(content, page = 'http://music.163.com/'):
    reg = r'(?:a href=\")(.+?)(?:\")'
    ulrre = re.compile(reg)
    ulrlist = re.findall(ulrre,content)
    urlset = set()
    for s in ulrlist:
        if s!='':
            if len(s)>=4 and s[:4]== "http":
                urlset.add(s)
            else:
                urlset.add(urlparse.urljoin(page,s))
    return list(urlset)

# playlist
def getPlaylist(idPlaylist = "2010827278"): 
	"""title,author,tags_list,description,image,songs_list"""
	
	urlPlaylist = "http://music.163.com/playlist?id="
	r = requests.get(urlPlaylist + idPlaylist,headers = headers)
	text = r.text
	
	patTitle = r'(?:data-res-name=")(.+?)(?:")'
	title = Find(patTitle,text)
	#梦里走了许多路，醒来也要走下去

	patAuthor = r'(?:data-res-author=")(.+?)(?:")'
	author = Find(patAuthor,text)	
	#给我一颗糖好吗
	
	# patKeywords =  r'(?:<meta name="keywords" content=")(.+?)(?:" />)'
	# keywords = Find(patKeywords,text)
	# #梦里走了许多路，醒来也要走下去，给我一颗糖好吗，华语，流行，校园
	
	patDescription = r'(?:<meta name="description" content=")(.*?)(?:" />)'
	description = Find(patDescription,text)
	#梦里走了许多路，醒来还是在床上？……
	
	patImage = r'(?:"images": \[")(.*?)(?:"\])'
	image = Find(patImage,text)
	#http://p1.music.126.net/vIw7wO2mPkJunPOSUODyCg==/109951163081338075.jpg
	
	tags_list = re.findall('(?:<a class="u-tag" .+?<i>)(.+?)(?:</i></a>)',text)
	#['华语', '流行', '校园']
	
	songs_list = re.findall('(?:<li><a href="/song\?id=)(.+?)(?:">)',text)
	#['246316', '394722', '472435973', '27588743', '436355876', '205549', '519250024', '25641032', '186103', '26562231', '406072138', '168091', '29713016', '29583952', '29328047', '27630567', '156016', '340395', '31445772', '5245936', '205978', '400162138', '381825', '518895142', '167975', '426026314', '504215085', '191240', '350815', '139357', '350749', '25657589', '30569534', '443292570', '472462728', '5254338', '484057003', '176675', '472442212', '191278', '29418039', '167880', '25713024', '240175', '350803', '191285', '29418037', '25706282', '5251354', '444548903', '22853023', '28798772', '28029031', '4874158', '27984963', '28160015', '436699254', '422463501', '420125810', '355992']
	
	return title,author,tags_list,description,image,songs_list

def getSong(idSong = "246316"):
	"""title,author,album,image"""
	urlSong = 'http://music.163.com/song?id='
	r = requests.get(urlSong + idSong,headers = headers)
	text = r.text
	
	patTitle = r'(?:data-res-name=")(.+?)(?:")'
	title = Find(patTitle,text)
	#飞

	patAuthor = r'(?:data-res-author=")(.+?)(?:")'
	author = Find(patAuthor,text)	
	#洪辰
	
	patAlbum = r'(?:class="s-fc7">)(.*?)(?:</a></p>)'
	album = Find(patAlbum,text)
	#72小姐
	
	patImage = r'(?:class="j-img" data-src=")(.*?)(?:">)'
	image = Find(patImage,text)
	
	return title,author,album,image

def getLyric(idSong = "246316"):
	urlLyric = 'http://music.163.com/api/song/lyric?os=pc&id=' + idSong + '&lv=-1&kv=-1&tv=-1'
	r = requests.get(urlLyric,headers = headers)
	text = r.text
	
	patLyric = '(?:"lyric":")(.+?)(?:")'
	lyric = Find(patLyric,text)
	lyric = re.sub(r'\[.+?\]','',lyric)
	return lyric
	
def getUser(idUser = "488658914"):
	urlUser = 'http://music.163.com/user/home?id='
	r = requests.get(urlUser + idUser,headers = headers)
	text = r.text
	
	patTitle = r'(?:data-res-name=")(.+?)(?:")'
	title = Find(patTitle,text)
	#TODO:需要检验此函数
	return title
		
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
	
	
if __name__=='__main__':
	pass