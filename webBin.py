import os
import sys

abspath = os.path.dirname(__file__)
sys.path.append(abspath)
os.chdir(abspath)

import web

import cgi
from random import choice
from string import letters
import mimetypes
import re
from tools import markdown
import codecs

shortURLs = {
        'ece': 'http://bit.ly/ece_stockroom'}

fileDict = {
	'' : './README.mkd',
	'favicon.ico' : './static/favicon.ico'}

regexURLs = "/(%s)" % '|'.join(shortURLs.keys())
regexFiles = "/(%s)" % '|'.join(fileDict.keys())

urls = (
		regexFiles, 'files',
		'/p', 'pBin',
		'/upload', 'upload',
		regexURLs, 'url',
		'/whoami', 'whoami')

app = web.application(urls, globals(), autoreload=False)
application = app.wsgifunc()
web.config.debug = False

pBinDir = "data"

class whoami:
        def GET(self):
                ua = web.ctx.env['HTTP_USER_AGENT']

class files:
	def GET(self, name):
		if name in fileDict.keys():
			file = fileDict[name]
			mimeType = mimetypes.guess_type(file)[0]
			if mimeType == "None":
				mimeType = "text/plain; charset=UTF-8"
			if file.split('.')[-1] != "mkd":
				web.header("Content-Type", mimeType)
				return open(file).read()
			else:
				web.header("Content-Type", "Content-Type: text/html; charset=UTF-8")
				input_file = codecs.open(file, mode="r", encoding="utf8")
				return markdown.markdown(input_file.read())
class url:
	def GET(self, name):
		if name in shortURLs.keys():
			return web.seeother(shortURLs[name])
		else:
			return "404 Not Found"

class pBin:
	def __init__(self):
		self.taken = os.listdir(pBinDir)
		self.taken.append("")
	def POST(self):
		input = dict(web.input())
		content = input["content"]
		filename = ""
		if filename in self.taken:
			filename = ''.join([choice(letters) for n in xrange(4)])
		self.taken.append(filename)
		f = open(pBinDir + "/" + filename, "w")
		f.write(content.encode('utf-8'))
		f.close()
		return "http://" + web.ctx.host + "/p?" + filename + "\n"
	def GET(self):
		input = list(web.input())
		try:
			input = input[0].split('/')[-1]
		except:
			input = input
		web.header("Content-Type", "text/plain; charset=UTF-8")
		if len(input) == 0:
			return os.listdir(pBinDir)
		else:
			return open(pBinDir + "/" + input).read()

class upload:
	def __init__(self):
		cgi.maxlen = 100 * 1024 * 1024
	def GET(self):
		web.header("Content-Type", "Content-Type: text/html; charset=UTF-8")
		return open("upload.html").read()
	def POST(self):
		try:
			upload = web.input(upfile={})
			upfile = upload['upfile']
			open("static/" + upfile.filename.split('/')[-1], 'wb').write(upfile.value)
			raise web.seeother('/upload')
		except ValueError:
			return "too big!"

if __name__ == "__main__":
	app.run()
