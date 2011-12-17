from django.shortcuts import render_to_response
from google.appengine.ext import db
from google.appengine.ext.db import djangoforms
from django.http import HttpResponseRedirect
from django.http import HttpResponse
import logging

from pistelogs import models
import helpers
import LogParser

# handlers

def index(request):
    users = models.PisteUser.all()
    resorts = models.Resort.all().fetch(limit=5)
    if users.count()>0:
        return render_to_response('index.html',
                                 {'users': users, 'resorts': resorts})
    else:
        return render_to_response('index.html')

def instructions(request):
    return render_to_response('instructions.html')

def oob(request):
    return render_to_response('oob.html')

def resorts(request):
    all_resorts = models.Resort.all()
    resort_count = all_resorts.count()
    return render_to_response('resorts.html',
                              {"resorts" : all_resorts,
                               "resort_count": resort_count})

def resort(request, resort_id=None):
    if resort_id:
        resort = models.Resort.get_by_id(int(resort_id))
        if resort!=None:         
            return render_to_response('resort.html',
                          {"resort" : resort,})
        else:
            return render_to_response('error.html',
                                  {'error' : "No resort found"})  
    else:
        return render_to_response('error.html',
                                  {'error' : "No id given"})    

def apidocs(request):
    return render_to_response('apidocs.html')

def user_profile(request, user_name=None):
    if user_name:
        all_users = models.PisteUser.all()
        all_users.filter('user_id = ', user_name)
        user = all_users.get()
        if user == None:
            return render_to_response('error.html',
                                     {'error' : "User not found"})
        if user.rawlog_set.count()>0:
            polished = {}
            polished["name"] = user_name
            polished['total_runs']=user.run_set.count()
            polished['total_km']=str(round(helpers.get_total_km(user), 2))
            polished['total_jumps']=helpers.get_total_jumps(user)
            polished['total_time']=helpers.get_total_time(user)
            
            runs_polished = []
            for run_entry in user.run_set.order('-created'):
                runs_polished.append({"run_guid": run_entry.guid,
                                      "run_time": helpers.get_time_diff_readable(run_entry.last_time_pointer),
                                      "run_length": str(round(helpers.get_total_run_length(run_entry), 2))})
            
            return render_to_response('user_profile.html',
                                     {'user_name' : user_name,
                                      'polished': polished,
                                     'runs_polished': runs_polished})
    else:
        return render_to_response('error.html',
                                  {'error' : "No name given"})

def user_run(request, user_name=None, run_guid=None):
    if user_name:
        run_query_results = models.Run.gql("WHERE guid= :1", run_guid)
        if run_query_results.count()>0:         
            polished = []
            for run in run_query_results:
                # fetch the needed values for all the raw logs inside this run
                jumps = 0
                highest_point = 0.0
                speed = 0.0
                max_speed = 0.0
                for rawlog_entry in run.rawlog_set:
                    jumps += rawlog_entry.jumps
                    if highest_point < rawlog_entry.highest_altitude:
                        highest_point = rawlog_entry.highest_altitude
                    speed = rawlog_entry.avg_speed
                    if max_speed < rawlog_entry.max_speed:
                        max_speed = rawlog_entry.max_speed
                if run.rawlog_set.count() > 0:
                    speed = speed / run.rawlog_set.count()
                
                polished.append({"run_duration": run.last_time_pointer - run.start_time,
                                 "run_length": str(round(helpers.get_total_run_length(run), 2)),
                                 "run_jumps": jumps,
                                 "run_highest": str(round(highest_point, 2)),
                                 "run_avg_speed": str(round(speed, 2)),
                                 "run_max_speed": str(round(max_speed, 2)),
                                 "run_start_location_lat": run.start_location_lat,
                                 "run_start_location_lon": run.start_location_lon,
                                 "run_board": run.board,
                                 "run_stance": run.stance,
                                 "run_degree_front": run.degree_front,
                                 "run_degree_back": run.degree_back,
                                 "run_music": run.music_listened,
                                 "run_resort": run.resort_id,})
                                 
            return render_to_response('polished_run.html',
                                     {'user_name' : user_name,
                                      'polished': polished})
    else:
        return render_to_response('error.html',
                                  {'error' : "No name given"})

# API

