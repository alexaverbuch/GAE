import os

import webapp2
import jinja2
from google.appengine.ext import db

import secutils

template_dir = os.path.join(os.path.dirname('templates/'))
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)

class Art(db.Model):
  title = db.StringProperty(required=True)
  art = db.TextProperty(required=True)
  created = db.DateTimeProperty(auto_now_add=True)

class Handler(webapp2.RequestHandler):
  def write(self, *a, **kw):
    self.response.out.write(*a, **kw)
  def render_str(self, template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)
  def render(self, template, **kw):
    self.write(self.render_str(template, **kw))

class HomeHandler(Handler):
  def get(self):    
    self.render("unit1home.html")      

class Unit1Handler(Handler):
  def get(self):
#    self.write("Hello, Udacity!")
    self.response.headers['Content-Type'] = 'text/plain'
    self.response.out.write("Hello, Udacity!")      

class Unit2Rot13Handler(Handler):
  def render_rot13(self, text=""):
    self.render("unit2rot13.html", text=text)
  def get(self):
    self.render_rot13()
  def post(self):
    text = self.request.get('text')
    text = text.encode("rot13")
    self.render_rot13(text)

class Unit3ChanHandler(Handler):
  def render_chan(self, title="", art="", error=""):
    arts = db.GqlQuery("SELECT * FROM Art ORDER BY created DESC")    
    self.render("unit3chan.html", title=title, art=art,
                error=error, arts=arts)
  def get(self):
    self.render_chan()
  def post(self):
    title = self.request.get("title")
    art = self.request.get("art")            

    if title and art:
      newArt = Art(title=title, art=art)
      newArt.put()
      self.redirect("/unit3/chan")
    else:
      error = "we need both a title and some artwork!"
      self.render_chan(title, art, error)

class Unit4VisitsHandler(Handler):
  def get(self):
    self.response.headers["Content-Type"] = "text/plain"

    visits = 0
    visits_cookie_str = self.request.cookies.get("visits")

    if visits_cookie_str != None:
      visits_val = secutils.extract_secure_val(visits_cookie_str)
      if visits_val:
        visits = int(visits_val)
    
    visits += 1
    new_visits_cookie_str = secutils.make_secure_val(str(visits))
    self.response.headers.add("Set-Cookie", "visits=%s" % new_visits_cookie_str)
        
    if visits > 20:
      self.write("You've been here %s times. WOOHOO!" % visits)
    else:
      self.write("You've been here %s times" % visits)
          
app = webapp2.WSGIApplication([('/', HomeHandler),
                               ('/unit1/hello', Unit1Handler),
                               ('/unit2/rot13', Unit2Rot13Handler),
                               ('/unit3/chan', Unit3ChanHandler),
                               ('/unit4/visits', Unit4VisitsHandler)],
                              debug=True)
