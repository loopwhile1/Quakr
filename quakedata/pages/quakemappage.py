from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
import os
from google.appengine.ext.webapp import template

class QuakeMapPageHandler(webapp.RequestHandler):
    def get(self):
        
        template_values = {}
        path = os.path.join(os.path.dirname(__file__), 'templates')
        path = os.path.join(path, 'QuakeMap.html')
        self.response.out.write(template.render(path, template_values))