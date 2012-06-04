import logging
import time

from utils import sec_utils
from utils import form_utils
from utils import json_utils
from utils import memcache_utils
from utils import webapp_utils

from wiki_model import WikiPage
from wiki_model import WikiUser

from google.appengine.ext import db
    
def get_page(title):
    pages = db.GqlQuery("SELECT * FROM WikiPage "
                        "WHERE title = :1 "
                        "ORDER BY version DESC "
                        "LIMIT 1",
                        title)
    pages = list(pages)     
    if pages:
      # page exists
      return pages[0]
    else:
      # page does not exist
      return None

def get_page_version(title, version=None):
    # logging
    logging.error("title = " + str(title))
    logging.error("version = " + str(version))
    
    pages = db.GqlQuery("SELECT * FROM WikiPage "
                        "WHERE title = :1 AND version = :2",
                        title, int(version))
    # logging
    logging.error("pages_query: " + pages.__str__())
    
    pages = list(pages)
        
    # logging
    logging.error("pages: " + str(len(pages)))
     
    if pages:
      # page exists
      return pages[0]
    else:
      # page does not exist
      return None

def get_page_versions(title):
    versions = db.GqlQuery("SELECT * FROM WikiPage "
                           "WHERE title = :1 "
                           "ORDER BY version DESC",
                           title)
    return list(versions)     

class WikiHandler(webapp_utils.Handler):
  def get(self):
    # Logging
    logging.error("WikiHandler.get()")
    
    self.redirect("/wiki/")
    
class WikiPageHandler(webapp_utils.Handler):
  def render_wiki_page(self, title, content, username, version):
    self.render("wiki_page.html", title=title, content=content, username=username, version=version)
  def get(self, title):
    secure_username = self.request.cookies.get("user_id")
    username = None
    if secure_username:
      username = sec_utils.extract_secure_val(secure_username)
    
    version = self.request.get('v')
    
    # Logging
    logging.error("WikiPageHandler.get()")
    logging.error("title=" + str(title))
    logging.error("username=" + str(username))
    logging.error("version=" + str(version))

    page = None
    if version:              
      page = get_page_version(title, version)
    else:
      page = get_page(title)
    
    if page:
      # show latest page
      self.render_wiki_page(page.title, page.content, username, page.version)
    elif username:
      # go to edit page
      self.redirect("/wiki/_edit" + str(title))
    else:
      self.redirect("/wiki/login")      

class WikiEditHandler(webapp_utils.Handler):
  def render_edit_wiki_page(self, title, content, username):
    self.render("wiki_edit.html", title=title, content=content, username=username)
  def get(self, title):    
    version = self.request.get('v')

    secure_username = self.request.cookies.get("user_id")
    username = None
    if secure_username:
      username = sec_utils.extract_secure_val(secure_username)
    
    # Logging
    logging.error("WikiEditHandler.get()")
    logging.error("title=" + str(title))
    logging.error("version=" + str(version))
    logging.error("username=" + str(username))
    
    if not username:                
      self.redirect("/wiki/")
    else:
      page = None
      if version:              
        page = get_page_version(title, version)
      else:
        page = get_page(title)
      if page:
        self.render_edit_wiki_page(page.title, page.content, username)
      else:
        self.render_edit_wiki_page(title, "", username)
  def post(self, title):
    content = self.request.get('content')
    
    # Logging
    logging.error("WikiEditHandler.post()")
    logging.error("title=" + str(title))
    logging.error("content=" + str(content))

    secure_username = self.request.cookies.get("user_id")
    username = None
    if secure_username:
      username = sec_utils.extract_secure_val(secure_username)
      
    if username:    
      page = get_page(title)
      version = 1    
      if page:
        version = page.version + 1      
      newPage = WikiPage(username=username, title=title, content=content, version=version)    
      newPage.put()    
      self.redirect("/wiki" + str(title))
    else:
      self.redirect("/wiki")

class WikiHistoryHandler(webapp_utils.Handler):
  def render_history_wiki_page(self, versions, username):
    self.render("wiki_history.html", versions=versions, username=username)
  def get(self, title):
    # Logging
    logging.error("WikiHistoryHandler.get()")
    logging.error("title=" + str(title))

    secure_username = self.request.cookies.get("user_id")
    username = None
    if secure_username:
      username = sec_utils.extract_secure_val(secure_username)
    
    versions = get_page_versions(title)
    self.render_history_wiki_page(versions, username)
        
class WikiSignupHandler(webapp_utils.Handler):
  def new_user(self, username, password, email):
    q = db.GqlQuery("SELECT * FROM WikiUser " + 
                    "WHERE username = :1",
                    username)
    results = q.fetch(1)
    if results:
      # user exists
      return None
    else:
      # create new user
      secure_password = sec_utils.make_pw_hash(username, password)
      newUser = WikiUser(username=username, password=secure_password) 
      if email:
        newUser.email = email
      newUser.put()
      return newUser
  def render_signup(self, username="", username_error="",
                    password_error="", verify_error="", email="",
                    email_error=""):
    self.render("wiki_signup.html", username=username,
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
      self.redirect("/wiki")
    else:
      self.render_signup(user_username, username_error, password_error,
                         verify_error, user_email, email_error)

class WikiLogoutHandler(webapp_utils.Handler):
  def get(self):
    # Logging
    logging.error("WikiLogoutHandler.get()")

    title = self.request.get('title')
    if not title:
      title = ""    
    self.response.headers.add("Set-Cookie", "user_id=; Path=/")
    self.redirect("/wiki" + str(title))

class WikiLoginHandler(webapp_utils.Handler):
  def valid_user(self, user_username, user_password):
    q = db.GqlQuery("SELECT * FROM WikiUser " + 
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
    self.render("wiki_login.html", error=error)
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
      self.redirect("/wiki")

class WikiWelcomeHandler(webapp_utils.Handler):
  def render_welcome(self, username=""):
    self.render("wiki_welcome.html", username=username)
  def get(self):
    secure_username = self.request.cookies.get("user_id")
    username = None
    if secure_username:
      username = sec_utils.extract_secure_val(secure_username)
    if username:                
      self.render_welcome(username)
    else:
      self.redirect("/wiki/login")
