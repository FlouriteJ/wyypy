# -*- coding:utf-8 -*-
#!/usr/bin/env python

import sys, os, time, jieba
import lucene, chardet
import re

from java.io import File
from org.apache.lucene.analysis.core import WhitespaceAnalyzer
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
# ATTENTION: 下一个是临时添加
from org.apache.lucene.queryparser.classic import MultiFieldQueryParser
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.util import Version
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.search import BooleanQuery
from org.apache.lucene.search import BooleanClause
# 以下是为了显示上下文并且高亮而import的 - Highlighter
from org.apache.lucene.analysis import TokenStream
from org.apache.lucene.index import Term
from org.apache.lucene import search
from org.apache.lucene.search import TermQuery
from org.apache.lucene.search.highlight import Highlighter
from org.apache.lucene.search.highlight import QueryScorer
from org.apache.lucene.search.highlight import SimpleHTMLFormatter
from org.apache.lucene.search.highlight import SimpleSpanFragmenter 

# 以下是为了实现网页接口 import 的库
import web
from web import form

print 'lucene', lucene.VERSION
vm_env = lucene.initVM(vmargs=['-Djava.awt.headless=true']) 

STORE_DIR_PLAYLIST = "Playlist"
dir_playlist = SimpleFSDirectory(File(STORE_DIR_PLAYLIST))              
searcher_playlist = IndexSearcher(DirectoryReader.open(dir_playlist))

STORE_DIR_SONGS = "Songs"
dir_songs = SimpleFSDirectory(File(STORE_DIR_SONGS))              
searcher_songs = IndexSearcher(DirectoryReader.open(dir_songs))

analyzer = WhitespaceAnalyzer(Version.LUCENE_CURRENT)
analyzer = LimitTokenCountAnalyzer(analyzer, 1048576)

print "初始化完成."