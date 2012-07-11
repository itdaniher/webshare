import os
import sys

sys.path.append(os.path.realpath('./webpy'))
sys.path.append(os.path.realpath('./GitPython'))

if __name__ != "__main__":
	abspath = os.path.dirname(__file__)
	sys.path.append(abspath)
	os.chdir(abspath)

from PythonMarkdown import markdown
import web
import git

import cgi
import mimetypes
import pprint
import codecs

from random import choice
from string import letters

try:
    import re2 as re
except ImportError:
    import re
else:
    re.set_fallback_notification(re.FALLBACK_WARNING)

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
	def __init__(self):
		roots2paths = lambda roots=['.']: [os.path.join(dirname, filename) for root in roots 
			for dirname, dirnames, filenames in os.walk(root) for filename in filenames]
		self.filePaths = roots2paths(['mkd', pBinDir])
	def GET(self, name):
		if name == "":
			name = "mkd/README.mkd"
		else:
			if name not in self.filePaths:
				results = [item for item in self.filePaths if re.search(name, item)]
				if bool(results):
					name = choice(results)
					web.header("Content-Type", "Content-Type: text/html; charset=UTF-8")
					return "<html><head><meta http-equiv=\"REFRESH\" content=\"1;url=/" + name + "\"></head></html>"
				else:
					web.header("Content-Type", "Content-Type: text/plain; charset=UTF-8")
					return "404" 
		mimeType = mimetypes.guess_type(name)[0]
		if mimeType == "None":
			mimeType = "text/plain; charset=UTF-8"
		if name.split('.')[-1] != "mkd":
			web.header("Content-Type", mimeType)
			return open(name).read()
		else:
			web.header("Content-Type", "Content-Type: text/html; charset=UTF-8")
			string = codecs.open(name, mode="r", encoding="utf8").read()
			return """<p><link href="/static/markdown.css" rel="stylesheet"></p>
"""+markdown.markdown(string)

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
		web.header("Content-Type", "Content-Type: text/plain; charset=UTF-8")
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
