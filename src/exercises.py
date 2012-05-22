import os
import urllib2
import logging
from xml.dom import minidom

import webapp2
import jinja2
from google.appengine.api import memcache
from google.appengine.ext import db

import sec_utils
from urllib2 import URLError

template_dir = os.path.join(os.path.dirname("templates/"))
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)

IP_URL = "http://api.hostip.info/?ip="
def get_coords(ip):
  ip = "4.2.2.2"
  ip = "23.24.209.141"
  url = IP_URL + ip
  content = None
  try:
    content = urllib2.urlopen(url).read()
  except URLError:
      return
  if content:
    content_dom = minidom.parseString(content)
    content_dom.getElementsByTagName("tag name")
    coord_elements = content_dom.getElementsByTagName("gml:coordinates")
    if coord_elements and coord_elements[0].childNodes[0].nodeValue:
        lon, lat = coord_elements[0].childNodes[0].nodeValue.split(",")
        return db.GeoPt(lat, lon)

GMAPS_URL = "http://maps.googleapis.com/maps/api/staticmap?size=380x263&sensor=false&"
def gmaps_img(points):
    markers = "&".join("markers=%s,%s" % (point.lat, point.lon) 
                       for point in points)
    return GMAPS_URL + markers

class Art(db.Model):
  title = db.StringProperty(required=True)
  art = db.TextProperty(required=True)
  created = db.DateTimeProperty(auto_now_add=True)
  coords = db.GeoPtProperty()
  
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

art_key = db.Key.from_path("ASCIIChan", "arts")

def top_arts(update=False):
  key = 'top'  
  
  arts = memcache.get(key)
  if (arts is None) or update:
    logging.error("DB QUERY")
#    arts = db.GqlQuery("SELECT * "
#                       "FROM Art "
#                       "WHERE ANCESTOR IS :1 "
#                       "ORDER BY created DESC "
#                       "LIMIT 10",
#                       art_key)
    arts = db.GqlQuery("SELECT * "
                       "FROM Art "
                       "ORDER BY created DESC "
                       "LIMIT 10")
    # prevent query from being run multiple times    
    arts = list(arts)
    memcache.set(key, arts)
  return arts

class Unit3ChanHandler(Handler):
  def render_chan(self, title="", art="", error=""):
    arts = top_arts()
        
    points = filter(None, (art.coords for art in arts))      
    
    img_url = None
    if points:
      img_url = gmaps_img(points)
    
    self.render("unit3chan.html", title=title, art=art,
                error=error, arts=arts, img_url=img_url)
  def get(self):
    # repr <- makes printing Python types HTML friendly
    # remote_addr <- requesting IP address
    # self.write(self.request.remote_addr)
    # self.write(repr(get_coords(self.request.remote_addr)))
    self.render_chan()
  def post(self):
    title = self.request.get("title")
    art = self.request.get("art")            

    if title and art:
      newArt = Art(parent=art_key, title=title, art=art)
      user_coods = get_coords(self.request.remote_addr)
      if user_coods:
        newArt.coords = user_coods
      newArt.put()
      top_arts(True)
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
      visits_val = sec_utils.extract_secure_val(visits_cookie_str)
      if visits_val:
        visits = int(visits_val)
    
    visits += 1
    new_visits_cookie_str = sec_utils.make_secure_val(str(visits))
    self.response.headers.add("Set-Cookie", "visits=%s" % new_visits_cookie_str)
        
    if visits > 20:
      self.write("You've been here %s times. WOOHOO!" % visits)
    else:
      self.write("You've been here %s times" % visits)
