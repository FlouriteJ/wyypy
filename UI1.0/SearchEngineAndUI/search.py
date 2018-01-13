# -*- coding:utf-8 -*-
#!/usr/bin/env python

# SearchFiles.py
# 搜索歌曲和歌单等信息
# 结合网页，与网页模板结合

# 所有需要的python库在SearchInitialize.py 文件里
from SearchInitialize import *
import LSHSearch as lshs
import os

# 歌单搜索
def search_playlist(playname, author, tags, sort_string):
    # 输入内容为空
    if not (playname or author or tags):
        return -1, []

    vm_env.attachCurrentThread()
    resultlist = []

    # playname = ' '.join(pynlpir.segment(playname, pos_tagging=False))
    # author = ' '.join(pynlpir.segment(author, pos_tagging=False))
    # tags = ' '.join(pynlpir.segment(tags, pos_tagging=False))
    try:
        querys = BooleanQuery()
        if playname:
            playname = ' '.join(jieba.cut(playname))
            query_playname = QueryParser(Version.LUCENE_CURRENT, "name", analyzer).parse(playname)
            querys.add(query_playname, BooleanClause.Occur.SHOULD)
        if author:
            author = ' '.join(jieba.cut(author))
            query_author = QueryParser(Version.LUCENE_CURRENT, "author", analyzer).parse(author)
            querys.add(query_author, BooleanClause.Occur.SHOULD)
        if tags:
            tags = ' '.join(jieba.cut(author))
            query_tags = QueryParser(Version.LUCENE_CURRENT, "tags", analyzer).parse(tags)
            querys.add(query_tags, BooleanClause.Occur.SHOULD)
    except Exception, e:
        print "分析关键词逻辑时发生错误"
        return -2, resultlist

    searcher = searcher_playlist
    scoreDocs = searcher.search(querys, 50).scoreDocs
    for scoreDoc in scoreDocs:
        doc = searcher.doc(scoreDoc.doc)
        playID = doc.get("ID")
        playname = doc.get("name") 
        author = doc.get("author")
        playImage = doc.get("image")
        tags = doc.get("tags")
        songIDs = doc.get("songIDs").split('|')

        sharecount = int(doc.get("sharecount"))
        playcount = int(doc.get("playcount"))
        subscribedcount = int(doc.get("subscribedcount"))
        commentcount = int(doc.get("commentcount"))

        playname = ''.join(playname.split())
        author = ''.join(author.split())

        songs=search_song_ID(songIDs)

        playlistDic = {
            "playID" : playID, 
            "playname" : playname,
            "author" : author,
            "playImage" : playImage,
            "tags" : tags,
            "songIDs" : songIDs,
            "songNum" : len(songIDs),
            "songs" :songs,
            "sharecount" : sharecount,
            "playcount" : playcount,
            "subscribedcount" : subscribedcount,
            "commentcount" : commentcount
        }
        resultlist.append(playlistDic)
    orderdic = {"1":"notsort", "2":"commentcount", "3":"sharecount"}
    sort_string = orderdic[sort_string]
    if sort_string == "notsort":
        return len(resultlist), resultlist
    else:
        return len(resultlist), sorted(resultlist, key=lambda obj:obj[sort_string],reverse = True)
    #     return len(resultlist), resultlist
    # query_songname = Quted(resultlist, key=lambda obj:obj[sort_string],reverse = True)

