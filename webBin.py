import os

if __name__ != "__main__":
	import sys
	abspath = os.path.dirname(__file__)
	sys.path.append(abspath)
	os.chdir(abspath)

from PythonMarkdown import markdown
import webpy as web

import cgi
import mimetypes
import re
import codecs

from random import choice
from string import letters

urls = (
		'/g', 'update',
		'/p', 'pBin',
		'/upload', 'upload',
		'/(.*|'')', 'files')

app = web.application(urls, globals(), autoreload=False)
application = app.wsgifunc()
web.config.debug = False 

pBinDir = "data"

class files:
	def GET(self, name):
		if name == "":
			name = "README.mkd"
		mimeType = mimetypes.guess_type(name)[0]
		if mimeType == "None":
			mimeType = "text/plain; charset=UTF-8"
		try:
			if name.split('.')[-1] != "mkd":
				web.header("Content-Type", mimeType)
				return open("static/"+name).read()
			else:
				web.header("Content-Type", "Content-Type: text/html; charset=UTF-8")
			try:
				string = codecs.open("mkd/"+name, mode="r", encoding="utf8").read()
			except:
				string = codecs.open("static/"+name, mode="r", encoding="utf8").read()
			return """<p><link href="/markdown.css" rel="stylesheet"></p>
"""+markdown.markdown(string)
		except IOError:
			return "404"

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

class update:
	def __init__(self):
		import GitPython as git
		self.last = ''
		self.repos = []
		self.repos.append(git.Repo("./"))
		for repo in self.repos[0].submodules:
			self.repos.append(git.Repo(repo.path))
	def POST(self):
		self.last = web.input()
		for repo in self.repos:
			repo.remote().pull('master')
		print "repo and all submodules updated to remote's master"
	def GET(self):
		return self.last

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
