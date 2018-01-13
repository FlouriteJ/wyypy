# -*- coding:utf-8 -*-
#!/usr/bin/env python

# IndexFiles.py
# 对所有的搜索内容建立索引

import lucene, threading, time, sys
import re, chardet, os, string
import pynlpir, jieba

from java.io import File
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.core import WhitespaceAnalyzer

from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexWriterConfig
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version

class Ticker(object):
    
    def __init__(self):
        self.tick = True

    def run(self):
        while self.tick:
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(1.0)

class IndexFiles(object):
    def __init__(self, storeDir, analyzer, function):
    
        if not os.path.exists(storeDir):
            os.mkdir(storeDir)

        store = SimpleFSDirectory(File(storeDir))
        analyzer = LimitTokenCountAnalyzer(analyzer, 1048576)
        config = IndexWriterConfig(Version.LUCENE_CURRENT, analyzer)
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
        writer = IndexWriter(store, config)
        eval("self." + function + "(writer)")
        ticker = Ticker()
        print 'commit index',
        threading.Thread(target=ticker.run).start()
        writer.commit()
        writer.close()
        ticker.tick = False
        print '索引建立完成.'

    # 添加歌单索引
    def indexDocs_playlist(self, writer):
        
        t1 = FieldType()
        t1.setIndexed(False)
        t1.setStored(True)
        t1.setTokenized(False)

        t2 = FieldType()
        t2.setIndexed(True)
        t2.setStored(True)
        t2.setTokenized(True)
        t2.setIndexOptions(FieldInfo.IndexOptions.DOCS_AND_FREQS)
        
        # playlist
        success = 0
        fail = 0
        noinfo = 0

        playlists = open('data/playlist_details2.db', "r")
        for line in playlists.readlines():
            if len(line) < 20:
                noinfo += 1
                continue

            information =  line.split(',')
            try:
                playID = information[0]
                playname = ' '.join(information[1:-8])
                author, playImage, tags, songIDs, sharecount, playcount, subscribedcount, commentcount = information[-8:]
            except Exception, e:
                fail += 1
                print "fail"
                continue
 
            playname = ' '.join(jieba.cut(playname))
            author = ' '.join(jieba.cut(author))
            tags = ' '.join(jieba.cut(tags))
            # playname = ' '.join(pynlpir.segment(playname, pos_tagging=False))
            # author = ' '.join(pynlpir.segment(author, pos_tagging=False))
            tags = tags.replace("|", " ")

            doc = Document()
            doc.add(Field("ID", playID, t2))
            doc.add(Field("name", playname, t2))
            doc.add(Field("author", author, t2))
            doc.add(Field("image", playImage, t1))
            doc.add(Field("tags", tags, t2))
            doc.add(Field("songIDs", songIDs, t1))
            doc.add(Field("sharecount", sharecount, t1))
            doc.add(Field("playcount", playcount, t1))
            doc.add(Field("subscribedcount", subscribedcount, t1))
            doc.add(Field("commentcount", commentcount, t1))
            writer.addDocument(doc)
            print "歌单", playname, "成功添加"
            success += 1
        playlists.close()

        print "===== 添加歌单索引完毕 ====="
        print "成功添加:", success
        print "添加失败:", fail
        print "没有歌单信息:", noinfo

    # 添加歌曲索引
    def indexDocs_songs(self, writer):
        
        #　歌曲评论
        commentFile = open('data/Comment2_details.db', "r")
        ID_to_position = {}
        commentsdata = []
        count = 0
        for line in commentFile.readlines():

            if len(line) < 30:
                continue

            try:
                information = line.split('|&&&|')
            except Exception, e:
                continue
            commentsdata.append(information)
            ID_to_position[information[0]] = count
            count += 1
        commentFile.close()

        t1 = FieldType()
        t1.setIndexed(False)
        t1.setStored(True)
        t1.setTokenized(False)

        t2 = FieldType()
        t2.setIndexed(True)
        t2.setStored(True)
        t2.setTokenized(True)

        # songs
        success = 0
        fail = 0
        noinfo = 0
        nolyric = 0
        nocomment = 0

        songs = open('data/song_details2.db', "r")
        for line in songs.readlines():

            if len(line) < 20:
                noinfo+= 1
                continue

            information =  line.split(',')
            try:
                songID, songname, singer, songAlbum, songImage, singerID, albumID = information
            except Exception, e:
                fail += 1
                continue

            songname = ' '.join(jieba.cut(songname))
            singer = ' '.join(jieba.cut(singer))
            songAlbum = ' '.join(jieba.cut(songAlbum))
            # songname = ' '.join(pynlpir.segment(songname, pos_tagging=False))
            # singer = ' '.join(pynlpir.segment(singer, pos_tagging=False))
            # songAlbum = ' '.join(pynlpir.segment(songAlbum, pos_tagging=False))
            
            # 添加歌词
            filename = "data/data_lyric/" + songID + ".db"
            try:
                lyric_file = open(filename)
                lyric = lyric_file.read()
                lyric = lyric.replace("\\n", '\n')
                r = re.compile(r"\[.*?\]")
                lyric = r.sub(' ', lyric)
                lyric = ' '.join(jieba.cut(lyric))
                # lyric = ' '.join(pynlpir.segment(lyric, pos_tagging=False))
            except Exception, e:
                nolyric += 1
                lyric = ""

            # 添加评论
            try:
                information = commentsdata[ID_to_position[songID]]
                commentsNum, comments, likedcount, userID, usernickname = information
                comments = comments.replace('|&|', '\n')
                comments = ' '.join(jieba.cut(comments))
            except Exception, e:
                nocomment += 1
                comments = ''
                likedcount = ''
                userID = ''
                usernickname = ''
                commentsNum = "0"
        
            doc = Document()
            doc.add(Field("ID", songID, t2))
            doc.add(Field("name", songname, t2))
            doc.add(Field("singer", singer, t2))
            doc.add(Field("album", songAlbum, t2))
            doc.add(Field("image", songImage, t1))
            doc.add(Field("lyric", lyric, t2))
            doc.add(Field("commentsNum", commentsNum, t1))
            doc.add(Field("comments", comments, t2))
            doc.add(Field("likedcount", likedcount, t1))
            doc.add(Field("userID", userID, t1))
            doc.add(Field("usernickname", usernickname, t1))
            doc.add(Field("singerID", singerID, t1))
            doc.add(Field("albumID", albumID, t1))
            writer.addDocument(doc)
            print "歌曲", songname, "成功添加"
            success += 1

        print "===== 建立歌曲索引完毕 ====="
        print "成功添加索引:", success
        print "添加失败:", fail
        print "没有歌曲信息:", noinfo
        print "没有歌词:", nolyric
        print "没有歌曲评论:", nocomment
        songs.close()
        
if __name__ == '__main__':
    start = time.time()
    pynlpir.open()
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    analyzer = WhitespaceAnalyzer(Version.LUCENE_CURRENT)

    # 建立索引的位置
    playlistDirectory = "Playlist"
    songDirectory = "Songs"

    # 建立歌单索引
    IndexFiles(playlistDirectory, analyzer, "indexDocs_playlist")
    # message = raw_input("输入以继续")
    # # 建立歌曲索引
    IndexFiles(songDirectory, analyzer, "indexDocs_songs")
    end = time.time()

    print "用时:", end - start, "s"