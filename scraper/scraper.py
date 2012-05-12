import socket
import os
import sys
import urllib2
import zipfile
import redis
from BeautifulSoup import BeautifulSoup

redis = redis.StrictRedis(host='localhost', port=6379, db=0)

socket.setdefaulttimeout(10)

def fetch_page( url ) :
	response = urllib2.urlopen( url, timeout = 10 )
	data = response.read()
	return data

def get_infos( node ) :
	url = "http://www.wikifonia.org/node/%d" % node
	data = fetch_page( url )
	soup = BeautifulSoup(data)	

	genres = []
	genres_raw = soup.findAll(id="sheet-genre")
	for genre in genres_raw :
		genres.append( genre.text )


	title = None
	if soup.find(id="sheet-title") :
		title = soup.find(id="sheet-title").text

	composer = None
	if soup.find(id="sheet-composer") :
		composer = soup.find(id="sheet-composer").text
	
	return {
		"id" : node,
		"title" : title,
		"composer" : composer,
		"genres" : ','.join(genres)
	}

def get_musicxml( node ) :
	url = "http://static.wikifonia.org/%d/musicxml.mxl" % node
	request = urllib2.Request( url )
	response = urllib2.urlopen( request, timeout = 10 )

	mxl = open('data/mxl/%d.mxl' % node , 'w')
	mxl.write( response.read() )
	mxl.close()

	musicxml = zipfile.ZipFile('data/mxl/%d.mxl' % node).read("musicXML.xml")

	xml = open('data/%d.xml' % node , 'w')
	xml.write( musicxml )
	xml.close()

def dequeue() :
	global redis
	return redis.spop('nodes')

while True :
	node = dequeue()
	print "Reading node", node
	if node :
		node = int(node)

		if os.path.exists( 'data/%d.txt' % node ) :
			continue

		try :			
			#get_musicxml( node )
			infos = get_infos( node )
		except socket.error :
			errno, errstr = sys.exc_info()[:2]
			if errno == socket.timeout:
				print "There was a timeout"
				redis.sadd('nodes', node)
				continue
		except urllib2.HTTPError :
			print 'Urllib HTTP Error'
			continue

		infos_file = open('data/%d.txt' % node, 'w')		
		s = "%(id)d|%(title)s|%(composer)s|%(genres)s\n" % infos
		infos_file.write( s.encode('ascii', 'ignore') )
		infos_file.close()
	else:
		break