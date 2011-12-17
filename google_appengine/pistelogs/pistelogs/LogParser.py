from xml.dom import minidom

ACC="acc_data"
MAG="mag_data"
GPS="gps_data"
JUMPS="air_time"

SPEED="ground_speed"
LONGITUDE="longitude"
LATITUDE="latitude"
ALTITUDE="altitude"

TSSTAMP="tstamp"

def add_root_element(text):
    """minidom fails to parse without root element"""
    return "<root>" + text + "</root>"

def get_parse_tree(text):
    return minidom.parseString(add_root_element(text))

def get_first_time_entry(parse_tree):
    """returns the first tick time"""
    ## Ugly hack due to http://code.google.com/p/googleappengine/issues/detail?id=4967#c0
    ## otherwise, this would work:
    #first_node = parse_tree.firstChild.firstChild
    #return float(first_node.attributes[TSSTAMP].value)
    tree = parse_tree.toxml()
    return float(tree[tree.find('tstamp="'):].split('"')[1])
    
def get_last_time_entry(parse_tree):
    """returns the last tick time"""
    last_node = parse_tree.lastChild.lastChild
    return float(last_node.attributes[TSSTAMP].value)

def ms_to_kmhour(ms):
    return (3600.0*ms/1000.0)

def get_average_speed(parse_tree):
    """get the speed average"""
    raw_log = parse_tree
    acc_entries = raw_log.getElementsByTagName(GPS)
    if len(acc_entries)==0:
        return -1
    speed_sum = 0
    for acc in acc_entries:
        speed_sum = speed_sum + float(acc.attributes[SPEED].value)
    return (speed_sum/len(acc_entries))

def get_max_speed(parse_tree):
    """get the max speed"""
    raw_log = parse_tree
    acc_entries = raw_log.getElementsByTagName(GPS)
    if len(acc_entries)==0:
        return 0.0
    max_speed = 0.0
    for acc in acc_entries:
        if max_speed < float(acc.attributes[SPEED].value):
            max_speed = float(acc.attributes[SPEED].value)
    return max_speed

def get_lowest_speed(parse_tree):
    """get the lowest speed"""
    raw_log = parse_tree
    acc_entries = raw_log.getElementsByTagName(GPS)
    if len(acc_entries)==0:
        return -1
    lowest_speed = 0
    first = True
    for acc in acc_entries:
        if first:
            lowest_speed = float(acc.attributes[SPEED].value)
            first = False
        if lowest_speed > float(acc.attributes[SPEED].value):
            lowest_speed = float(acc.attributes[SPEED].value)
        
    return lowest_speed

def get_jumps_count(parse_tree):
    """get the number of jumps"""
    raw_log = parse_tree
    acc_entries = raw_log.getElementsByTagName(JUMPS)
    return len(acc_entries)

def get_location(parse_tree):
    """get the first location inside the sample"""
    raw_log = parse_tree
    acc_entries = raw_log.getElementsByTagName(GPS)
    if len(acc_entries)>0:
        return {"lat": float(acc_entries[0].attributes[LATITUDE].value),
                "lon": float(acc_entries[0].attributes[LONGITUDE].value)}
    return {"lat": 0, "lon": 0} # TODO sensible return

def get_altitude(parse_tree):
    """get the first altitude inside the sample"""
    raw_log = parse_tree
    acc_entries = raw_log.getElementsByTagName(GPS)
    if len(acc_entries)>0:
        return float(acc_entries[0].attributes[ALTITUDE].value)
    return 0 # TODO sensible return

def get_lowest_altitude(parse_tree):
    """get the lowest altitude inside the sample"""
    raw_log = parse_tree
    acc_entries = raw_log.getElementsByTagName(GPS)
    lowest_altitude = 0
    first = True
    for acc in acc_entries:
        if first:
            lowest_altitude = float(acc.attributes[ALTITUDE].value)
            first = False
        if lowest_altitude > float(acc.attributes[ALTITUDE].value):
            lowest_altitude = float(acc.attributes[ALTITUDE].value)
    return lowest_altitude # TODO sensible default return

def get_highest_altitude(parse_tree):
    """get the highest altitude inside the sample"""
    raw_log = parse_tree
    acc_entries = raw_log.getElementsByTagName(GPS)
    highest_altitude = 0
    first = True
    for acc in acc_entries:
        if highest_altitude < float(acc.attributes[ALTITUDE].value):
            highest_altitude = float(acc.attributes[ALTITUDE].value)
        if first:
            highest_altitude = float(acc.attributes[ALTITUDE].value)
            first = False
    return highest_altitude # TODO sensible default return

# TEST

def return_time(time_value):
    import time
    return time.ctime(time_value)

def test_print_acc(parse_tree):
    """prints all the acc nodes and their values"""
    raw_log = parse_tree
    acc_entries = raw_log.getElementsByTagName(ACC)
    for acc in acc_entries:
        attributes = acc.attributes.keys()
        for attribute in attributes:
            a = acc.attributes[attribute]
            print "Name: " + a.name + " Value: " + a.value

def main():
    test_entry = """<air_time tstamp="1303979914.839" in_air="0.467" landed="false"/> <acc_data tstamp="1303979914.889" x="0" y="9.8" z="0" r="9.8"/>"""
    tree = get_parse_tree(test_entry)
    #test_print_acc(tree)
    first_time = get_first_time_entry(tree)
    last_time = get_last_time_entry(tree)
    
    print "First time: " + return_time(first_time)
    print "Last time: " + return_time(last_time)

    print "Average speed: %f" % ms_to_kmhour(get_average_speed(tree))

    print "Max speed: %d" % get_max_speed(tree)

    print "Lowest speed: %d" % get_lowest_speed(tree)

    print "Jumps: %d" % get_jumps_count(tree)

    print "Location: " + str(get_location(tree))

    print "First altitude: " + str(get_altitude(tree))

    print "Lowest altitude: " + str(get_lowest_altitude(tree))

    print "Highest altitude: " + str(get_highest_altitude(tree))

    test_real = """<feet_sum tstamp="1299861847.560" sum="3056"/>    <foot_data tstamp="1299861847.594" side="R" toes="729" heel="762"/>    <feet_sum tstamp="1299861847.594" sum="3056"/>    <foot_data tstamp="1299861847.608" side="L" toes="734" heel="831"/>    <acc_data tstamp="1299861847.611" x="-0.308976" y="7.56992" z="3.55323" r="8.36807"/>"""
    tree = get_parse_tree(test_real)
    print "Average speed: %f" % ms_to_kmhour(get_average_speed(tree))
    print "First time: " + str(get_first_time_entry(tree))

if __name__ == '__main__':
    main()
