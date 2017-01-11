import syslog
import sys
import datetime
import time

# this script will take eventlog file (hard coded path)
# read the file in, and strip the date from the eventlog file
# and store the date in a variable, compare current date with last date
# then write to the file then close the file
# send log out based on delta date (current - last)


DEFAULT_MAX_DELTA_TIME = 600  # ten minutes
FACILITY = syslog.LOG_LOCAL7
PRIORITY = syslog.LOG_ALERT

raw_eventlog_rel_path = []

if len(sys.argv) > 1:
    for item in sys.argv[1:]:
        raw_eventlog_rel_path.append(item)
else:
    # find the path to eventlog
    raw_eventlog_rel_path.append("eventlogs/eventlogs-12-06-2016")

def push_log_to_syslog(max_delta_time, max_timescale_factor=1):

    # ================= Init our variables =================
    previous_log_timestamp = None
    current_log_timestamp = None

    # ======================================================

    # loop through the lines in eventlog_file
    for counter, line in enumerate(eventlog_file):

        # one way this could potentially be done is to split the line on %
        split_line = line.split("%")

        if len(split_line) > 1:
            # reassemble the log file in eventlog % format
            current_log = "%" + "%".join(split_line[1:])
            
            # swap old current into previous_log_timestamp
            previous_log_timestamp = current_log_timestamp
            
            # update current_log_timestamp
            current_log_timestamp = timestamp_convert(split_line[0].strip())
            
            # get delta_time
            delta_time = calculate_delta_time(previous_log_timestamp, 
                current_log_timestamp, max_timescale_factor, max_delta_time)

            print "Log %d of %d" % (counter+1, total_logs)
            print "current_log:", current_log
            print "delta_time: %d seconds"  % (delta_time)
            print "========================================="

            # now send the log
            send_log(delta_time, current_log)

    syslog.closelog()


# convert string to timestamp function
def timestamp_convert(string):
    try:
        this_year = str(datetime.datetime.now().year)
        timestamped_str = datetime.datetime.strptime(this_year + ' ' + 
            string, '%Y %b  %d %H:%M:%S')
        timestamped_in_seconds = time.mktime(timestamped_str.timetuple())
        return timestamped_in_seconds
    except ValueError:
        raise ValueError("Section does not contain date, or a well-formatted date.")


# calculate the time that should elapse before sending syslog
def calculate_delta_time(previous_log_timestamp, current_log_timestamp, 
    max_timescale_factor, max_delta_time):
    if previous_log_timestamp and current_log_timestamp:
        # find the time delta, convert string to workable time
        delta_time = max_timescale_factor * (current_log_timestamp - 
                                             previous_log_timestamp)

        # create a 10 minute cap if the delta between log messages
        # happens to be greater than 10 minutes/600 seconds
        if delta_time > max_delta_time:
            delta_time = max_delta_time
    else:
        # assume nothing came before this current log
        delta_time = 0
    return delta_time
    

def send_log(delta_time, current_log):
    # sleep a little before sending off the log
    time.sleep(delta_time)

    # then send to syslog
    syslog.syslog(PRIORITY | FACILITY, current_log)

        
if __name__ == '__main__':
    max_timescale_factor = raw_input("Optional, enter a timescale factor ")
    if max_timescale_factor:
        try:
            max_timescale_factor = float(max_timescale_factor)
            max_delta_time = max_timescale_factor * DEFAULT_MAX_DELTA_TIME
        except ValueError:
            print "No idea what you typed there, but it wasn't a number"
    else:
        max_delta_time = DEFAULT_MAX_DELTA_TIME
        max_timescale_factor = 1

    for eventlog_path in raw_eventlog_rel_path:
        # open eventlog file
        eventlog_file = open(eventlog_path)

        with open(eventlog_path) as f:
            total_logs = len(f.readlines())

        print "Some logs will be pushed out with a",
        print "%d second interval between them" % (max_delta_time)

        print "========================================"
        print "Starting the syslog push"
        print "          _.~._"
        print "        ,~'.~@~.`~."
        print "       / : _..._ : \\"
        print "      { :,'''\\`'.: }"
        print "       `C) 9 _ 9 (--.._,-'''-.__"
        print "        (  )(@)(  )             `."
        print "         `-.___.-'                \\"
        print "         ,' \ /    ,`             ;`-._,-."
        print "       ,'  ,'/   ,'           `---t.,-.   \_"
        print "     ,--.,','  ,'----.__\         _(   \----'"
        print "   '///,`,--.,'          `-.__.--'  `.  )"
        print "       '///,'                         `-`"
        print "========================================"

        push_log_to_syslog(max_delta_time, max_timescale_factor)
    
