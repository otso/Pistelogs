import math
from datetime import datetime
KM_MULTIPLIER=6373

def distance_on_unit_sphere(lat1, long1, lat2, long2):
    """ This code from http://www.johndcook.com/python_longitude_latitude.html,
    KM_MULTIPLIER constant from the same source"""

    # Convert latitude and longitude to 
    # spherical coordinates in radians.
    degrees_to_radians = math.pi/180.0
        
    # phi = 90 - latitude
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians
        
    # theta = longitude
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians
        
    # Compute spherical distance from spherical coordinates.
        
    # For two locations in spherical coordinates 
    # (1, theta, phi) and (1, theta, phi)
    # cosine( arc length ) = 
    #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length
    
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
           math.cos(phi1)*math.cos(phi2))
    arc = math.acos( cos )

    # Remember to multiply arc by the radius of the earth 
    # in your favorite set of units to get length.
    return arc

def distance_on_earth(lat1, long1, lat2, long2):
    return KM_MULTIPLIER * distance_on_unit_sphere(lat1, long1, lat2, long2)

def get_time_diff_readable(dt):
    diff = datetime.now() - dt
    if diff.days == 0:
        if diff.seconds <= 60:
            return " ride ONGOING"
        elif diff.seconds <= 3600:
            return str(int(diff.seconds/60)) + " minutes ago"
        else:
            return str(int(diff.seconds/3600)) + " hours ago"
    else:
        if diff.days > 30:
            return "around " + str(diff.days/30) + " month(s) ago"
        else:
            return str(diff.days) + " days ago"

# Helpers for user data fetching

def get_total_km(user):
    total_km = 0
    if user.run_set.count()>0:
        for run_entry in user.run_set:
            difference = distance_on_unit_sphere(run_entry.start_location_lat,
                                                run_entry.start_location_lon,
                                                run_entry.end_location_lat,
                                                run_entry.end_location_lon)
            total_km = total_km + (difference * KM_MULTIPLIER)
    return total_km

def get_total_jumps(user):
    total_jumps = 0
    if user.rawlog_set.count()>0:
        for log_entry in user.rawlog_set:
            total_jumps = total_jumps + log_entry.jumps
    return total_jumps

def get_total_time(user):
    total_time = 0
    if user.run_set.count()>0:
        for run_entry in user.run_set:
            difference = run_entry.last_time_pointer - run_entry.start_time
            total_time = total_time + difference.seconds
    return total_time / 60

# Helpers for individual runs

def get_total_run_length(run_entry):
    difference = distance_on_unit_sphere(run_entry.start_location_lat,
                                        run_entry.start_location_lon,
                                        run_entry.end_location_lat,
                                        run_entry.end_location_lon)
    total_km = difference * KM_MULTIPLIER
    return total_km
