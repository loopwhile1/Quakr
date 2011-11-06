#!/usr/bin/env python
#
# Copyright 2011 Sanjit Saluja
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
import urllib2
import simplejson
import csv
from model.earthquake import *
import datetime

class FetchQuakeDataHandler(webapp.RequestHandler):
    def fetch(self, jobDetails = {'jobName' : 'daily'}):
        """
        Fetch the daily earthquake CSV
        """
        csvUrl = '';
        if jobDetails['jobName'] == 'daily':
            csvUrl = 'http://earthquake.usgs.gov/earthquakes/catalogs/eqs1day-M1.txt'
        else:
            csvUrl = 'http://earthquake.usgs.gov/earthquakes/catalogs/eqs1hour-M1.txt'
        
        request = urllib2.Request(csvUrl)
        response = urllib2.urlopen(request)
        reader = csv.DictReader(response, fieldnames = ( "Src","Eqid","Version","Datetime", "Lat", "Lon", "Magnitude", "Depth", "NST", "Region" ), skipinitialspace=True)
        
        #reader = csv.DictReader(open('eqs7day-M2.5.txt', 'r'), fieldnames = ( "Src","Eqid","Version","Datetime", "Lat", "Lon", "Magnitude", "Depth", "NST", "Region" ), skipinitialspace=True)
        i = 0
        for row in reader:
            if i > 0:
                EarthQuakeDataStoreHelper.addEarthQuake(row)
            i=i+1
        
        jobDetails['csvUrl'] = csvUrl;
        jobDetails['status'] = 'OK';
        return simplejson.dumps(jobDetails, sort_keys=True, indent=4)
    
    def fetchDailyQuakes(self):
        return self.fetch({'jobName' : 'daily'})
        
    def fetchHourlyQuakes(self):
        return self.fetch({'jobName' : 'hourly'})
    
    def get(self):
        jobDetails = {}
        jobDetails['jobName'] = self.request.get('job') or 'daily'
        self.response.out.write(self.fetch(jobDetails))
        