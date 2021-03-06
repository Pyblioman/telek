# -*- coding: utf-8 -*

import os
import sys
import string
import urllib
import urllib2
import urlparse

try:
    import xbmcgui
    import xbmcplugin
except:
    print "kann xbmc-module nicht laden"
import socket
import codi
##################
_id='plugin.video.telek'
programpath=os.path.dirname( os.path.realpath( __file__ ) )
ImgPath = programpath + "/resources/media/logos"
PlayListsPath = programpath + "/resources/media/playlists"

class Main:
    def __init__(self):
        self.pDialog = None
        self.run()

        try:
            os.stat(PlayListsPath + "/")
        except:
            os.mkdir(PlayListsPath + "/")
        try:
            os.stat(PlayListsPath + "/тема")
        except:
            os.mkdir(PlayListsPath + "/тема")

        def dateiname(pfad):
            for item in pfad.split("/"): 
                datei=item
            return datei

        def read_url(textdatei):
            print textdatei
            aList=[]
            bList=[]
            try:
                with open(textdatei) as f:
                    for line in f:
                        bList.append(line)
                    bList=bList[1:]
                    for line in bList:
                        if line[:len(line)-1]!="" and line[:1]!="#" and line[:1]!="\r":
                            if line[len(line)-2:]=="\r\n":
                                aList.append(line[:len(line)-2])
                            elif line[len(line)-1:]=="\r" or line[len(line)-1:]=="\n":
                                aList.append(line[:len(line)-1])
                            else:
                                aList.append(line)
                f.close()
            except:
                print textdatei, "- not found!"
            return aList
            
        def download(url1, pfad, i):
            try:
                filein = urllib2.urlopen(url1)
                fileout = open(pfad + "tmp.txt", "wb")
                kb_geladen=0
                #print str(i) + ". " + url1 + " -> " + pfad + dateiname(url1)
                while True:
                        try:
                            kb_geladen=kb_geladen+0.128
                            bytes = filein.read(128000)
                            fileout.write(bytes)
                            print "ca. " + str(kb_geladen) + " MB heruntergeladen"
                        except IOError, (errno, strerror):
                            print ("I/O error(%s): %s" % (errno, strerror))
                            sys.exit(2)
                                                 
                        if bytes == "":
                            break
                fileout.close()
                filein.close()
                txt=open(pfad + "tmp.txt",'r')
                zeile = txt.readline()
                fileout = open(pfad + dateiname(url1), "wb")
                while zeile:
                    fileout.write(zeile)
                    zeile = txt.readline()
                txt.close()
                fileout.close()

            except urllib2.URLError, msg:
                print ("Urllib2 error (%s)" % msg)
                return False
            except socket.error, (errno, strerror):
                print ("Socket error (%s) for host %s (%s)" % (errno, strerror))
                return False


        def nachThemen():
            for item in os.listdir(PlayListsPath + "/тема"):
                os.remove(PlayListsPath + "/тема/" + item)
            for list1 in m3us:
                fileout = open(PlayListsPath + "/тема/" + "tmp.txt", "w")
                fileout.write("#EXTM3U" + "\n")
                for kanal in list1[1]:
                    print "Suchen:", kanal
                    for item in os.listdir(PlayListsPath):
                            if len(item[:1])>0 and item[:1]!='.' and item[len(item)-4:].upper()=='.M3U':
                                if os.path.isfile(os.path.join(PlayListsPath, item)):
                                    print "    lesen:", item
                                    txt=open(PlayListsPath + "/" + item,'r')
                                    zeile = txt.readline()
                                    while zeile and zeile.find("=== PEERSTV (OFF) ===")==-1:
                                        #print zeile.upper(), kanal.upper(),zeile[:8]=="#EXTINF:", zeile.upper().find(kanal.upper())>0
                                        if zeile[:8]=="#EXTINF:" and zeile.decode('utf-8').upper().find(kanal.decode('utf-8').upper())>-1 and zeile.find("PremiumSlyNet")==-1 and zeile.find("===")==-1:
                                            #print zeile.decode('utf-8').upper(), kanal.decode('utf-8').upper()
                                            fileout.write(zeile.split(",")[0] + "," + item + " - " + zeile.split(",")[1])
                                            fileout.write(txt.readline())
                                        zeile = txt.readline()
                                    txt.close()

                fileout.close()

                fileout = open(PlayListsPath + "/тема/" + list1[0] + ".m3u", "w")
                txt = open(PlayListsPath + "/тема/" + "tmp.txt", "r")
                zeile = txt.readline()
                links=[]
                fileout.write(zeile)
                while zeile:
                    if zeile[:8]=="#EXTINF:":
                        zeile1=zeile
                        zeile2 = txt.readline()
                        if (zeile2 in links)==False:
                            links.append(zeile2)
                            fileout.write(zeile1)
                            fileout.write(zeile2)
                    zeile = txt.readline()
                txt.close()
                fileout.close()
        nachThemen()

        def herunterladen():
            j=0
            try:
                download("https://raw.githubusercontent.com/Pyblioman/telek/master/spiski.txt", programpath + "/resources/media/spiski/", j)
                for item in os.listdir(PlayListsPath):
                    if len(item[:1])>0 and item[:1]!='.' and item[len(item)-4:].upper()=='.M3U':
                        if os.path.isfile(os.path.join(PlayListsPath, item)):
                            if os.path.splitext(item)[1][1:].strip().lower() in "m3u":
                                os.remove(PlayListsPath + "/" +item)
                txt=open(programpath + "/resources/media/spiski/spiski.txt",'r')
                zeile = txt.readline()
                fileout = open(programpath + "/resources/media/spiski/spiski.m3u", "w")
                fileout.write("#EXTM3U,"+ zeile)
                zeile = txt.readline()
                i=0
                while zeile:
                    i=i+1
                    fileout.write("#EXTINF:0," + "Liste " + str(i) + "\n")
                    fileout.write(codi.kodi2Aus(zeile) + "\n")
                    zeile = txt.readline()
                txt.close()
                fileout.close()
            except:
                print "download spiski.txt nicht erfolgreich" 

            for jedeurl in read_url(programpath + "/resources/media/spiski/spiski.m3u"):
                j+=1
                try:
                    download(jedeurl, PlayListsPath + "/", j)
                except:
                    print "download " + jedeurl + " nicht erfolgreich"
            nachThemen()

        #--------------------------------------------------- 
        base_url = sys.argv[0]
        addon_handle = int(sys.argv[1])
        args = urlparse.parse_qs(sys.argv[2][1:])
         
        xbmcplugin.setContent(addon_handle, 'movies')
         
        def build_url(query):
            return base_url + '?' + urllib.urlencode(query)
         
        mode = args.get('mode', None)

        def addListItem(name, url, iconimage):
            liz=xbmcgui.ListItem(name, iconImage=ImgPath+'/'+iconimage, thumbnailImage=ImgPath+'/'+iconimage)
            liz.setInfo("Video", { 'year': 2014, "Genre": name })
            ok=xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=liz)
            return ok

        if mode is None:
            for item in os.listdir(PlayListsPath):
                if len(item[:1])>0 and item[:1]!='.':
                    if os.path.isfile(os.path.join(PlayListsPath, item)):
                        if os.path.splitext(item)[1][1:].strip().lower() in "m3u":
                            url = build_url({'mode': 'folder', 'foldername': item})
                            li = xbmcgui.ListItem(item, iconImage='icon.png')
                            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                            listitem=li, isFolder=True)
            for item in os.listdir(PlayListsPath + "/тема"):
                if len(item[:1])>0 and item[:1]!='.':
                    if os.path.isfile(os.path.join(PlayListsPath + "/тема", item)):
                        if os.path.splitext(item)[1][1:].strip().lower() in "m3u":
                            url = build_url({'mode': 'folder', 'foldername': "тема/" + item})
                            li = xbmcgui.ListItem("тема/" + item, iconImage='icon.png')
                            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                            listitem=li, isFolder=True)
         
            url = build_url({'mode': 'folder', 'foldername': 'Обновить'})
            li = xbmcgui.ListItem('Обновить списки каналов...', iconImage='icon.png')
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
            xbmcplugin.endOfDirectory(addon_handle)
         
        elif mode[0] == 'folder':
            if args['foldername'][0]=="Обновить": 
                herunterladen()
            elif args['foldername'][0][:5]=="тема/": 
                foldername = PlayListsPath + args['foldername'][1]
                print "lesen: " + foldername
                txt=open(foldername,'r')
                zeile = txt.readline()
                while zeile:
                    if zeile[:10]=="#EXTINF:0,":
                        title=zeile[10:]
                        zeile = txt.readline()
                        if zeile[:1]!="#":
                            url=zeile
                            addListItem(title, url[:-1], 'icon.png')
                    if zeile[:11]=="#EXTINF:-1,":
                        title=zeile[11:]
                        zeile = txt.readline()
                        if zeile[:1]!="#" and title[0:1]!="=":
                            url=zeile
                            addListItem(title, url[:-1], 'icon.png')
                    zeile = txt.readline()
                txt.close()
            
                xbmcplugin.endOfDirectory(addon_handle)
            else:
                foldername = PlayListsPath + '/' + args['foldername'][0]
                print "lesen: " + foldername
                txt=open(foldername,'r')
                zeile = txt.readline()
                while zeile:
                    if zeile[:10]=="#EXTINF:0,":
                        title=zeile[10:]
                        zeile = txt.readline()
                        if zeile[:1]!="#":
                            url=zeile
                            addListItem(title, url[:-1], 'icon.png')
                    if zeile[:11]=="#EXTINF:-1,":
                        title=zeile[11:]
                        zeile = txt.readline()
                        if zeile[:1]!="#":
                            url=zeile
                            addListItem(title, url[:-1], 'icon.png')
                    zeile = txt.readline()
                txt.close()
           
                xbmcplugin.endOfDirectory(addon_handle)
        