# 歌曲搜索
def search_songs(songname, singer, songAlbum, lyric, comments, sort_string):
    # 搜索内容为空
    if not (songname or singer or songAlbum or lyric or comments):
        return -1, []

    vm_env.attachCurrentThread()
    resultlist = []
    songname = ' '.join(jieba.cut(songname))
    singer = ' '.join(jieba.cut(singer))
    songAlbum = ' '.join(jieba.cut(songAlbum))
    lyric = ' '.join(jieba.cut(lyric))
    comments = ' '.join(jieba.cut(comments))
    try:
        querys = BooleanQuery()
        if songname:
            query_songname = QueryParser(Version.LUCENE_CURRENT, "name", analyzer).parse(songname)
            querys.add(query_songname, BooleanClause.Occur.SHOULD)
        if singer:
            query_singer = QueryParser(Version.LUCENE_CURRENT, "singer", analyzer).parse(singer)
            querys.add(query_singer, BooleanClause.Occur.SHOULD)
        if songAlbum:
            query_songAlbum = QueryParser(Version.LUCENE_CURRENT, "album", analyzer).parse(songAlbum)
            querys.add(query_songAlbum, BooleanClause.Occur.SHOULD)
        if lyric:
            query_lyric = QueryParser(Version.LUCENE_CURRENT, "lyric", analyzer).parse(lyric)
            querys.add(query_lyric, BooleanClause.Occur.SHOULD)
        if comments:
            query_comments = QueryParser(Version.LUCENE_CURRENT, "comments", analyzer).parse(comments)
            querys.add(query_comments, BooleanClause.Occur.SHOULD)
    except Exception, e:
        print "分析关键词逻辑时发生错误"
        return -2, resultlist

    searcher = searcher_songs
    scoreDocs = searcher.search(querys, 50).scoreDocs
    for scoreDoc in scoreDocs:
        doc = searcher.doc(scoreDoc.doc)
        songID = doc.get("ID")
        songname = doc.get("name")
        singer = doc.get("singer")
        songAlbum = doc.get("album")
        songImage = doc.get("image")
        lyric = doc.get("lyric")
        comments = doc.get("comments")
        commentsNum = int(doc.get("commentsNum"))
        likedcount = doc.get("likedcount")
        userID = doc.get("userID")
        usernickname = doc.get("usernickname")
        singerID = doc.get("singerID")
        albumID = doc.get("albumID")

        songname = ''.join(songname.split())
        singer = ''.join(singer.split())
        songAlbum = ''.join(songAlbum.split())
        lyric = ''.join(lyric.split(' '))
        comments = ''.join(comments.split())

        commentsData = []
        for i, j in zip(comments.split("|&&|"),likedcount.split("|&&|")):
            if not i and not j: continue
            commentsData.append(i + " (" + j + ")")
        
        if not commentsData:
            hotcomment="暂无数据！"
        else:
            hotcomment=commentsData[0]
            if len(hotcomment)>70:
                hotcomment=hotcomment[:67]+"... "+hotcomment[hotcomment.find("("):]

        try:
            maxlikedcount = int(likedcount.split("|&&|")[0])
        except:
            maxlikedcount = 0
        
        # 添加到结果字典中
        songsDic = {
            "ID" : songID,  
            "name" : songname, 
            "singer" : singer,
            "album" : songAlbum,
            "image" : songImage,
            "lyric" : lyric.lstrip().replace('\n', '<br/>'),
            "commentsData" : commentsData,
            "hotcomment" : hotcomment,
            "commentsNum" : commentsNum,
            "maxlikedcount" : maxlikedcount
        }
        resultlist.append(songsDic)
    orderdic = {"1":"notsort", "2":"commentsNum", "3":"maxlikedcount"}
    sort_string = orderdic[sort_string]
    if sort_string == "notsort":
        return len(resultlist), resultlist
    else:
        return len(resultlist), sorted(resultlist, key=lambda obj:obj[sort_string],reverse = True)

def search_playlist_ID(playlist_ID):
    vm_env.attachCurrentThread()

    querys = BooleanQuery()
    for id in  playlist_ID:
        #print id
        queryID = TermQuery(Term("ID", id))
        querys.add(queryID, BooleanClause.Occur.SHOULD)
    
    resultlist = []
    searcher = searcher_playlist
    scoreDocs = searcher.search(querys, 500).scoreDocs
    for scoreDoc in scoreDocs:
        doc = searcher.doc(scoreDoc.doc)
        playID = doc.get("ID")
        playname = doc.get("name") 
        author = doc.get("author")
        playImage = doc.get("image")
        tags = doc.get("tags")
        songIDs = doc.get("songIDs").split('|')


        sharecount = int(doc.get("sharecount"))
        playcount = int(doc.get("playcount"))
        subscribedcount = int(doc.get("subscribedcount"))
        commentcount = int(doc.get("commentcount"))

        playname = ''.join(playname.split())
        author = ''.join(author.split())

        songs=search_song_ID(songIDs)

    
        playlistDic = {
            "playID" : playID, 
            "playname" : playname,
            "author" : author,
            "playImage" : playImage,
            "tags" : tags,
            "songIDs" : songIDs,
            "songNum" : len(songIDs),
            "songs" :songs,
            "sharecount" : sharecount,
            "playcount" : playcount,
            "subscribedcount" : subscribedcount,
            "commentcount" : commentcount
        }
        resultlist.append(playlistDic)

    return len(resultlist), resultlist


def search_song_ID(song_ID):
    vm_env.attachCurrentThread()
    querys = BooleanQuery()
    for id in  song_ID:
        queryID = TermQuery(Term("ID", id))
        querys.add(queryID, BooleanClause.Occur.SHOULD)
    
    resultlist = []
    ids = []
    searcher = searcher_songs

    scoreDocs = searcher.search(querys, 500).scoreDocs
    for scoreDoc in scoreDocs:
        doc = searcher.doc(scoreDoc.doc)
        ID = doc.get("ID")
        name = doc.get("name") 
        singer = doc.get("singer")
        name = ''.join(name.split())
        singer = ''.join(singer.split())
        data = u"《" + name + u"》——" + singer
        resultlist.append([ID, data])
        ids.append(ID)
    for id in song_ID:
        if id not in ids:
            resultlist.append([id, "暂无数据"])
    return resultlist

