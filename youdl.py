import subprocess
import urllib2
import httplib
import json
from optparse import OptionParser
from sets import Set

"""
A useful wrapper around youtube-dl to download youtube videos in different ways

Option 1:
	Specify a url as
		you-dl -v http://www.youtube.com/watch?v=x3cte6Pm-1M
		
	Specify a list fo files
		you-dl -l name_of_file
		
	Specify a management prefix for a list of files
		you-dl -m management
		
	Specify a management prefix for a list of files
		you-dl -q query -limit n
"""

def parseOptions():
	global options
	parser = OptionParser()
	parser.add_option("-s", "--scriptLocation", dest="scriptLocation",
					  help="location of python script", metavar="PATH")
	parser.add_option("-v", "--video", dest="videoUrl",
					  help="Url of Video", metavar="URL")
	parser.add_option("-l", "--listFile", dest="listFile",
					  help="file with list of urls", metavar="FILE")
	parser.add_option("-m", "--managePrefix", dest="managePrefix",
					  help="file with list of urls", metavar="FILE")
	parser.add_option("-q", "--query", dest="query",
					  help="Get Urls matching query", metavar="Query")
	parser.add_option("-l", "--limit", dest="limit",
					  help="max number of videos to download", metavar="Integer")

	(options, args) = parser.parse_args()

class YouTubeDownLoader:
	commandPrefix = "scriptLocation\youtube-dl.py  "
	outputTemplate = "%(stitle)s.FORMAT.%(ext)s"
	formats =    [   37,    46,   22,   45,   44,  18]
	formatDesc = ["10m", "10w", "7m", "7w", "4w", "3m"]
	def __init__(self, scriptLocation):
		self.scriptLocation = scriptLocation
		self.commandPrefix = self.commandPrefix.replace("scriptLocation", self.scriptLocation)

	def processUrl(self, url):
		print "Getting url:%(u)s\n" %{"u":url}
		success = False
		index=-1
		for cFormat in self.formats:
			index = index + 1
			print "Trying format", cFormat, " ..."
			result=subprocess.call(["python", self.commandPrefix, "-o", self.outputTemplate.replace("FORMAT", self.formatDesc[index]), "--format", format(cFormat), url])
			print "result=", result
			if(result == 0):
				print   " success\n"
				success=True
				break
			else:
				print " failure\n"

		if(not success):
			command= self.commandPrefix + " -o outputTemplate" + " " + url 
			command
			print "Trying default ..."
			result=subprocess.call(command)
			if(result == 0):
				print   " success\n"
				success=True
			else:
				print   " failure\n"

		return success
				
	def processFile(self, listFile):
		f = open(listFile, "r")
		urls = f.readlines();
		for url in urls:
			self.processUrl(url)


#download the file:
#close file because we dont need it anymore:
	def processQuery(self, query, filePrefix, options):
		limit = 50
		start = 1
		if hasattr(options, "limit"):
				limit = options.limit
		
		if(limit > 50):
			limit = 50
		
		url = "http://gdata.youtube.com/feeds/api/videos?q=%(q)s&orderby=published&start-index=1&max-results=%(l)s&v=2&prettyprint=true&hd=true&alt=json" %{"l":limit, "q":query}
		
		file = urllib2.urlopen(url)
		data = file.read()
#		print data
		file.close()
		
		jObj = json.loads(data)
		entries = jObj['feed']['entry']
		candidateFile = filePrefix + "_c.txt"
		for entry in entries:
			url = entry['media$group']['media$player']['url']
			index = url.find("&")
			if(index != -1):
				url = url[:index]
			c_f = open(candidateFile, "a")
			c_f.write(url + "\n")
			c_f.close()
		
		self.processManagedFiles(filePrefix)
			
		
		
			
	def processManagedFiles(self, filePrefix):
		"""Files looked will be filePrefix_c, filePrefix_i, filePrefix_d.txt"""
		candidateFile = filePrefix + "_c.txt"
		ignoreFile = filePrefix + "_i.txt"
		doneFile = filePrefix + "_d.txt"

		c_f = open(candidateFile, "r")
		candidates = c_f.readlines()
		for index, c in enumerate(candidates):
			candidates[index] = c.strip()
		candidates = Set(candidates)
		c_f.close()
			
		d_f = open(doneFile, "r")
		done = d_f.readlines()
		for index, c in enumerate(done):
			done[index] = c.strip()
		done = Set(done)
		d_f.close()
		
		i_f = open(ignoreFile, "r")
		ignore = i_f.readlines()
		for index, c in enumerate(ignore):
			ignore[index] = c.strip()
		ignore = Set(ignore)
		i_f.close()
		
		todo = candidates - (done | ignore)
		
		print 'Candidates: %(c)s\nTodo: %(t)s\n' %{"c":len(candidates), "t":len(todo)}
		for url in todo:
			success = self.processUrl(url)
			if(success):
				d_f = open(doneFile, "a");
				d_f.write(url + "\n")
				d_f.close()
	
def main():	
	global options
	parseOptions()
	yt = YouTubeDownLoader(options.scriptLocation)
	if(options.query != None):
		if(options.managePrefix == None):
			print "Need manage prefix"
			return(-1)
		else:
			yt.processQuery(options.query, options.managePrefix, options)
	elif(options.listFile != None):
		yt.processFile(options.listFile)
	elif(options.videoUrl != None):
		yt.processUrl(options.videoUrl)
	elif(options.managePrefix != None):
		yt.processManagedFiles(options.managePrefix)

	
main()
