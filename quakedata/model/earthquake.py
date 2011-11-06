from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
import datetime

class EarthQuake(db.Model):
  # ( "Src","Eqid","Version","Datetime", "Lat", "Lon", "Magnitude", "Depth", "NST", "Region" )
  date = db.DateTimeProperty()
  geoPoint = db.GeoPtProperty()
  magnitude = db.FloatProperty()
  depth = db.FloatProperty()
  region = db.StringProperty()

class EarthQuakeDataStoreHelper(object):
    @staticmethod
    def earthquake_key(earthquake_name=None):
        """Constructs a datastore key for a EarthQuake entity with earthquake_name."""
        return db.Key.from_path('EarthQuake', earthquake_name or 'default_earthquakes')
  
    @staticmethod
    def addEarthQuake(row):
        """Parse the CSV row and create an Earth quake data store object"""
        earthquake = EarthQuake(parent=EarthQuakeDataStoreHelper.earthquake_key(), key_name=row['Eqid'])
        earthquake.geoPoint = db.GeoPt(float(row['Lat']), float(row['Lon']))
        earthquake.magnitude = float(row['Magnitude'])
        earthquake.depth = float(row['Depth'])
        earthquake.region = row['Region']
        # Saturday, November  5, 2011 21:52:18 UTC
        earthquake.date = datetime.datetime.strptime(row['Datetime'], '%A, %B %d, %Y %H:%M:%S %Z')
        earthquake.put()
        
    