###########website############below  write by dream

urls = (
    '/', 'home',             
    '/song','songRes',
    '/playlist', 'playlistRes',
    '/comment','commentRes',
    '/lyric','lyricRes',
    '/singer','singerRes',
    '/album','albumRes', 
    '/image','imageRes'                  
)
render = web.template.render('templates') # your template



key=""
order="1"
        
    
class home:
    def GET(self):
        return render.home()

class songRes:
    def GET(self):
        global key,order
        user_data = web.input(keyword = "", order="1")
        key=user_data.keyword
        order=user_data.order

        #print user_data.keyword
        #print user_data.keyword02
        ResultNum, ResultData = search_songs(user_data.keyword,"","","","",order)

        print  ResultNum #, ResultData
        return render.songRes(ResultNum, ResultData,key,order)

class playlistRes:
    def GET(self):
        global key,order
        user_data = web.input(keyword="", order="1")
        key=user_data.keyword
        order=user_data.order

        ResultNum, ResultData = search_playlist(user_data.keyword,"","",order)
        return render.playlistRes(ResultNum, ResultData,key,order)

class commentRes:
    def GET(self):
        global key,order
        user_data = web.input(keyword="", order="1")
        key=user_data.keyword
        order=user_data.order   
        ResultNum, ResultData = search_songs("","","","",user_data.keyword,order)
        return render.commentRes(ResultNum, ResultData,key,order)

class lyricRes:
    def GET(self):
        global key,order
        user_data = web.input(keyword="", order="1")

        key=user_data.keyword
        order=user_data.order   
        ResultNum, ResultData = search_songs("","","",user_data.keyword,"",order)
        return render.lyricRes(ResultNum, ResultData,key,order)

class singerRes:
    def GET(self):
        global key,order
        user_data = web.input(keyword="", order="1")
        key=user_data.keyword
        order=user_data.order 

        ResultNum, ResultData = search_songs("",user_data.keyword,"","","",order)
        
        return render.singerRes(ResultNum, ResultData,key,order)

class albumRes:
    def GET(self):
        global key,order
        user_data = web.input(keyword="", order="1")

        key=user_data.keyword
        order=user_data.order   
        ResultNum, ResultData = search_songs("","",user_data.keyword,"","",order)
        return render.albumRes(ResultNum, ResultData,key,order) 

class imageRes:
    def GET(self):
        global key,order
        return render.imageRes(0,[],key,order,"")

    def POST(self):
        global key,order
        user_data=web.input(pic={})
        #print web.data()
        #print user_data
        #print user_data.pic.file.read()

        #文件总数据
        pic=user_data.pic
        #print pic
        if( pic.filename !=""):
            picpath=''
            filedir = './user_data' # change this to the directory you want to store the file in.
            if "pic" in user_data: # to check if the file-object is created
                filepath=pic.filename.replace('\\','/') # replaces the windows-style slashes with linux ones.
                filename=filepath.split('/')[-1] # splits the and chooses the last part (the filename with extension)
                fout = open(filedir +'/'+ filename,'w') # creates the file where the uploaded file should be stored
                picpath=filedir +'/'+ filename
                fout.write(pic.file.read()) # writes the uploaded file to the newly created file.
                fout.close() # closes the file, upload complete.
            #文件临时保存路径
            print picpath
            id=lshs.lshTOfind(picpath)
            if not id:
                return render.imageRes(0,[],key,order,pic.filename)

            print id

            #print search_playlist_ID(id)
            ResultNum,ResultData=search_playlist_ID(id)
            
            os.remove(picpath)

            return render.imageRes(ResultNum,ResultData,key,order,pic.filename)
            


        return render.imageRes(-1,[],key,order,pic.filename)





if __name__ == '__main__':
    app = web.application(urls, globals())
    app.run()
    del searcher_playlist
    del searcher_songs

'''



#搜索程序位置
            playlistDic = {
            "playID" : "76750608", 
            "playname" : "MG动画选用",
            "author" : "温不少",
            "playImage" :"http://p4.music.126.net/QxG-hc2O0Bt1gaVr9ZVM0g==/7707576511668054.jpg",
            "tags" : "运动 清新 放松",
            "songIDs" : [],
            "songNum" :0,
            "sharecount" : 212,
            "playcount" : 150144,
            "subscribedcount" : 10964,
            "commentcount" : 123
            }
            ResultData=[playlistDic,]
            #删除临时文件
'''