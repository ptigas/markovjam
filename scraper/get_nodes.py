import urllib2
import re
import redis

pages = range(0, 240)

redis = redis.StrictRedis(host='localhost', port=6379, db=0)

def fetch_page( url ) :
	response = urllib2.urlopen( url )
	data = response.read()
	return data

node_re = re.compile( r"\/node\/(\d+)" )

def get_nodes( page ) :
	global node_re
	url = "http://www.wikifonia.org/sheet?page=%d" % page
	return node_re.findall( fetch_page(url) )

def enque_node( node ) :
	global redis
	redis.sadd( 'nodes', node )

for page in pages :
	print 'parsing page', page
	nodelist = get_nodes( page )
	for node in nodelist :
		enque_node( node )