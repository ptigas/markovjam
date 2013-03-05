'''
Python script to scrape http://www.lotro-abc.com/songlist.html

Panagiotis Tigas <ptigas@gmail.com> - 2013
'''

import urllib2
import re
import zlib

req = urllib2.Request('http://www.lotro-abc.com/songlist.html')
response = urllib2.urlopen(req)
page = response.read()

e_pattern = '<tr>[^<]*<td>([^<]+)</td>[^<]*<td>([^<]+)</td>[^<]*<td><a href="([^"]+)">([^<]+)</a></td>[^<]*<td>([^<]+)</td>[^<]*<td>([^<]+)</td>[^<]*</tr>'
pattern = re.compile(e_pattern)

def get_file( filename ) :
	try :
		req = urllib2.Request('http://www.lotro-abc.com/abc/%s'%filename)
		response = urllib2.urlopen(req)
		data = response.read()
		if '.zip' in filename :
			data = zlib.decompress(data)
			filename.replace('.zip', '.abc')			
		with open('data/'+filename, 'wb') as f :
			f.write(data)
	except urllib2.HTTPError:
		print '%s not found' % filename
		return False
	except zlib.error:
		print '%s cannot decompress' % filename
		return False
	return True

match = pattern.finditer(page)

db = open('database.tsv', 'w')

for m in match:
	data = m.groups()
	title = data[0]
	artist = data[1]
	filename = data[3]

	genre = data[5]

	if get_file(filename) :
		print >>db, '\t'.join([artist, title, 'data/'+filename, genre])

db.close()
