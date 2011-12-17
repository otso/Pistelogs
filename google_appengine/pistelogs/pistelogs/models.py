from appengine_django.models import BaseModel
from google.appengine.ext import db

#
# Resort information and location
#
# The following code is copied from the Mutiny example at:
#
# http://code.google.com/p/mutiny/
#

import geobox
import logging
from helpers import distance_on_earth

#resolution, slice, http://code.google.com/p/mutiny/source/browse/trunk/models.py
GEOBOX_CONFIGS = (
  (4, 5, True),
  (3, 2, True),
  (3, 8, False),
  (3, 16, False),
  (2, 5, False),
)

class Resort(db.Model):
    name = db.StringProperty()
    url = db.StringProperty()
    area_name = db.StringProperty() #continent
    country = db.StringProperty()
    lat = db.FloatProperty()
    lon = db.FloatProperty()
    location = db.GeoPtProperty()
    geoboxes = db.StringListProperty()
    @classmethod
    def create(cls, **kwargs):
        lat = kwargs['lat']
        lon = kwargs['lon']
        location = db.GeoPt(lat, lon)
        name = kwargs['name']
        url = kwargs['url']
        area_name = kwargs['area_name']
        country = kwargs['country']
        all_boxes = []
        for (resolution, slice, use_set) in GEOBOX_CONFIGS:
          if use_set:
            all_boxes.extend(geobox.compute_set(lat, lon, resolution, slice))
          else:
            all_boxes.append(geobox.compute(lat, lon, resolution, slice))
        new_resort = Resort(name=name, location=location, lat=lat,
                            lon=lon, area_name=area_name, country=country,
                            url=url, geoboxes=all_boxes)
        return new_resort
    @classmethod
    def query(cls, lat, lon, max_results, min_params):
        found_resorts = {}
        
        # Do concentric queries until the max number of results is reached.
        # Use only the first three geoboxes for search to reduce query overhead.
        for params in GEOBOX_CONFIGS[:3]:
          if len(found_resorts) >= max_results:
            break
          if params < min_params:
            break
    
          resolution, slice, unused = params
          box = geobox.compute(lat, lon, resolution, slice)
          logging.debug("Searching for box=%s at resolution=%s, slice=%s",
                        box, resolution, slice)
          query = cls.all()
          query.filter("geoboxes =", box)
          results = query.fetch(50)
          logging.debug("Found %d results", len(results))
          
          # De-dupe results.
          for result in results:
            if result.name not in found_resorts:
              found_resorts[result.name] = result
  
        # Now compute distances and sort by distance.
        resorts_by_distance = []
        for resort in found_resorts.itervalues():
          distance = distance_on_earth(lat, lon, resort.location.lat, resort.location.lon)
          resorts_by_distance.append((distance, resort))
        resorts_by_distance.sort()
    
        return resorts_by_distance[:max_results]

# User and logs 

class PisteUser(db.Model):
    user_id = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    last_time_from_log = db.DateTimeProperty()
    #last_time_modified = db.DateTimeProperty(auto_now=True)

class Run(db.Model):
    # TODO guid should be mapped to human readable format - URLs look bad currently
    guid = db.StringProperty()
    user_id = db.ReferenceProperty(PisteUser)
    resort_id = db.ReferenceProperty(Resort)
    created = db.DateTimeProperty(auto_now_add=True)
    start_time = db.DateTimeProperty()
    # the time "pointer" to the last RawLog added to this Run
    last_time_pointer = db.DateTimeProperty() 
    end_time = db.DateTimeProperty()
    start_location_lat = db.FloatProperty()
    start_location_lon = db.FloatProperty()
    end_location_lat =  db.FloatProperty()
    end_location_lon =  db.FloatProperty()
    board = db.StringProperty()
    stance = db.StringProperty()
    degree_front = db.IntegerProperty(default=0)
    degree_back = db.IntegerProperty(default=0)
    music_listened = db.StringProperty()

class RawLog(db.Model):
    guid = db.StringProperty()
    log_data = db.TextProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    user_id = db.ReferenceProperty(PisteUser)
    run_id = db.ReferenceProperty(Run) #TODO is this more efficient
    first_time_from_log = db.DateTimeProperty()
    last_time_from_log = db.DateTimeProperty()
    jumps = db.IntegerProperty(default=0)
    lowest_altitude = db.FloatProperty()
    highest_altitude = db.FloatProperty()
    avg_speed = db.FloatProperty()
    max_speed = db.FloatProperty()
    lowest_speed = db.FloatProperty()
