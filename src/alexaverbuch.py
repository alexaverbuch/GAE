import re
import os

import webapp2
import jinja2
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname('templates/'))
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)

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
    self.render("home.html")      

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
    
username_re = re.compile('^[a-zA-Z0-9_-]{3,20}$')
password_re = re.compile('^.{3,20}$')
email_re = re.compile('^[\S]+@[\S]+\.[\S]+$')

class Unit2SignupHandler(Handler):
  def render_signup(self, username="", username_error="",
                 password_error="", verify_error="", email="",
                 email_error=""):
    self.render("unit2signup.html", username=username,
                username_error=username_error, password_error=password_error,
                verify_error=verify_error, email=email, email_error=email_error)
  def get(self):
    self.render_signup()
  def post(self):
    user_username = self.request.get('username')
    user_password = self.request.get('password')
    user_verify = self.request.get('verify')
    user_email = self.request.get('email')
    username_error = "" if username_re.match(user_username) else "That's not a valid username."
    password_error = "" if password_re.match(user_password) else "That wasn't a valid password."
    verify_error = "" if (user_password == user_verify or (not password_error == "")) else "Your passwords didn't match."
    email_error = "" if (user_email == "" or email_re.match(user_email)) else "That's not a valid email."
#    if ((username_error == "") and (password_error == "") and (verify_error == "") and (email_error == "")):
    if (not username_error) and (not password_error) and (not verify_error) and (not email_error):
      self.redirect("/unit2/welcome?username=%s" % user_username)
    else:
      self.render_signup(user_username, username_error, password_error,
                         verify_error, user_email, email_error)

class Unit2WelcomeHandler(Handler):
  def render_welcome(self, username=""):
    self.render("unit2welcome.html", username=username)
  def get(self):
    username = self.request.get("username")
    self.render_welcome(username)

class Art(db.Model):
  title = db.StringProperty(required=True)
  art = db.TextProperty(required=True)
  created = db.DateTimeProperty(auto_now_add=True)

class Unit3ChanHandler(Handler):
  def render_chan(self, title="", art="", error=""):
    arts = db.GqlQuery("SELECT * FROM Art ORDER BY created DESC")
    self.render("unit3chan.html", title=title, art=art, error=error, arts=arts)
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
      self.render_chan("unit3chan.html", title, art, error)
      
app = webapp2.WSGIApplication([('/', HomeHandler),
                               ('/unit1/hello', Unit1Handler),
                               ('/unit2/rot13', Unit2Rot13Handler),
                               ('/unit2/signup', Unit2SignupHandler),
                               ('/unit2/welcome', Unit2WelcomeHandler),
                               ('/unit3/chan', Unit3ChanHandler)],
                              debug=True)
