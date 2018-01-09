f = open("song_details2.db")
f2 = open("albumPic.db",'w')
d = {}
for line in f:
        l = line.split(',')
        album = l[-1]
        song = l[0]
        if(d.get(album,False)==False):
                d[album]=True
                f2.write(album.strip('\n'))
                f2.write(',')
                f2.write(l[4])
                f2.write('\n')
print("finished")
f.close()
f2.close()

f = open("song_details2.db")
f2 = open("album",'w')
d = {}
for line in f:
        l = line.split(',')
        album = l[-1]
        song = l[0]
        if(d.get(album,False)==False):
                d[album]=True
                f2.write(album)
print("finished")