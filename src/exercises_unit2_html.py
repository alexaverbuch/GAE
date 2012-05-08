import webapp2
import cgi
import re

unit1form = """"Hello, Udacity!"""
unit2rot13form = """
<!DOCTYPE html>

<html>
  <head>
    <title>Unit 2 Rot 13</title>
  </head>

  <body>
    <h2>Enter some text to ROT13:</h2>
    <form method="post">
      <textarea name="text"
                style="height: 100px; width: 400px;">%(text)s</textarea>
      <br>
      <input type="submit">
    </form>
  </body>

</html>
"""
unit2signupform = """
<!DOCTYPE html>

<html>
  <head>
    <title>Sign Up</title>
    <style type="text/css">
      .label {text-align: right}
      .error {color: red}
    </style>

  </head>

  <body>
    <h2>Signup</h2>
    <form method="post">
      <table>
        <tr>
          <td class="label">
            Username
          </td>
          <td>
            <input type="text" name="username" value=%(username)s>
          </td>
          <td class="error">
            %(username_error)s
          </td>
        </tr>

        <tr>
          <td class="label">
            Password
          </td>
          <td>
            <input type="password" name="password" value="">
          </td>
          <td class="error"> 
            %(password_error)s
          </td>
        </tr>

        <tr>
          <td class="label">
            Verify Password
          </td>
          <td>
            <input type="password" name="verify" value="">
          </td>
          <td class="error">
            %(verify_error)s
          </td>
        </tr>

        <tr>
          <td class="label">
            Email (optional)
          </td>
          <td>
            <input type="text" name="email" value=%(email)s>
          </td>
          <td class="error">
            %(email_error)s
          </td>
        </tr>
      </table>

      <input type="submit">
    </form>
  </body>

</html>
"""
unit2welcomeform = """
<!DOCTYPE html>

<html>
  <head>
    <title>Unit 2 Signup</title>
  </head>

  <body>
    <h2>Welcome, %(username)s!</h2>
  </body>
</html>"""
      
def escape_html(s):
  return cgi.escape(s, quote=True)

class Home(webapp2.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'
    self.response.out.write("Home")      

class Unit1Handler(webapp2.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'
    self.response.out.write(unit1form)      

class Unit2Rot13Handler(webapp2.RequestHandler):
  def write_form(self, text=""):
    self.response.headers['Content-Type'] = 'text/html'
    self.response.out.write(unit2rot13form % {"text": text})
  def get(self):
    self.write_form()
  def post(self):
    text = self.request.get('text')
    text = text.encode("rot13")
    text = escape_html(text)
    self.write_form(text)

username_re = re.compile('^[a-zA-Z0-9_-]{3,20}$')
password_re = re.compile('^.{3,20}$')
email_re = re.compile('^[\S]+@[\S]+\.[\S]+$')

class BlogSignupHandler(webapp2.RequestHandler):
  def write_form(self, username="", username_error="",
                 password_error="", verify_error="",
                 email="", email_error=""):
    self.response.headers['Content-Type'] = 'text/html'
    self.response.out.write(unit2signupform % {"username": username,
                                               "username_error": username_error,
                                               "password_error": password_error,
                                               "verify_error": verify_error,
                                               "email": email,
                                               "email_error": email_error})
  def get(self):
    self.write_form()
  def post(self):
    user_username = self.request.get('username')
    user_password = self.request.get('password')
    user_verify = self.request.get('verify')
    user_email = self.request.get('email')
    username_error = ""
    password_error = ""
    verify_error = ""
    email_error = ""
    username_error = "" if username_re.match(user_username) else "That's not a valid username."
    password_error = "" if password_re.match(user_password) else "That wasn't a valid password."
    verify_error = "" if (user_password == user_verify or (not password_error == "")) else "Your passwords didn't match."
    email_error = "" if (user_email == "" or email_re.match(user_email)) else "That's not a valid email."
    if ((username_error == "") and (password_error == "") and (verify_error == "") and (email_error == "")):
      self.redirect("/unit2/welcome?username=%s" % user_username)
    else:
      self.write_form(user_username, username_error, password_error, verify_error, user_email, email_error)
      
class BlogWelcomeHandler(webapp2.RequestHandler):
  def write_form(self, username=""):
    self.response.headers['Content-Type'] = 'text/html'
    self.response.out.write(unit2welcomeform % {"username": username})
  def get(self):
    username = self.request.get("username")
    self.write_form(username)

app = webapp2.WSGIApplication([('/', Home),
                               ('/unit1', Unit1Handler),
                               ('/unit2/rot13', Unit2Rot13Handler),
                               ('/unit2/signup', BlogSignupHandler),
                               ('/unit2/welcome', BlogWelcomeHandler)],
                              debug=True)
