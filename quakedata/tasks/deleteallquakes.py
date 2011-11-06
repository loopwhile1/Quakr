from google.appengine.ext import db
from google.appengine.ext import webapp
import time

class bulkdelete(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        try:
            while True:
                q = db.GqlQuery("SELECT __key__ FROM EarthQuake")
                assert q.count()
                db.delete(q.fetch(200))
                time.sleep(0.5)
        except Exception, e:
            self.response.out.write(repr(e)+'\n')
            pass