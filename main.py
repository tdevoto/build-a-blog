import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))


class Blogpost(db.Model):

	title = db.StringProperty(required = True)
	entry = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)

class Newpost(Handler):

	def get(self):
		self.render("newpost.html")

	def render_newposts(self, title="", entry="", error=""):
		self.render("newpost.html", title=title, entry=entry, error=error)

	def post(self):
		title = self.request.get("title")
		entry = self.request.get("entry")

		if title and entry:
			a = Blogpost(title=title, entry=entry)
			a.put()
			newpostkey = Blogpost.key(a).id()
			self.redirect("/blog/" + str(newpostkey))
		else:
			error = "we need both title and a new entry"
			self.render_newposts(title, entry, error)


class Blogpage(Handler):

	def render_blogs(self, title="", entry="", error=""):
		blogposts = db.GqlQuery("select * from Blogpost order by created desc limit 5")
		self.render("blogs.html", title=title, entry=entry, error=error, blogposts=blogposts)

	def get(self):
		self.render_blogs()

class ViewPostHandler(Handler):

	def get(self, id):
		singlepost = Blogpost.get_by_id(int(id), parent=None)
		postid = Blogpost.key(singlepost).id()

		if singlepost:
			self.render("singlepost.html", singlepost=singlepost, postid=postid)
		else:
			self.response.write("There is no post with that ID")



app = webapp2.WSGIApplication([
	('/', Blogpage),
	('/newpost', Newpost),
	('/blog', Blogpage),
	webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
