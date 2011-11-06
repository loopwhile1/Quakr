from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
import simplejson
from model.earthquake import *
import datetime
import time
from google.appengine.api import memcache
import logging
from tasks.fetchquakedata import FetchQuakeDataHandler
from math import *

def to_dict(model):
    """
    Convert a webapp model into a python dictionary
    """
    SIMPLE_TYPES = (int, long, float, bool, dict, basestring, list)
    output = {}
    for key, prop in model.properties().iteritems():
        value = getattr(model, key)
        if value is None or isinstance(value, SIMPLE_TYPES):
            output[key] = value
        elif isinstance(value, datetime.date):
            # Convert date/datetime to ms-since-epoch ("new Date()").
            # ms = time.mktime(value.utctimetuple()) * 1000
            # ms += getattr(value, 'microseconds', 0) / 1000
            # output[key] = int(ms)
            output[key] = str(value)
        elif isinstance(value, db.GeoPt):
            output[key] = {'lat': value.lat, 'lon': value.lon}
        elif isinstance(value, db.Model):
            output[key] = to_dict(value)
        else:
            raise ValueError('cannot encode ' + repr(prop))
    return output

class GetEarthQuakes(webapp.RequestHandler):
    def getLastDay(self, minMagnitude=2.5):
	
		# Refresh our data set fetching the daily quakes
        fetchquakes = FetchQuakeDataHandler()
        response = fetchquakes.fetchDailyQuakes()
        
        lastDayQuery = db.GqlQuery("SELECT * "
            "FROM EarthQuake "
            "WHERE ANCESTOR IS :1 "
            "AND date > :2 "
            "ORDER BY date DESC",
            EarthQuakeDataStoreHelper.earthquake_key(),
            datetime.datetime.utcnow() + datetime.timedelta(days=-7))
            
        quakeArray = [to_dict(quake) for quake in lastDayQuery if quake.magnitude >= minMagnitude]
        return quakeArray
    
    def getLastDayFromCache(self):
        data = memcache.get("lastDayJSON")
        if data is not None:
            return data
        else:
            data = self.getLastDay()
            response = simplejson.dumps(data) #, sort_keys=True, indent=4)
            memcache.add("lastDayJSON", response, 1800)  
            return response
    
    def get(self):
        earthquakes = self.getLastDayFromCache()
        stats = memcache.get_stats()
        logging.debug("<b>Cache Hits:%s</b><br>" % stats['hits'])
        logging.debug("<b>Cache Misses:%s</b><br><br>" %
                              stats['misses'])
        self.response.out.write(earthquakes)
        