def receive_log(request):
    if request.method == 'POST':
        try:
            user_name = request.POST['user_id']
            guid = request.POST['run_guid']
            guid = guid[1:len(guid)-1] # remove '{}' characters
            # parameter binding for user input to be safe
            user_exists = models.PisteUser.gql("WHERE user_id= :1", user_name)
            user_ref=None
            
            # TODO move the below to LogParser - return dict with all the information
            from datetime import datetime
            tree = LogParser.get_parse_tree(request.POST['log_data'])
            last_time_in_log = datetime.fromtimestamp(LogParser.get_last_time_entry(tree))
            first_time_in_log = datetime.fromtimestamp(LogParser.get_first_time_entry(tree))
            location = LogParser.get_location(tree)
            jumps = LogParser.get_jumps_count(tree)
            lowest_altitude = LogParser.get_lowest_speed(tree)
            highest_altitude = LogParser.get_highest_altitude(tree)
            avg_speed = LogParser.get_average_speed(tree)
            max_speed = LogParser.get_max_speed(tree)
            lowest_speed = LogParser.get_lowest_speed(tree)
            # TODO get the following dynamically from the client:
            board = "Burton Aftermath" # yes, my 2012 season board
            stance = "goofy"
            degree_front = 15
            degree_back = -15
            music_listened = "AC/DC"
            # fetch matching resort:
            resort = None
            results = models.Resort.query(location["lat"], location["lon"], 1, (2, 0))
            if len(results)>0:
                for res in results:
                    resort = res[1]
            
            first_time = False
            
            if not user_exists.count()>0:
                first_time = True
                new_user = models.PisteUser()
                new_user.user_id = request.POST['user_id']
                new_user.last_time_from_log = last_time_in_log
                new_user.put()
                user_ref=new_user
            else:
                for user in user_exists:
                    user_ref = user
                    user.last_time_from_log = last_time_in_log
                    user.put()
            
            raw_deposit = models.RawLog(user_id=user_ref)
            raw_deposit.guid = guid
            raw_deposit.log_data = request.POST['log_data']
            raw_deposit.first_time_from_log = first_time_in_log
            raw_deposit.last_time_from_log = last_time_in_log
            raw_deposit.jumps = jumps
            raw_deposit.lowest_altitude = lowest_altitude
            raw_deposit.highest_altitude = highest_altitude
            raw_deposit.avg_speed = avg_speed
            raw_deposit.max_speed = max_speed
            raw_deposit.lowest_speed = lowest_speed
            
        except:
            #TODO move to "global" to catch all app exceptions and tracebacks
            import sys, traceback
            exception_traceback = ''.join(traceback.format_exception(*sys.exc_info()))
            logging.error("START TRACEBACK----------")
            logging.error(exception_traceback)
            logging.error("END TRACEBACK----------")
        
        # deposit Run, start with first time user logging and create a new Run
        if first_time:
            new_run = models.Run(user_id=user_ref)
            new_run.start_time = first_time_in_log
            new_run.last_time_pointer = last_time_in_log
            new_run.start_location_lat = location["lat"]
            new_run.start_location_lon = location["lon"]
            new_run.end_location_lat = location["lat"]
            new_run.end_location_lon = location["lon"]
            new_run.guid = guid
            new_run.board = board
            new_run.stance = stance
            new_run.degree_front = degree_front
            new_run.degree_back = degree_back
            new_run.music_listened = music_listened
            new_run.resort_id = resort
            new_run.put()
            # deposit raw log
            raw_deposit.run_id = new_run
            raw_deposit.put()
            return HttpResponse('{"result": "1"}')
        
        # check 
        run_query_results = models.Run.gql("WHERE guid= :1 AND user_id= :2", guid, user_ref)
        # no results found, create a new Run
        if run_query_results.count() == 0:
            new_run = models.Run(user_id=user_ref)
            new_run.start_time = first_time_in_log
            new_run.last_time_pointer = last_time_in_log
            new_run.start_location_lat = location["lat"]
            new_run.start_location_lon = location["lon"]
            new_run.end_location_lat = location["lat"]
            new_run.end_location_lon = location["lon"]
            new_run.guid = guid
            new_run.board = board
            new_run.stance = stance
            new_run.degree_front = degree_front
            new_run.degree_back = degree_back
            new_run.music_listened = music_listened
            new_run.resort_id = resort
            new_run.put()
            # deposit raw log
            raw_deposit.run_id = new_run
            raw_deposit.put()
        else: # TODO perhaps check the weird results also? say minus...
            # just change the pointer to the last time entry
            for run in run_query_results:
                run.last_time_pointer = last_time_in_log
                run.end_location_lat = location["lat"]
                run.end_location_lon = location["lon"]
                run.put()
                # deposit raw log
                raw_deposit.run_id = run
                raw_deposit.put()

        return HttpResponse('{"result": "1"}')
    return HttpResponse('{"result": "0"}')

