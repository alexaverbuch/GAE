import os
import logging
import math
import time

import webapp2
import jinja2
from google.appengine.ext import db

from utils import sec_utils
from utils import form_utils
from utils import json_utils
from utils import memcache_utils

from exercises import exercises
from wiki import wiki 

template_dir = os.path.join(os.path.dirname('templates/'))
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)

class BlogPost(db.Model):
  subject = db.StringProperty(required=True)
  content = db.TextProperty(required=True)
  created = db.DateTimeProperty(auto_now_add=True)
  last_modified = db.DateTimeProperty(auto_now=True)

class User(db.Model):
  username = db.StringProperty(required=True)
  password = db.StringProperty(required=True)
  email = db.EmailProperty(required=False)
  created = db.DateTimeProperty(auto_now_add=True)

class Handler(webapp2.RequestHandler):
  def write(self, *a, **kw):
    self.response.out.write(*a, **kw)
  def render_str(self, template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)
  def render(self, template, **kw):
    self.write(self.render_str(template, **kw))
  def debug(self, msg):
    self.write("%s<br>" % msg)

def get_post(self, key, update=False):
  def fun_miss():
    try:
      post = db.get(key)
    except db.BadKeyError:
      post = None 
    return (time.time(), post)  
#  return memcache_utils.get(key, fun_miss, update)
  return memcache_utils.get_cas(key, fun_miss, update)

def get_top_posts(self, update=False):
  key = 'top_posts'
  def fun_miss():
    posts = db.GqlQuery("SELECT * FROM BlogPost ORDER BY created DESC LIMIT 10")
    return (time.time(), list(posts))  
#  return memcache_utils.get(key, fun_miss, update)
  return memcache_utils.get_cas(key, fun_miss, update)

class BlogHandler(Handler):
  def render_blog(self):
    (time_queried, posts) = get_top_posts(self)
    seconds_since_query = int(math.floor(time.time() - time_queried))
    self.render("blog.html", posts=posts, seconds_since_query=seconds_since_query)
  def get(self):
    self.render_blog()
    
class BlogJSONHandler(Handler):
  def get_posts(self):
    # TODO use get_top_posts()
    posts = db.GqlQuery("SELECT * "
                        "FROM BlogPost "
                        "ORDER BY created DESC "
                        "LIMIT 10")
    # prevent query from being run multiple times        
    return list(posts)
  def get(self):    
    # get blog content
    posts = self.get_posts()    
    # convert blog content to json
    posts_json = json_utils.posts_to_json(posts)
    # send response as json
    self.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
    self.write(posts_json)

class BlogSignupHandler(Handler):
  def new_user(self, user_username, user_password, user_email):
    q = db.GqlQuery("SELECT * FROM User " + 
                    "WHERE username = :1",
                    user_username)
    results = q.fetch(1)
    if results.__len__() > 0:
      # user exists
      return None
    else:
      # create new user
      secure_password = sec_utils.make_pw_hash(user_username, user_password)
      newUser = User(username=user_username, password=secure_password) 
      if user_email:
        newUser.email = user_email
      newUser.put()
      return newUser

  def render_signup(self, username="", username_error="",
                    password_error="", verify_error="", email="",
                    email_error=""):
    self.render("blog_signup.html", username=username,
                username_error=username_error, password_error=password_error,
                verify_error=verify_error, email=email, email_error=email_error)
  def get(self):
    self.render_signup()
  def post(self):
    user_username = self.request.get('username')
    user_password = self.request.get('password')
    user_verify = self.request.get('verify')
    user_email = self.request.get('email')

    username_error = form_utils.check_username(user_username, "That's not a valid username.")    
    password_error = form_utils.check_password(user_password, "That wasn't a valid password.")
    verify_error = "" if ((user_password == user_verify) or (not password_error == "")) else "Your passwords didn't match."
    email_error = form_utils.check_email(user_email, "That's not a valid email.") 
    
    if (not username_error) and (not self.new_user(user_username, user_password, user_email)):
      username_error = "That user already exists."
    
    if (not username_error) and (not password_error) and (not verify_error) and (not email_error):
      secure_username = sec_utils.make_secure_val(str(user_username)) 
      signed_username_cookie = "user_id=%s; Path=/" % secure_username 
      self.response.headers.add("Set-Cookie", str(signed_username_cookie))
      self.redirect("/blog/welcome")
    else:
      self.render_signup(user_username, username_error, password_error,
                         verify_error, user_email, email_error)

class BlogLogoutHandler(Handler):
  def get(self):
    self.response.headers.add("Set-Cookie", "user_id=; Path=/")
    self.redirect("/blog/signup")

