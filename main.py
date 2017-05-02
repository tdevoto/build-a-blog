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


class MainHandler(Handler):

	def render_front(self, title="", entry="", error=""):
		blogposts = db.GqlQuery("select * from Blogpost order by created desc")
		self.render("main.html", title=title, entry=entry, error=error, blogposts=blogposts)

	def get(self):
		self.render_front()

	def post(self):
		title = self.request.get("title")
		entry = self.request.get("entry")

		if title and entry:
			a = Blogpost(title=title, entry=entry)
			a.put()

			self.redirect("/")
		else:
			error = "we need both title and a new entry"
			self.render_front(title, entry, error)

app = webapp2.WSGIApplication([
	('/', MainHandler)
], debug=True)