def recent_download(request, time=None):

    if request.method == 'GET' and request.GET.has_key('time'):
        
        logging.debug("FROM REQUEST: " + request.GET['time'])
    
        from django.utils import simplejson 
        runs = models.Run.all().order('-start_time').fetch(limit=1)
        res = {}
        for run in runs:
            if request.GET['time'] < run.start_time.isoformat():
                res = {'id': run.guid,
                       'time': run.start_time.isoformat()}
                return HttpResponse(simplejson.dumps(res), mimetype="text/plain")
            else:
                return HttpResponse('{}', mimetype="text/plain")  
    else:        
        return HttpResponse('{}', mimetype="text/plain")

def receive_resort(request):
    # TODO this interface needs to be CLOSED after the data import
    # appengine does provide other data upload capabilities but this was
    # convenient
    if request.method == 'POST':
        try:
            name = request.POST['name']
            area_name = request.POST['area_name']
            country = request.POST['country']
            url= request.POST['url']
            lat = float(request.POST['lat'])
            lon = float(request.POST['lon'])            
            new_resort = models.Resort.create(name=name, area_name=area_name,
                                           country=country, lat=lat, lon=lon,
                                           url=url)
            new_resort.put()
            return HttpResponse('{"result": "1"}')
        except:
            import sys, traceback
            exception_traceback = ''.join(traceback.format_exception(*sys.exc_info()))
            logging.error("START TRACEBACK----------")
            logging.error(exception_traceback)
            logging.error("END TRACEBACK----------")            
            
            return HttpResponse('{"result": "0"}')
    else:
        return HttpResponse('{"result": "0"}')

def query_resort(request):
    if request.method == 'POST':
        try:
            lat = float(request.POST['lat'])
            lon = float(request.POST['lon'])            
            results = models.Resort.query(lat, lon, 3, (2, 0))
            if len(results)>0:
                res = {}
                res["result"] = {}
                for resort in results:
                    res["result"][resort[1].name] = {"url": resort[1].url, "distance": resort[0]}
                return HttpResponse(str(res))
            else:
                return HttpResponse('{"result": "0"}')
        except:
            import sys, traceback
            exception_traceback = ''.join(traceback.format_exception(*sys.exc_info()))
            logging.error("START TRACEBACK----------")
            logging.error(exception_traceback)
            logging.error("END TRACEBACK----------")            
            
            return HttpResponse('{"result": "0"}')
    else:
        return HttpResponse('{"result": "0"}')

# TEST:

def test(request):
    users = models.PisteUser.all()
    if users.count()>0:
        return render_to_response('test.html',
                                 {'users': users})
    else:
        return render_to_response('test.html')

def test_polished_user_data(request, user_name=None):
    if user_name:
        all_users = models.PisteUser.all()
        all_users.filter('user_id = ', user_name)
        logs_user = all_users.get()
        if logs_user.rawlog_set.count()>0:
            polished = []
            for log_entry in logs_user.rawlog_set:
                tree=LogParser.get_parse_tree(log_entry.log_data)
                log_dict={"highest": LogParser.get_highest_altitude(tree),
                          "location": LogParser.get_location(tree),
                          "jumps": LogParser.get_jumps_count(tree),
                          "avg_speed": LogParser.get_average_speed(tree),
                          "start_time": LogParser.return_time(LogParser.get_first_time_entry(tree)),
                          "max_speed": LogParser.get_max_speed(tree)}
                polished.append(log_dict)
            return render_to_response('polished_user.html',
                                     {'polished_logs': polished})
    else:
        return HttpResponse("No name given") # TODO sensible error message

def test_polished_user_runs(request, user_name=None):
    if user_name:
        all_users = models.PisteUser.all()
        all_users.filter('user_id = ', user_name)
        logs_user = all_users.get()
        if logs_user.rawlog_set.count()>0:
            polished = []
            # iterate over the runs
            for log_entry in logs_user.run_set:
                polished.append({"xml": log_entry.to_xml()})
            return render_to_response('runs_user.html',
                                     {'runs': polished})
    else:
        return HttpResponse("No name given") # TODO sensible error message

def test_raw_user_data(request, user_name=None):
    if user_name:
        all_users = models.PisteUser.all()
        all_users.filter('user_id = ', user_name)
        logs_user = all_users.get()
        if logs_user.rawlog_set.count()>0:
            return render_to_response('user.html',
                                     {'raw_logs': logs_user.rawlog_set})
    else:
        return HttpResponse("No name given") # TODO sensible error message