class BlogLoginHandler(Handler):
  def valid_user(self, user_username, user_password):
    q = db.GqlQuery("SELECT * FROM User " + 
                    "WHERE username = :1",
                    user_username)        
    results = q.fetch(1)        
    if results.__len__() == 0:
      # no such user
      return None
    else:    
      # user exists
      user = results[0]
      return sec_utils.check_pw_hash(user_username, user_password, user.password)      
  def render_login(self, error=""):
    self.render("blog_login.html", error=error)
  def get(self):
    self.render_login()
  def post(self):
    user_username = self.request.get('username')
    user_password = self.request.get('password')

    # UGLY, FIX SO FORMUTILS EXPOSES NO PUBLIC VARIABLES
    invalid_username_format = not form_utils.username_re.match(user_username)
    invalid_password_format = not form_utils.password_re.match(user_password)
    invalid_user = not self.valid_user(user_username, user_password)

    if invalid_username_format or invalid_password_format or invalid_user:       
      self.render_login(error="Invalid login.")
    else:
      secure_username = sec_utils.make_secure_val(str(user_username))
      signed_username_cookie = "user_id=%s; Path=/" % secure_username
      self.response.headers.add("Set-Cookie", str(signed_username_cookie))
      self.redirect("/blog/welcome")

class BlogWelcomeHandler(Handler):
  def render_welcome(self, username=""):
    self.render("blog_welcome.html", username=username)
  def get(self):
    secure_username = self.request.cookies.get("user_id")
    if secure_username:
      username = sec_utils.extract_secure_val(secure_username)
      self.render_welcome(username)
    else:
      self.redirect("/blog/signup")

class BlogNewPostHandler(Handler):
  def render_newpost(self, subject="", content="", error=""):
    self.render("blog_newpost.html", subject=subject, content=content, error=error)
  def get(self):
    self.render_newpost()
  def post(self):
    subject = self.request.get("subject")
    content = self.request.get("content")            
    if subject and content:
      new_post = BlogPost(subject=subject, content=content)
      new_post.put()
      get_post(self, str(new_post.key()))
      get_top_posts(self, True)
      new_post_id = new_post.key()
      self.redirect("/blog/%s" % new_post_id)
    else:
      error = "subject and content, please!"
      self.render_newpost(subject, content, error)

class BlogPostHandler(Handler):
  def render_post(self, post, seconds_since_query):
    self.render("blog_post.html", post=post, seconds_since_query=seconds_since_query)
  def get(self, post_key):
    (time_queried, post) = get_post(self, post_key)
    if post is None:
      self.redirect("/blog")
    else:
      seconds_since_query = int(math.floor(time.time() - time_queried))
      self.render_post(post, seconds_since_query)
class BlogPostJSONHandler(Handler):
  def get(self, post_key):
    # TODO memcache
    post = db.get(post_key)
    post_json = json_utils.post_to_json(post)
    self.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
    self.write(post_json)

class BlogFlushHandler(Handler):
  def get(self):
    memcache_utils.flush()
    self.redirect("/blog")

app = webapp2.WSGIApplication([# Exercises
                               ('/', exercises.HomeHandler),
                               ('/unit1/hello', exercises.Unit1Handler),
                               ('/unit2/rot13', exercises.Unit2Rot13Handler),
                               ('/unit3/chan', exercises.Unit3ChanHandler),
                               ('/unit4/visits', exercises.Unit4VisitsHandler),
                               # Blog                               
                               ('/blog', BlogHandler),
                               ('/blog/.json', BlogJSONHandler),
                               ('/blog/flush', BlogFlushHandler),
                               ('/blog/signup', BlogSignupHandler),
                               ('/blog/welcome', BlogWelcomeHandler),
                               ('/blog/login', BlogLoginHandler),
                               ('/blog/logout', BlogLogoutHandler),
                               ('/blog/newpost', BlogNewPostHandler),
                               ('/blog/(.*).json', BlogPostJSONHandler),
                               ('/blog/(.*)', BlogPostHandler),
                               # Wiki
                               ('/wiki', wiki.WikiHandler),
                               ('/wiki/signup', wiki.WikiSignupHandler),
                               ('/wiki/welcome', wiki.WikiWelcomeHandler),
                               ('/wiki/login', wiki.WikiLoginHandler),
                               ('/wiki/logout', wiki.WikiLogoutHandler),
                               ('/wiki/_edit(/(?:[a-zA-Z0-9_-]+/?)*)', wiki.WikiEditHandler),
                               ('/wiki/_history(/(?:[a-zA-Z0-9_-]+/?)*)', wiki.WikiHistoryHandler),
                               ('/wiki(/(?:[a-zA-Z0-9_-]+/?)*)', wiki.WikiPageHandler)],
                              debug=True)
