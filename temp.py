import webapp2
import cgi

unit1form = """"Hello, Udacity!"""
unit2form_rot13 = """
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
unit2form_signup = """

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
            <input type="text" name="username" value="">
          </td>
          <td class="error">
            
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
            
          </td>
        </tr>

        <tr>
          <td class="label">
            Email (optional)
          </td>
          <td>
            <input type="text" name="email" value="">
          </td>
          <td class="error">
            
          </td>
        </tr>
      </table>

      <input type="submit">
    </form>
  </body>

</html>
"""

testform = """
<form method="post">
	What is the date today?
	<br>

	<label>
		Year
		<input type="text" name="year" value=%(year)s>
	</label>
	
	<label>
		Month
		<input type="text" name="month" value=%(month)s>
	</label>
	
	<label>
		Day
		<input type="text" name="day" value=%(day)s>
	</label>
	<div style="color: red">%(error)s</div>
	
	<br>
	<br>
	
	<input type="submit">
</form>
"""

months = ['January',
          'February',
          'March',
          'April',
          'May',
          'June',
          'July',
          'August',
          'September',
          'October',
          'November',
          'December']
          
month_abbvs = dict((m[:3].lower(), m) for m in months)

#string1 = "My name is %(name)s, my nickname is %(nickname)s" % {"nickname":nickname, "name":name}
#string2 = "My name is %s, my nickname is %s" % ("name", "nickname")

# valid_year('0') => None    
# valid_year('-11') => None
# valid_year('1950') => 1950
# valid_year('2000') => 2000
def valid_year(year):
	if year and year.isdigit():
		year = int(year)
		if year>1900 and year<=2020:
			return year

# valid_month("january") => "January"    
# valid_month("January") => "January"
# valid_month("foo") => None
# valid_month("") => None
def valid_month(month):
	if month:
		short_month = month[:3].lower()
		return month_abbvs.get(short_month)	
		
# valid_day('0') => None    
# valid_day('1') => 1
# valid_day('15') => 15
# valid_day('500') => None
def valid_day(day):
	if day and day.isdigit():
		day = int(day)
		if day>0 and day<=31:
			return day
			
# replaces:
# > with &gt;
# < with &lt;
# " with &quot;
# & with &amp;
# and returns the escaped string
def escape_html(s):
	return cgi.escape(s, quote=True)

class MainPage(webapp2.RequestHandler):
	def write_form(self, error="", year="", month="", day=""):
		#self.response.headers['Content-Type'] = 'text/plain'		
		self.response.out.write(form % {"error": error,
						"year": escape_html(year),
						"month": escape_html(month),
						"day": escape_html(day)})
	def get(self):		
		self.write_form()
	def post(self):
		user_year = self.request.get('year')
		user_month = self.request.get('month')
		user_day = self.request.get('day')
		
		year = valid_year(self.request.get('year'))
		month = valid_month(self.request.get('month'))
		day = valid_day(self.request.get('day'))
		
		if not (year and month and day):
			self.write_form(error="bad input",
											year=user_year,
											month=user_month,
											day=user_day)
		else:
			self.redirect("/thanks")
			
class ThanksHandler(webapp2.RequestHandler):
	def get(self):		
			self.response.out.write("Thanks!")			
			
#class TestHandler(webapp2.RequestHandler):
	#def get(self):
		##q = self.request.get("q")
		##self.response.out.write(q)
		#self.response.headers['Content-Type'] = 'text/plain'		
		#self.response.out.write(self.request)

class Home(webapp2.RequestHandler):
	def get(self):		
		self.response.headers['Content-Type'] = 'text/plain'
		self.response.out.write("Home")			

class Unit1Handler(webapp2.RequestHandler):
	def get(self):		
		self.response.headers['Content-Type'] = 'text/plain'
		self.response.out.write(unit1form)			

class Unit2Handler(webapp2.RequestHandler):
	def write_form(self, text=""):
		self.response.headers['Content-Type'] = 'text/html'
		self.response.out.write(unit2form % {"text": text})
	def get(self):		
		self.write_form()
	def post(self):
		text = self.request.get('text')
		text = text.encode("rot13")
		text = escape_html(text)		
		self.write_form(text)

app = webapp2.WSGIApplication([('/', Home),
															 ('/unit1', Unit1Handler),
															 ('/unit2', Unit2Handler)],
                              debug=True)
